import os
import sys
import pandas as pd
import pdfplumber
from typing import Optional

from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException


class FileParser:
    """
    Handles parsing of financial files (CSV, Excel, PDF)
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def parse_csv(self, file_path: str) -> pd.DataFrame:
        try:
            self.logger.info(f"Parsing CSV file: {file_path}")
            return pd.read_csv(file_path)
        except Exception as e:
            self.logger.error("CSV parsing failed", exc_info=True)
            raise CustomException(e, sys)

    def parse_excel(self, file_path: str) -> pd.DataFrame:
        try:
            self.logger.info(f"Parsing Excel file: {file_path}")
            return pd.read_excel(file_path)
        except Exception as e:
            self.logger.error("Excel parsing failed", exc_info=True)
            raise CustomException(e, sys)

    def parse_pdf(self, file_path: str) -> pd.DataFrame:
        """
        Naive PDF table parser.
        Improves later with layout-aware extraction.
        """
        all_rows = []

        try:
            self.logger.info(f"Parsing PDF file: {file_path}")

            with pdfplumber.open(file_path) as pdf:
                for page_number, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if not text:
                        self.logger.warning(
                            f"No text found on page {page_number}"
                        )
                        continue

                    for line in text.split("\n"):
                        columns = [c.strip() for c in line.split(",")]
                        all_rows.append(columns)

            df = pd.DataFrame(all_rows)
            return df

        except Exception as e:
            self.logger.error("PDF parsing failed", exc_info=True)
            raise CustomException(e, sys)

    def parse_file(self, file_path: str) -> pd.DataFrame:
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            extension = file_path.split(".")[-1].lower()

            self.logger.info(f"Detected file extension: {extension}")

            if extension == "csv":
                return self.parse_csv(file_path)

            if extension in ("xls", "xlsx"):
                return self.parse_excel(file_path)

            if extension == "pdf":
                return self.parse_pdf(file_path)

            raise ValueError(f"Unsupported file format: {extension}")

        except Exception as e:
            self.logger.error("File parsing failed", exc_info=True)
            raise CustomException(e, sys)

    @staticmethod
    def preview_data(df: pd.DataFrame, rows: int = 5) -> pd.DataFrame:
        return df.head(rows)
