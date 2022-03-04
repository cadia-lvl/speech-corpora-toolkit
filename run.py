#!/usr/bin/env python3

"""
    This is the main script for handling raw data sources.

    The script assumes that the user has a valid sources.json file which
    contains necessary information like
    audio_dir
    text_dir
    mappings_dir
    name

    Functionality:
    run
    python main.py -i input.json -o output_folder -ca

    this will for each source in input.json

    1. Generate the folder structure in the output folder,
        see "generate_folder_structure" for details
    2.
        a) -ca -> Convert audio to .wav and copy to output folder
        b) -gas -> Generate audio symlinks in the audio folder for the source
    3. Convert text documents to .txt files
        and put them into the text folder for the source
    4. Generate a new mappings.tsv file


"""

___author___ = "Staffan Hedström"
___license___ = "Apache 2.0"
___copyright___ = "2022 Staffan Hedström Reykjavík University"

from source_handler.handler import Source, SourceHandler
from document_handler.document_to_text import DocumentReader
from utilities.utilities import copy_and_convert_to_wav
import os
import logging
import argparse
import pandas as pd
from pathlib import Path


def generate_folder_structure(source_names: list, destination) -> None:
    """
    Generates the desired folder structure in the destination folder
    Creates all folders to the destination path as necessary

    Folder structure
    destination_folder/
        |___source_1_name/
            |____audio/
            |____text/
        |___source_2_name/
            |___audio/
            |___text/
        ...
    """
    for name in source_names:
        path = os.path.join(destination, name)
        audio_path = os.path.join(path, "audio")
        text_path = os.path.join(path, "text")

        try:
            os.makedirs(audio_path)
            os.makedirs(text_path)
        except FileExistsError:
            logging.warning(f"Folder {audio_path} or {text_path} already exists")


def generate_txt_files(sources: list, destination) -> None:
    """
    Converts all text files to txt files and places them in the
    destination / source_name / text folder.
    """
    reader = DocumentReader()

    for source in sources:
        if isinstance(source, Source):
            if not os.path.exists(source.text_dir):
                logging.error(
                    f"Audio path for {source.name_ascii} \
                        cannot be found: '{source.text_dir}' \
                        skipping..."
                )
                continue
            text_dest_folder = os.path.join(destination, source.name_ascii, "text")
            for root, dirs, files in os.walk(source.text_dir):
                for file in files:
                    reader.read(os.path.join(root, file))
                    reader.save(os.path.join(text_dest_folder, file))


def generate_audio(sources: list, destination, copy=False) -> None:
    """
    Generates audio symlinks into the destination path for each source.

    Uses the source audio dir to find the original audio files, and for each
    creates a symlink in the destination / source_name / audio folder.

    This relies on that the folder structure has already been created.
    """
    for source in sources:
        if isinstance(source, Source):
            if not os.path.exists(source.audio_path):
                logging.error(
                    f"Audio path for {source.name_ascii} \
                        cannot be found: '{source.audio_path}'"
                )
            audio_folder = os.path.join(destination, source.name_ascii, "audio")
            for root, dirs, files in os.walk(source.audio_path):
                logging.info(f"Found {len(files)} audio files for {source.name_ascii}")
                for file in files:
                    try:
                        if copy:
                            copy_and_convert_to_wav(
                                os.path.join(root, file),
                                os.path.join(audio_folder, file),
                            )
                        else:  # else create symlinks to save space
                            if ".wav" not in file:
                                logging.warn(
                                    "The audio is not in .wav format. \
                                    Continue with care or run with -ca command."
                                )
                            os.symlink(
                                os.path.join(root, file),
                                os.path.join(audio_folder, file),
                            )

                    except FileExistsError:
                        logging.warn(
                            f"File: '{os.path.join(audio_folder, file)}' already exits"
                        )


def __format_audio_mapping(path: str) -> str:
    return str(Path("audio") / Path(path).name)


def __format_text_mapping(path: str) -> str:
    return str(Path("text") / f"{Path(path).stem}.txt")


