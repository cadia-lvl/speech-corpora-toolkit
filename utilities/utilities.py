#!/usr/bin/env python3

"""
    This module will contains small helper functions that can be useful for
    other modules.

    seconds_to_hours_mins(seconds) -> (hours, mins):
    Takes in seconds and outputs whole hours and whole minutes in a tuple

    EXTEND AS FUNCTIONALITY IS EXTENDED
"""

___author___ = "Staffan Hedström"
___license___ = "Apache 2.0"
___copyright___ = "2022 Staffan Hedström Reykjavík University"


def seconds_to_hours_mins(seconds):
    mins = int((seconds / 60) % 60)
    hours = int(seconds / 60 / 60)
    return hours, mins
