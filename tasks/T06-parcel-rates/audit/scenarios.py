"""X10-X13 (S1-S4): each example parcel in the intent gets exactly the answer the intent gives:
the four values for S1 to S3, and a refusal (status 2, no price) for S4. Field types and what a
refusal writes are C1's business.
Usage: python3 scenarios.py S1|S2|S3|S4"""

import json
import sys

from _audit import check, refused, values

SCENARIOS = {
    "S1": ('{"zone": 1, "weight_g": 1500, "length_cm": 30, "width_cm": 20, "height_cm": 10}',
           {"billable_g": 1500, "base_cents": 690, "surcharge_cents": 0, "total_cents": 690}),
    "S2": ('{"zone": 3, "weight_g": 800, "length_cm": 50, "width_cm": 40, "height_cm": 30}',
           {"billable_g": 12000, "base_cents": 2190, "surcharge_cents": 0, "total_cents": 2190}),
    "S3": ('{"zone": 4, "weight_g": 3500, "length_cm": 20, "width_cm": 110, "height_cm": 15}',
           {"billable_g": 6600, "base_cents": 2520, "surcharge_cents": 1500, "total_cents": 4020}),
    "S4": ('{"zone": 1, "weight_g": 3000, "length_cm": 20, "width_cm": 10, "height_cm": 155}',
           None),
}

name = sys.argv[1]
text, want = SCENARIOS[name]
# None of the scenario parcels sits on a carrying limit, so values() never excuses a refusal here.
judge = refused if want is None else values(json.loads(text), want)
check([(name, text, judge)], f"{name} ok")
