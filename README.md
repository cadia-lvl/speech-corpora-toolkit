# Speech Corpora Toolkit

A collection of tools for processing public domain audio and scripts to prepare them for segmentation and alignment.

The output for each source should be the same and be presented in the following folder structure.

```
output_folder
├── source_1_name
│   ├── audio
│   │   ├── source_1_name_00001.mp3
│   │   ├── **/*.mp3
│   ├── text
│   │   ├── source_1_name_00001.txt
│   │   ├── **/*.txt
│   ├── map.tsv
├── source_2_name
│   ├── audio
│   │   ├── source_2_name_00001.mp3
│   │   ├── **/*.mp3
│   ├── text
│   │   ├── source_2_name_00001.txt
│   │   ├── **/*.txt
│   ├── map.tsv
...
```

To be able to generate this. The input should be a sources.json file of the following format.

```json
{
  "last_updated": "2022-04-08",
  "sources": [
    {
      "name": "Source number 1",
      "rss_feed": "https://link.to.source.1.rss/",
      "text_dir": "<path source 1 script files>",
      "text_format": "doc",
      "audio_dir": "<path source 1 audio files>",
      "mapping_file": "<path source 1 mapping file>"
    },
    {
      "name": "Source number 1",
      "rss_feed": "https://link.to.source.2.rss/",
      "text_dir": "<path source 2 script files>",
      "text_format": "pdf",
      "audio_dir": "<path source 2 audio files>",
      "mapping_file": "<path source  mapping file>"
    }
  ]
}
```

The mapping file should be a tab separated file that connects scripts and audio files together.

# Tools

## sources_handler

The source handler is a helper class to help handle the sources. It is responsible for reading the sources.json and providing access to all relevant information there to the rest of the code.

## document_handler

The document handler is responsible for converting different types of text documents into .txt files.

This could be extended in the future to include trim tags. Tags that would indicate that that text should be removed from the output text.

So far it supports conversion to txt from:

- pdf
- doc
- docx
- pptx

## rss_handler

The rss handler handles all things to do with rss feeds. Like downloading audio files, estimating source lengths and so forth.

# Running the pre-processing

To run the pre-processing simply populate a sources.json and run the following code

```python
python run.py -i sources.json
```

This will:

- Generate the standardized folder structure for each source
- Generate symbolic links for all audio
- Convert all text files into .txt
- Standardize all filenames and generate mapping file

There some options. It is possible to create symbolic links instead of copying the audio files. Creating .wav files in the output folder and more. For a list of options run.

```python
python run.py -h
```

# Requirements

A requirements file has been provided for your convenience and the project is setup as an installable module. You can chose to either

install the module

```python
python setup.py install
```

Which will install the requirements as well.

Or install the requirements

```python
pip install -r requirements.txt
```

# Authors / Credit

Reykjavik University

- Staffan Hedström
- Judy Y. Fong

# Acknowledgments

This project was funded by the Language Technology Programme for Icelandic 2019-2023. The programme, which is managed and coordinated by Almannarómur, is funded by the Icelandic Ministry of Education, Science and Culture.
