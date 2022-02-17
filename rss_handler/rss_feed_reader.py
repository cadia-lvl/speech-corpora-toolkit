#!/usr/bin/env python3

"""
    This module will handle all functions needed to be executed via rss feeds.
    Starting with returning valid audio urls for each episode.

    EXTEND AS FUNCTIONALITY IS EXTENDED

    This is for now a proof of concept,
    WILL BE REWRITTEN TO A CLASS
"""

___author___ = "Staffan Hedström"
___license___ = "Apache 2.0"
___copyright___ = "2022 Staffan Hedström Reykjavík University"


from bs4 import BeautifulSoup
import requests
import ffmpeg

from source_handler.handler import SourceHandler
from utilities.utilities import seconds_to_hours_mins
from tqdm import tqdm


def get_sample_rate(url: str):
    meta = ffmpeg.probe(url)
    duration = eval(meta["format"]["duration"])
    size = eval(meta["format"]["size"])
    return int(round(size / duration))


def get_duration_seconds(url: str, sample_rate: int):
    return get_length_from_url(url) / sample_rate


def get_length_from_url(url: str):
    r = requests.head(url)
    cLength = r.headers["content-length"]
    return int(cLength)


def get_series_length(url: str):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    audio_urls = []
    total_length_seconds = 0

    for item in soup.find_all("item"):
        audio_url = item.guid.string
        audio_urls.append(audio_url)

    sample_rate = get_sample_rate(audio_urls[0])

    for u in tqdm(audio_urls, desc=url):
        duration = get_duration_seconds(u, sample_rate)
        total_length_seconds += int(duration)

    return total_length_seconds


def main():
    test_data = "test_data.json"
    source_handler = SourceHandler(test_data)

    rss_urls = source_handler.get_rss_urls()

    length = 0
    for url in rss_urls:
        audioLength = get_series_length(url)
        hours, mins = seconds_to_hours_mins(audioLength)
        print(f"Length: {hours} hours and {mins} minutes")
        length += audioLength

    hours, mins = seconds_to_hours_mins(length)
    print(f"Total length: {hours} hours and {mins} minutes")


if __name__ == "__main__":
    main()
