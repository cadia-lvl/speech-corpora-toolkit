#!/usr/bin/env python3

"""
    This module contains the SourceHandler class. The class is responsible for
    handling a sources json and outputting wished for information.

    Example:

    source_handler = SourceHandler(filepath)
    urls = source_handler.get_rss_urls()

    # urls contains a list with the rss feed url for each source

    EXTEND AS FUNCTIONALITY IS EXTENDED
"""

___author___ = "Staffan Hedström"
___license___ = "Apache 2.0"
___copyright___ = "2022 Staffan Hedström Reykjavík University"

import json
from utilities.utilities import standardize_string
import logging


class Headers(object):
    SOURCES = "sources"
    LAST_UPDATED = "last_updated"
    NAME = "name"
    RSS_URL = "rss_feed"
    TEXT_DIR = "text_dir"
    AUDIO_DIR = "audio_dir"
    MAPPING_FILE = "mapping_file"


class Source:
    def __init__(
        self, name, text_dir=None, audio_dir=None, rss_feed_url=None, mapping_file=None
    ) -> None:
        self.name = name
        self.name_ascii = standardize_string(name)
        self.text_dir = text_dir
        self.audio_path = audio_dir
        self.rss_feed_url = rss_feed_url
        self.mapping_file = mapping_file


class SourceHandler:
    def __init__(self, path) -> None:
        self.path = path
        # TODO: Add error handling
        with open(path, "r") as f:
            data = json.load(f)
            self.sources = data[Headers.SOURCES]
            self.last_updated = data[Headers.LAST_UPDATED]

    def get_source_names(self):
        names = []

        for source in self.sources:
            names.append(source[Headers.NAME])

        return names

    def get_source_names_ascii(self):
        names = []

        for source in self.sources:
            names.append(standardize_string(source[Headers.NAME]))

        return names

    def get_rss_urls(self):
        urls = []

        for source in self.sources:
            urls.append(source[Headers.RSS_URL])

        return urls

    def get_rss_feeds(self) -> dict:
        feeds = {}

        for source in self.sources:
            name = source[Headers.NAME]
            url = source[Headers.RSS_URL]
            feeds[name] = url

        return feeds

    def valid_source(self, source: Source) -> bool:
        if not source.name:
            logging.warning("Source is missing name. Skipping")
            return False
        if not source.url: 
            logging.warning(f"Source: '{source.name}' is missing url. This is ok as long as you are not downloading the sources.")
        if not source.audio_path: 
            logging.warning(f"Source: '{source.name}' is missing audio dir path. Skipping this source...")
            return False
        if not source.text_dir:
            logging.warning(f"Source: '{source.name}' is missing text dir path. Skipping this source...")
            return False
        if not source.mapping_file:
            logging.warning(f"Source '{source.name}' is missing a mapping file. Skipping this source...")
            return False

        return True

    def get_sources(self) -> list:
        s = []
        for source in self.sources:
            name = source[Headers.NAME]
            url = source[Headers.RSS_URL]
            text_dir = source[Headers.TEXT_DIR]
            audio_dir = source[Headers.AUDIO_DIR]
            mapping_file = source[Headers.MAPPING_FILE]

            source_to_add = Source(
                    name=name,
                    text_dir=text_dir,
                    audio_dir=audio_dir,
                    rss_feed_url=url,
                    mapping_file=mapping_file,
                )

            # Validate each source before adding
            if self.valid_source(source_to_add):
                s.append(source_to_add)

        return s


def main():
    path = "test_data.json"
    sh = SourceHandler(path)
    names = sh.get_source_names()
    print(names)


if __name__ == "__main__":
    main()
