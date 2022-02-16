import os
from bs4 import BeautifulSoup
import requests
import vlc

from source_handler.handler import SourceHandler
from utilities.utilities import seconds_to_hours_mins
from tqdm import tqdm


def get_duration_seconds(url: str):
    # Turn of vlc error logging
    os.environ["VLC_VERBOSE"] = str("-1")

    media = vlc.MediaPlayer(url)
    media.play()  # need to play audio to get length
    media.audio_set_mute(True)

    time = media.get_length() / 1000  # seconds
    while time <= 0:
        time = media.get_length() / 1000  # seconds
    media.stop()

    return time


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

    duration_seconds = get_duration_seconds(audio_urls[0])

    content_length = get_length_from_url(audio_urls[0])

    sample_rate = round(content_length / duration_seconds)

    for u in tqdm(audio_urls, desc=url):
        content_length = get_length_from_url(u)
        total_length_seconds += int(content_length) / sample_rate

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
