#!/usr/bin/env python3

"""
    This class handles converting documents into a txt format.

    For a proof of concept this is tried with the same google presentation
    saved as .pdf and .pptx

    Functionality:
    reader = DocumentReader()
    reader.read(input_filepath)
    reader.save(output_filepath) # -> saves as plain text

    TODO: Clean .pdf output from itemized and numbered list symbols.

"""

___author___ = "Staffan Hedström"
___license___ = "Apache 2.0"
___copyright___ = "2022 Staffan Hedström Reykjavík University"

from pptx import Presentation
import pdfplumber
from docx import Document


class DocumentReader:
    def __init__(self) -> None:
        self.text = []

    def text_from_presentation(self, filepath) -> list:
        prs = Presentation(filepath)

        text = []

        for slide in prs.slides:
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        # Only add strings with text
                        if run.text:
                            text.append(run.text)
        self.text = text
        return text

    def text_from_pdf(self, filepath) -> list:
        text = []
        pdf = pdfplumber.open(filepath)
        for page in pdf.pages:
            text.append(page.extract_text())
        self.text = text
        return text

    def text_from_docx(self, filepath) -> list:
        text = []
        docx = Document(filepath)
        for p in docx.paragraphs:
            text.append(" ".join(p.text.split()))  # fixes a few whitespace issues
        return text

    def read(self, filepath) -> list:
        if ".pptx" in filepath:
            return self.text_from_presentation(filepath)
        if ".pdf" in filepath:
            return self.text_from_pdf(filepath)
        if ".docx" in filepath or ".doc" in filepath:
            return self.text_from_docx(filepath)
        return "Unknown format. Known formats are ['.pdf','.pptx', '.docx', '.doc']"

    def save(self, output_path) -> bool:
        # Clean output_path
        output_txt = self.to_txt_path(output_path)

        try:
            with open(output_txt, "w") as f:
                f.writelines(self.text)
            return True
        except IOError:
            print(
                "An error occurred while creating or writing to the file: \
                    {output_txt}"
            )
            return False

    def to_txt_path(self, path):
        """Makes a path end with .txt"""
        output = path.split(".")
        output[-1] = "txt"
        return ".".join(output)


def main():
    file = "document_handler/test_inputs/test_pdf.pdf"
    reader = DocumentReader()
    text = reader.read(file)
    for t in text:
        print(t)
    reader.save("document_handler/test_outputs/saved.txt")


if __name__ == "__main__":
    main()
