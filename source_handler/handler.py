import json


class Headers(object):
    SOURCES = "sources"
    LAST_UPDATED = "last_updated"
    NAME = "name"
    RSS_URL = "rss_feed"


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

    def get_rss_urls(self):
        urls = []

        for source in self.sources:
            urls.append(source[Headers.RSS_URL])

        return urls


def main():
    path = "test_data.json"
    sh = SourceHandler(path)
    names = sh.get_source_names()
    print(names)


if __name__ == "__main__":
    main()
