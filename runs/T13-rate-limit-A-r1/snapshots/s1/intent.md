---
owner: api platform team
---

# Rate-limit replay

Before we switch on rate limiting at our API gateway, we want to know what it would have
done to real traffic. We replay a recorded log of requests through a token-bucket limiter
with a burst size and a refill rate, one bucket per client, and report which requests the
limiter would have accepted and which it would have rejected.

## Goals

- G1: Every client has its own bucket. Clients are told apart by their exact name, so
  "alice", "Alice" and "alice " are three different clients, and one client's requests
  never change the decisions made for another client.
- G2: A bucket holds at most `burst` tokens, and it is full before its client's first
  request, whenever that request comes. So a client can make `burst` requests at the same
  instant and all of them are accepted, and however long a client stays quiet, it never
  gets more than `burst` requests accepted at one instant. Tokens that would overflow a
  full bucket are lost.
- G3: Tokens flow back into a bucket continuously at `rate` tokens per second. If a client
  was left with k tokens right after its previous request at time p (in milliseconds), then
  at time t it holds the smaller of `burst` and k + rate × (t − p) / 1000. Progress toward
  the next token is kept from one request to the next; it is never thrown away because a
  request arrived before the token was complete.
- G4: A request is accepted when its client's bucket holds at least one whole token at that
  moment, and accepting it takes exactly one token out. A request that finds less than one
  token is rejected and takes nothing, so a client that keeps retrying gets its next token
  just as soon as a client that waits.

## Constraints

- C1: The limiter is a command named `limit`. It reads one JSON object on standard input
  with `burst` (an integer, at least 1), `rate` (an integer, at least 1: tokens added per
  second) and `requests` (a list, possibly empty, of objects with `client`, a non-empty
  string, and `at`, an integer number of milliseconds, 0 or more). Other fields are
  ignored. On success it exits with status 0 and writes one JSON object to standard output
  with exactly two fields: `decisions`, a list holding "accept" or "reject" for each
  request, in the order the requests were given; and `clients`, an object with one entry
  for each client that appears in the log and no others, where each entry is an object
  `{"accepted": A, "rejected": R}` counting that client's decisions. A refused request
  exits with status 2 and writes nothing to standard output (a message on standard error
  is fine).
- C2: Tokens are counted exactly, never rounded, however many requests come in between. A
  token that falls due at the very millisecond of a request is available to that request,
  and one that falls due even a fraction of a millisecond later is not. For example, at a
  rate of 3 a token takes 333⅓ ms, so a client whose bucket is empty at 0 ms is rejected
  at 333 ms and accepted at 334 ms; and at a rate of 10, a client that empties its bucket
  at 0 ms and then asks every 10 ms is rejected nine times and accepted at exactly 100 ms.
- C3: The log is in time order: each request's `at` is no earlier than the `at` of the
  request listed just before it, whichever clients made them. Requests with the same `at`
  are handled in the order they are listed. A log that goes back in time anywhere is
  refused.
- C4: Invalid requests are refused, never replayed. That includes input that isn't a JSON
  object; a `burst` or `rate` that is missing, not an integer, or less than 1; `requests`
  missing or not a list; an entry in `requests` that isn't an object; a `client` that is
  missing, not a string, or empty; and an `at` that is missing, not an integer, or
  negative. true and false are not integers, and neither is a number written with a
  decimal point or an exponent, such as 2.0, 2.5 or 1e3.

## Scenarios

- S1: With `burst` 3 and `rate` 2, client "alice" asks at 0, 0, 0, 0, 499, 500, 1000 and
  1000 ms. The decisions are accept, accept, accept, reject, reject, accept, accept,
  reject, and `clients` is `{"alice": {"accepted": 5, "rejected": 3}}`: the burst of three
  goes through at once, the next token is due at 500 ms and the one after at 1000 ms.
- S2: With `burst` 1 and `rate` 1, the log is "a" at 0, "b" at 0, "a" at 0, "b" at 600,
  "a" at 1000 and "b" at 1000 ms. The decisions are accept, accept, reject, reject, accept,
  accept, and `clients` is `{"a": {"accepted": 2, "rejected": 1}, "b": {"accepted": 2,
  "rejected": 1}}`.
- S3: With `burst` 2 and `rate` 1, client "carol" asks three times at 0 ms and three times
  at 60000 ms. The decisions are accept, accept, reject, accept, accept, reject, and
  `clients` is `{"carol": {"accepted": 4, "rejected": 2}}`: a minute of quiet refills the
  bucket to 2 tokens, not 60.

## Out of scope

- Sliding windows, fixed windows and other limiting schemes; requests that cost more than
  one token; limits shared across several gateways; reading the clock or live traffic.
