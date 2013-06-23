#!/usr/bin/env python

import json
import datetime
import dateutil.parser
import time


def parse_lift(raw):
    lift_name, raw_sets = raw.split("@")

    lift_name = lift_name.strip()

    sets = []

    for raw_set in raw_sets.split("+"):
        weight, reps = raw_set.split("x")
        sets.append({
            "weight": float(weight.strip()),
            "reps": int(reps.strip()),
        })

    return {
        "name": lift_name,
        "sets": sets
    }


def parse_workout(line):
    line = line.strip()
    raw_date, _, right = line.rpartition("|")

    if not raw_date:
        date = datetime.date.today()
    else:
        date = dateutil.parser.parse(raw_date)

    raw_lifts, _, comment = right.partition("#")

    comment = comment.strip()

    lifts = []

    for raw_lift in raw_lifts.split(","):
        lifts.append(parse_lift(raw_lift))

    return {
        "date": date.strftime("%Y-%m-%d"),
        "comment": comment,
        "lifts": lifts
    }


def dump_lift(lift):
    return "{}@{}".format(lift["name"],
                          "+".join("{}x{}".format(set["weight"], set["reps"]) for set in lift["sets"]))


def dump_workout(workout):
    return "{}|{}".format(workout["date"],
                          ",".join(dump_lift(lift) for lift in workout["lifts"]))


if __name__ == "__main__":
    import readline
    import os
    import sys

    try:
        input = raw_input
    except NameError:
        pass

    db_loc = sys.argv[1]
    print("Example: 2013-06-19|Squat@137.5x3+137.5x4,Overhead Press@42.5x5+42.5x5+42.5x4,Deadlift@120x1 # comment")
    workout = parse_workout(input("> "))
    dump = json.dumps(workout, indent=2, sort_keys=True)
    print(dump)

    fn = os.path.join(os.path.expanduser(db_loc), workout["date"] + ".json")
    if os.path.exists(fn):
        raise RuntimeError("not overwriting existing record at " + fn)

    with open(fn, "w") as f:
        f.write(dump)

    print("Okay, committed to: " + f.name)