def map_and_standardize_filenames(sources: list, destination) -> None:
    for source in sources:
        if isinstance(source, Source):
            if not os.path.exists(source.mapping_file):
                logging.error(
                    f"Cannot find the mapping file: {source.mapping_file} for {source}"
                )
                continue
        mapping = pd.read_csv(source.mapping_file, sep="\t")

        mapping.audio = mapping.audio.apply(__format_audio_mapping)
        mapping.text = mapping.text.apply(__format_text_mapping)

        mapping = standardize_files(mapping, destination, source.name_ascii)

        # Check if file exists?
        mapping.to_csv(Path(destination, source.name_ascii, "mapping.tsv"), sep="\t")


def standardize_files(
    mapping_dataframe: pd.DataFrame, destination, source_name
) -> pd.DataFrame:
    """
    Standardizes the files in the destination folder according to
    source_name_000XX.txt
    source_name_000XX.wav

    Uses the data in the mapping_dataframe to rename the files sp
    that the audio file and matching text file have matching names.
    """
    audio_new_files = []
    text_new_files = []

    audio_folder = Path(destination, source_name, "audio")
    text_folder = Path(destination, source_name, "text")

    for row in mapping_dataframe.iterrows():
        file_number = row[0] + 1
        audio = f"{Path(row[1].audio).stem}.wav"
        text = f"{Path(row[1].text).stem}.txt"
        audio_new_name = f"{source_name}_{str(file_number).zfill(6)}.wav"
        text_new_name = f"{source_name}_{str(file_number).zfill(6)}.txt"

        os.rename(Path(audio_folder, audio), Path(audio_folder, audio_new_name))
        os.rename(Path(text_folder, text), Path(text_folder, text_new_name))

        audio_new_files.append(audio_new_name)
        text_new_files.append(text_new_name)

    mapping_dataframe.audio = audio_new_files
    mapping_dataframe.text = text_new_files

    return mapping_dataframe


def main():
    parser = argparse.ArgumentParser(
        description="Formats and converts the data into a ready for alignment state"
    )

    parser.add_argument(
        "-skip_fs",
        "--skip_folder_structure",
        required=False,
        help="Use this flag to skip the generation of the folder structure.",
        action="store_true",
    )

    parser.add_argument(
        "-gas",
        "--generate_audio_symlinks",
        required=False,
        help="Use this flag to generate audio symlinks. Only use this if you know the \
            audio has the correct format already.",
        action="store_false",
    )

    parser.add_argument(
        "-sd",
        "--skip_convert_documents",
        required=False,
        help="Use this flag to skip the convertion of documents (pdf, pptx...) to .txt",
        action="store_true",
    )

    parser.add_argument(
        "-sm",
        "--skip_mapping",
        required=False,
        help="Use this flag to skip the generation of a mapping file.",
        action="store_true",
    )

    parser.add_argument(
        "-ca",
        "--copy_audio",
        required=False,
        help="Use this flag to convert the audio to .wav and copy it to the output folder. \
            Will take precedence over generate audio symlinks.",
        action="store_true",
    )

    parser.add_argument(
        "-output",
        "--output_folder",
        required=False,
        help="Set the path to the output folder. default=output",
        default="output",
    )

    parser.add_argument(
        "-i",
        "--input_source_json",
        required=False,
        help="Path to the source.json file.",
        default="test_data.json",
    )

    args = parser.parse_args()

    # Source handler
    source_file = args.input_source_json
    source_handler = SourceHandler(source_file)

    # Output folder
    output = args.output_folder
    sources = source_handler.get_sources()
    sources_names = source_handler.get_source_names_ascii()

    if not args.skip_folder_structure:
        generate_folder_structure(sources_names, output)

    if args.copy_audio:
        generate_audio(sources, output, copy=True)

    elif args.generate_audio_symlinks:
        generate_audio(sources, output)

    if not args.skip_convert_documents:
        generate_txt_files(sources, output)

    # Mapping has to be done before
    # This should only generate a new mapping file with new file names and file
    # extensions
    if not args.skip_mapping:
        map_and_standardize_filenames(sources, output)


if __name__ == "__main__":
    main()
