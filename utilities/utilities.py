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

import unidecode
import ffmpeg


def seconds_to_hours_mins(seconds):
    mins = int((seconds / 60) % 60)
    hours = int(seconds / 60 / 60)
    return hours, mins


def standardize_string(string):
    return unidecode.unidecode(string.lower().replace(" ", "_"))


def copy_and_convert_to_wav(input, output):
    """
    Uses ffmpeg to convert the intput file to a .wav
    and places a copy of it at output
    """
    file_format = output.split(".")[-1]
    if file_format != "wav":
        output = output.split(".")
        output[-1] = "wav"
        output = ".".join(output)
    stream = ffmpeg.input(input)
    stream = ffmpeg.output(
        stream,
        filename=output,
        f="wav",
        acodec="pcm_s16le",
        ac=1,
        ar="16k",
        loglevel="error",
    )
    ffmpeg.run(stream)
