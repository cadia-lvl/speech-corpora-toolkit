#! /usr/bin/env python3
#
#  Copyright 2022 Judy Fong <lvl@judyyfong.xyz> Reykjavik University
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
    TODO: This file converts Hátalarinn text and audio episodes into a format usable
    by aligners so .txt and a standard audio file format, either .mp3 or .flac
"""
___author___ = "Judy Fong"
___license___ = "Apache 2.0"
___copyright___ = "2022 Judy Fong"

def main():
    """
        Write code here
        TODO: map text to audio files
              assume.txt files for hatalarinn are actually .doc files OR change .txt to .doc
              extract the text
    """
    # cat ruv_unprocessed/airdate2title2media.csv | grep 'Hátalarinn' but in
    # python
    # TODO: put in the json file
    orig_mapping_file = '/data/misc/ruv_unprocessed/airdate2title2media.csv'
    with open(original_mapping_file, 'w') as airdate:
        file_contents = airdate.read()
        # TODO if line has show name then keep, otherwise do nothing
        # TODO: put show name in json
        show_name = 'Hátalarinn'

    print()


if __name__ == '__main__':
    # this portion is run when this file is called directly by the command line
    main()
