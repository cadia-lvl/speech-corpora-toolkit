#!/usr/bin/env python3

"""
    This module will handle all functions needed to be executed via rss feeds.
    Starting with returning valid audio urls for each episode.

    Example of usage
    rss_feeds = {
        "feed1": url1,
        "feed2": url2,
    }
    rss_handler = RSSFeedsHandler(rss_feeds)
    rss_handler.get_total_lengths(print_feed_lengths = True)

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
from pathlib import Path
from datetime import datetime


class RSSFeedsHandler:
    def __init__(self, feeds: dict) -> None:
        self.feeds = feeds

    def get_total_length(self, print_feed_lengths=False) -> int:

        length = 0
        for key, item in self.feeds.items():
            feed_length = self.__get_feed_length(item)
            hours, mins = seconds_to_hours_mins(feed_length)

            if print_feed_lengths:
                print(f"{key}: {hours} hours and {mins} minutes")

            length += feed_length

        if print_feed_lengths:
            total_hours, total_mins = seconds_to_hours_mins(length)
            print(f"Total: {total_hours} hours and {total_mins} minutes")

        return length

    def get_length_of_feed(self, name: str):
        if self.feeds[name]:
            return self.__get_feed_length(self.feeds[name])

        return -1

    def __get_sample_rate(self, url: str):
        meta = ffmpeg.probe(url)
        duration = eval(meta["format"]["duration"])
        size = eval(meta["format"]["size"])
        return int(round(size / duration))

    def __get_duration_seconds(self, url: str, sample_rate: int):
        return self.__get_length_from_url(url) / sample_rate

    def __get_length_from_url(self, url: str):
        r = requests.head(url)
        content_length = r.headers["content-length"]
        return int(content_length)

    def __get_feed_length(self, url: str):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "lxml")
        audio_urls = []
        total_length_seconds = 0

        for item in soup.find_all("item"):
            audio_url = item.guid.string
            audio_urls.append(audio_url)

        sample_rate = self.__get_sample_rate(audio_urls[0])

        for u in tqdm(audio_urls, desc=url):
            duration = self.__get_duration_seconds(u, sample_rate)
            total_length_seconds += int(duration)

        return total_length_seconds

    def __get_episodes(self, url) -> list:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "lxml")
        episodes = []
        strp = "%a, %d %b %Y %H:%M:%S +%f"
        strp2 = "%a, %d %b %Y %H:%M:%S %Z"

        for item in soup.find_all("item"):
            if item.guid.attrs.get("ispermalink") == "false":
                audio_url = item.enclosure.attrs.get("url")
            else:
                audio_url = item.guid.string
            title = item.title.string
            date = item.pubdate.string
            try:
                d = datetime.strptime(date, strp)
            except ValueError:
                d = datetime.strptime(date, strp2)
            episode_name = (
                f"{d.year}.{str(d.month).zfill(2)}.{str(d.day).zfill(2)}_{title}"
            )
            episodes.append({"name": episode_name.replace("/", ""), "url": audio_url})
        return episodes

    def download_source_audio(self, source, output_path):
        url = self.feeds[source]
        episodes = self.__get_episodes(url)

        for episode in tqdm(episodes):
            path = Path(output_path, episode["name"] + ".mp3")
            if path.exists():
                continue
            r = requests.get(episode["url"])
            with open(path, "wb") as f:
                f.write(r.content)


def main():
    test_data = "test_data.json"
    source_handler = SourceHandler(test_data)

    # Get the rss dict {"name": "url"}
    rss_feeds = source_handler.get_rss_feeds()

    rss_handler = RSSFeedsHandler(rss_feeds)

    length = rss_handler.get_total_length(print_feed_lengths=True)
    hours, mins = seconds_to_hours_mins(length)
    print(f"Total: {hours} hours and {mins} minutes")

    # Test for individual feed
    name = "Í ljósi sögunnar"
    individual_length = rss_handler.get_length_of_feed(name)
    hours, mins = seconds_to_hours_mins(individual_length)
    print(f"{name}: {hours} hours and {mins} minutes")


if __name__ == "__main__":
    main()
