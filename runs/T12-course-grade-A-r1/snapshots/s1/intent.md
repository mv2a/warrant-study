---
owner: course coordinator, first-year programming
---

# Course grade

At the end of term we turn each student's marks into a course percentage and a letter
grade. One bad quiz should not sink anyone, late homework should cost something but not
everything at once, and a student sitting just under a boundary should be treated the same
way every time. Every grade must follow these rules exactly, so any student can recompute
their own.

## Goals

- G1: The course percentage is a weighted sum of four components, each on a 0 to 100
  scale: 15% quiz average, 25% homework average, 25% midterm exam, 35% final exam.
- G2: When a student has two or more quiz scores, the single lowest one is dropped before
  the quizzes are averaged. Only one score is dropped, even when several tie for lowest.
  A student with a single quiz score keeps it. The quiz average is the plain mean of the
  scores that remain.
- G3: Late homework loses 10% of its own score for each day late, from 1 to 4 days late:
  2 days late keeps 80% of the score, so 85 becomes 68. Homework 5 or more days late
  scores 0, and homework that is not late keeps its full score. The homework average is
  the plain mean of every homework score after its penalty; no homework is dropped.
- G4: The letter grade is decided by the rounded course percentage: A for 90.0 or more,
  B+ for 86.0 to 89.9, B for 80.0 to 85.9, C+ for 76.0 to 79.9, C for 70.0 to 75.9,
  D for 60.0 to 69.9, and F below 60.0.

## Constraints

- C1: The course percentage is computed exactly, without rounding any intermediate value
  (quiz scores, homework scores after penalty, averages or weighted parts), and is then
  rounded once to one decimal place, with an exact half rounded up: 82.25 becomes 82.3
  and 89.95 becomes 90.0.
- C2: Invalid requests are refused, never graded. That includes text that is not JSON,
  anything other than a JSON object, a missing field, a quiz or homework list that is
  empty or not a list, a quiz score, homework score, midterm or final that is not a JSON
  integer from 0 to 100 (such as -1, 101, 87.5, 90.0, "90" or true), a homework entry
  that is not an object or lacks score or days_late, and a days_late that is not a JSON
  integer of 0 or more (such as -1, 1.5, "2" or true).
- C3: Grading runs as a command named `grade` that reads one JSON object on standard
  input with the fields `quizzes` (a list of scores), `homework` (a list of objects, each
  with `score` and `days_late`), `midterm` (a score) and `final` (a score); other fields,
  in the request or in a homework object, are ignored. On success it exits with status 0
  and writes one JSON object on standard output with exactly two fields: `percent`, a
  JSON number holding the rounded course percentage (such as 82.3 or 90.0), and `letter`,
  one of the strings "A", "B+", "B", "C+", "C", "D" or "F". A refused request exits with
  status 2 and writes nothing on standard output.

## Scenarios

- S1: Quizzes 70, 85, 90 and 40; homework 90 on time, 80 two days late and 100 on time;
  midterm 78; final 84. The 40 is dropped and the 80 counts as 64, so the student gets
  percent 82.3 and letter B.
- S2: Quizzes 85 and 62; homework 88 on time; midterm 92; final 92. The course
  percentage is exactly 89.95, which rounds to 90.0, so the student gets percent 90.0
  and letter A.
- S3: A single quiz of 64; homework 100 five days late, 90 three days late and 75 on
  time; midterm 71; final 69. The homework counts as 0, 63 and 75, so the student gets
  percent 63.0 and letter D.

## Out of scope

- Extra credit, curving, incomplete grades, excused absences, and letter grades other
  than the seven listed.
