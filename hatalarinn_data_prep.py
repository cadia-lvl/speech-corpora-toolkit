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
              assume.txt files for hatalarinn are actually .rtf files OR change
              .txt to .rtf
              extract the text
    """
    original_mapping_file = '/data/misc/ruv_unprocessed/airdate2title2media.csv'
    with open(original_mapping_file, 'r') as airdate:
        show_name = 'Hátalarinn'
        # If line has show name then keep
        hatalarinn_lines = [line for line in airdate if show_name in line]
        print(hatalarinn_lines)
        print(len(hatalarinn_lines))

    # TODO: get list of script files
        # TODO: put show name in json


if __name__ == '__main__':
    # this portion is run when this file is called directly by the command line
    main()
