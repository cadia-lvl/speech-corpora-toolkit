#!/usr/bin/env python3

"""
    This is the main script for handling raw data sources.

    The script assumes that the user has a valid sources.json file which
    contains necessary information like
    audio_dir
    text_dir
    mappings_file
    name

    Functionality:
    run
    python run.py -i input.json -o output_folder -wave

    this will for each source in input.json

    1. Generate the folder structure in the output folder,
        see "generate_folder_structure" for details
    2.
        a) -wave -> Convert audio to .wav and copy to output folder
        b) -gas -> Generate audio symlinks in the audio folder for the source
        c) -ca -> Copy the audio files to the output folder
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
import shutil
from tqdm import tqdm


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
    for name in tqdm(source_names, "Generating folders"):
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
        if not isinstance(source, Source):
            continue
        if not os.path.exists(source.text_dir):
            logging.error(
                f"Audio path for {source.name_ascii} \
                    cannot be found: '{source.text_dir}' \
                    skipping..."
            )
            continue
        mapping_file = Path(destination, source.name_ascii, "mapping.tsv")
        if not mapping_file.exists():
            logging.error(
                f"Cannot find the matching mapping file for source: {source.name_ascii}"
            )
            continue

        mapping = pd.read_csv(mapping_file, sep="\t")
        text_dest_folder = os.path.join(destination, source.name_ascii, "text")
        for root, dirs, files in os.walk(source.text_dir):
            for file in tqdm(files, f"Converting documents for {source.name_ascii}"):
                if file in mapping.text.values:
                    reader.read_and_trim(os.path.join(root, file), source.trim_list)
                    reader.save(os.path.join(text_dest_folder, file))


def generate_audio(sources: list, destination, copy=False, wave=False) -> None:
    """
    Generates audio symlinks into the destination path for each source.

    Uses the source audio dir to find the original audio files, and for each
    creates a symlink in the destination / source_name / audio folder.

    This relies on that the folder structure has already been created.
    This also relies on that the matching mappings file has been generated.
    """
    for source in sources:
        if isinstance(source, Source):
            if not os.path.exists(source.audio_path):
                logging.error(
                    f"Audio path for {source.name_ascii} \
                        cannot be found: '{source.audio_path}'"
                )
                continue
            mapping = pd.read_csv(
                Path(destination, source.name_ascii, "mapping.tsv"), sep="\t"
            )
            audio_folder = os.path.join(destination, source.name_ascii, "audio")
            for root, dirs, files in os.walk(source.audio_path):
                logging.info(f"Found {len(files)} audio files for {source.name_ascii}")
                for file in tqdm(files, f"Generating audio for: {source.name_ascii}"):
                    # If file not in the matching mapping file, then skip it
                    if file not in mapping.audio.values:
                        continue
                    try:
                        if copy and wave:
                            copy_and_convert_to_wav(
                                os.path.join(root, file),
                                os.path.join(audio_folder, file),
                            )
                        elif copy:
                            shutil.copy(Path(root, file), Path(audio_folder, file))
                        else:  # else create symlinks to save space
                            os.symlink(
                                os.path.join(root, file),
                                os.path.join(audio_folder, file),
                            )

                    except FileExistsError:
                        logging.warn(
                            f"File: '{os.path.join(audio_folder, file)}' already exits"
                        )


def make_matching_maps(sources: list, destination: str) -> None:
    for source in tqdm(sources, "Making mapping files."):
        if not isinstance(source, Source) or not Path(source.mapping_file).exists:
            logging.error(
                f"Cannot find the mapping file: {source.mapping_file} for {source}"
            )
            continue

        mapping = pd.read_csv(source.mapping_file, sep="\t")
        audio_files = os.listdir(source.audio_path)
        text_files = os.listdir(source.text_dir)

        matching_audio = []
        matching_text = []

        for row in mapping.iterrows():
            if row[1].text in text_files and row[1].audio in audio_files:
                matching_audio.append(row[1].audio)
                matching_text.append(row[1].text)

        matching_mapping = pd.DataFrame()
        matching_mapping["text"] = matching_text
        matching_mapping["audio"] = matching_audio

        matching_mapping.to_csv(
            Path(destination, source.name_ascii, "mapping.tsv"), sep="\t", index=False
        )


def __format_audio_mapping(path: str) -> str:
    return str(Path("audio") / Path(path).name)


def __format_text_mapping(path: str) -> str:
    return str(Path("text") / f"{Path(path).stem}.txt")


def map_and_standardize_filenames(sources: list, destination, wave) -> None:
    for source in tqdm(sources, "Standardizing filenames."):
        if not isinstance(source, Source):
            logging.error(f"Cannot read source: {source}")
            continue
        mapping_path = Path(destination, source.name_ascii, "mapping.tsv")
        if not mapping_path.exists():
            logging.error(f"Cannot find the mapping file: {mapping_path} for {source}")
            continue
        mapping = pd.read_csv(mapping_path, sep="\t")

        # Keep original file names
        mapping["original_text_name"] = mapping.text
        mapping["original_audio_name"] = mapping.audio

        mapping.audio = mapping.audio.apply(__format_audio_mapping)
        mapping.text = mapping.text.apply(__format_text_mapping)

        mapping = standardize_files(mapping, destination, source.name_ascii, wave)

        # Check if file exists?
        mapping.to_csv(
            Path(destination, source.name_ascii, "mapping.tsv"), sep="\t", index=False
        )


def standardize_files(
    mapping_dataframe: pd.DataFrame, destination, source_name, wave
) -> pd.DataFrame:
    """
    Standardizes the files in the destination folder according to
    source_name_000XX.txt
    source_name_000XX.wav

    Uses the data in the mapping_dataframe to rename the files so
    that the audio file and matching text file have matching names.
    """
    audio_new_files = []
    text_new_files = []

    audio_folder = Path(destination, source_name, "audio")
    text_folder = Path(destination, source_name, "text")

    for row in mapping_dataframe.iterrows():
        file_number = row[0] + 1
        audio = f"{Path(row[1].audio).name}"
        audio_format = Path(row[1].audio).suffix

        if wave:
            audio = audio.replace(audio_format, ".wav")
            audio_format = ".wav"
        text = f"{Path(row[1].text).stem}.txt"
        audio_new_name = f"{source_name}_{str(file_number).zfill(6)}{audio_format}"
        text_new_name = f"{source_name}_{str(file_number).zfill(6)}.txt"

        os.rename(Path(audio_folder, audio), Path(audio_folder, audio_new_name))
        os.rename(Path(text_folder, text), Path(text_folder, text_new_name))

        audio_new_files.append(audio_new_name)
        text_new_files.append(text_new_name)

    mapping_dataframe.text = text_new_files
    mapping_dataframe.audio = audio_new_files

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
        help="Use this flag to copy the audio to the output folder. \
            Will take precedence over generate audio symlinks.",
        action="store_true",
    )

    parser.add_argument(
        "-wave",
        "--convert_to_wave",
        required=False,
        help="Use this flag to convert the audio to wave format.",
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
        "-i", "--input_source_json", required=True, help="Path to the source.json file."
    )

    args = parser.parse_args()

    # Source handler
    source_file = args.input_source_json
    source_handler = SourceHandler(source_file)

    # Output folder
    output = args.output_folder
    sources = source_handler.get_sources()
    sources_names = source_handler.get_source_names_ascii()

    # Step 1 generate folder structure unless instructed to not to
    # Skip if already generated for all sources
    if not args.skip_folder_structure:
        generate_folder_structure(sources_names, output)

    # Step 2 Generate the matching maps file
    # In case of some audio file not matching some text file or vise verse
    # Make a matching mapping file for each source
    make_matching_maps(sources, output)

    # Step 3 Copy/Generate symlinks to audio files
    if args.copy_audio or args.convert_to_wave:
        generate_audio(sources, output, copy=True, wave=args.convert_to_wave)

    elif args.generate_audio_symlinks:
        generate_audio(sources, output)

    # Step 4 Generate the text files from documents
    if not args.skip_convert_documents:
        generate_txt_files(sources, output)

    # Step 5 Standardize file names in and outside of mappings file
    if not args.skip_mapping:
        map_and_standardize_filenames(sources, output, wave=args.convert_to_wave)


if __name__ == "__main__":
    main()
