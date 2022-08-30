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

import os
from datetime import datetime

def main():
    """
        Write code here
        TODO: map text to audio files
              assume.txt files for hatalarinn are actually .rtf files OR change
              .txt to .rtf
              extract the text
    """
    original_mapping_file = '/data/misc/ruv_unprocessed/airdate2title2media.csv'
    with open(original_mapping_file, 'r') as mapping:
        show_name = 'Hátalarinn'
        # If line has show name then keep
        hatalarinn_lines = set([line.rstrip() for line in mapping if show_name in line])
        print(len(hatalarinn_lines))

    scripts_folder = 'ruv_unprocessed/transcripts/radiotranscripts/Hátalarinn/'
    dir_list = os.listdir(scripts_folder)
    # Get list of script files
    txt_list = [line for line in dir_list if line.endswith('.txt')]
    print(len(txt_list))
    matches = {}
    for item in txt_list:
        episode_date = datetime.strptime(item[10:18],'%d%m%Y').strftime('%Y-%m-%d')
        for airdate in hatalarinn_lines:
            if episode_date in airdate:
                segments = airdate.split(',')
                print('\n' + scripts_folder + item)
                print('ruv_unprocessed/audio/Hátalarinn/\'' + segments[2] + '\'')
                print(airdate)
                break
        # also extract the dates
        # TODO: put show name in json


if __name__ == '__main__':
    # this portion is run when this file is called directly by the command line
    main()
