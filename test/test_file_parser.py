import pandas as pd
import pytest

from backend.services.file_parser import FileParser
from backend.utils.exceptions import CustomException


@pytest.fixture
def parser():
    return FileParser()


@pytest.fixture
def csv_file_path():
    return r"E:\financial-health-ai\notebook\sample_finance.csv"


@pytest.fixture
def pdf_file_path():
    return r"E:\financial-health-ai\notebook\sample_finance.csv.pdf"


@pytest.fixture
def invalid_file_path():
    return r"E:\financial-health-ai\notebook\does_not_exist.csv"


def test_parse_csv_success(parser, csv_file_path):
    df = parser.parse_csv(csv_file_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_parse_csv_via_parse_file(parser, csv_file_path):
    df = parser.parse_file(csv_file_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_parse_pdf_success(parser, pdf_file_path):
    df = parser.parse_pdf(pdf_file_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_parse_pdf_via_parse_file(parser, pdf_file_path):
    df = parser.parse_file(pdf_file_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_file_not_found(parser, invalid_file_path):
    with pytest.raises(CustomException):
        parser.parse_file(invalid_file_path)


def test_unsupported_file_format(parser, tmp_path):
    fake_file = tmp_path / "data.txt"
    fake_file.write_text("random")

    with pytest.raises(CustomException):
        parser.parse_file(str(fake_file))


def test_preview_data(parser, csv_file_path):
    df = parser.parse_csv(csv_file_path)
    preview = parser.preview_data(df, rows=3)

    assert isinstance(preview, pd.DataFrame)
    assert len(preview) == 3
