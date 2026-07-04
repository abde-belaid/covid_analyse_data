import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import pandas as pd
from minio import Minio

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.minio_utils import create_buckets
from scripts.prepare_owid_data import (
    extract_vaccination_data,
    extract_mortality_data,
    extract_testing_data,
    extract_cases_data,
)
from scripts.utils import load_env

def _build_minio_client(env):
    endpoint = env.get("MINIO_ENDPOINT")
    secure = False
    if endpoint:
        normalized = endpoint.strip()
        secure = normalized.startswith("https://")
        endpoint = normalized.replace("http://", "").replace("https://", "")
    else:
        host = env.get("MINIO_HOST")
        port = env.get("MINIO_PORT")
        if not host or not port:
            raise EnvironmentError(
                "MINIO_HOST and MINIO_PORT must be set in .env when MINIO_ENDPOINT is not defined."
            )
        endpoint = f"{host}:{port}"

    return Minio(
        endpoint=endpoint,
        access_key=env.get("MINIO_ROOT_USER"),
        secret_key=env.get("MINIO_ROOT_PASSWORD"),
        secure=secure,
    )


def _download_to_local(url, destination_path):
    try:
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request) as response, open(destination_path, "wb") as local_file:
            local_file.write(response.read())
        print(f"Downloaded remote source to {destination_path}")
    except HTTPError as exc:
        raise RuntimeError(f"HTTP error downloading {url}: {exc.code} {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"URL error downloading {url}: {exc.reason}") from exc


def _load_source_file(env, tmp_dir):
    local_file = env.get("COVID_DATA_FILE")
    if local_file:
        source_path = Path(local_file)
        if source_path.exists():
            print(f"Using local source file: {local_file}")
            return source_path
        raise FileNotFoundError(f"Local source file not found: {local_file}")

    source_url = env.get("COVID_DATA_URL")
    if not source_url:
        raise EnvironmentError(
            "Data source missing: set COVID_DATA_URL or COVID_DATA_FILE in .env"
        )

    destination = tmp_dir / "owid_source.csv"
    print(f"Downloading source file from {source_url}")
    _download_to_local(source_url, destination)
    return destination


def _upload_csv_to_bronze(client, bucket_name, object_name, file_path):
    with open(file_path, "rb") as data:
        file_size = file_path.stat().st_size
        client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=data,
            length=file_size,
            content_type="text/csv",
        )
    print(f"Uploaded {object_name} to bucket '{bucket_name}'")


def ingest_bronze_data():
    env = load_env()
    create_buckets()

    bucket_name = env["MINIO_BUCKET_BRONZE"]
    minio_client = _build_minio_client(env)

    with TemporaryDirectory() as tmpdir:
        tmp_dir = Path(tmpdir)
        source_file = _load_source_file(env, tmp_dir)

        print(f"Reading source CSV from {source_file}")
        df = pd.read_csv(source_file, low_memory=False)

        extracted = []
        if any(col in df.columns for col in ["total_vaccinations", "people_vaccinated", "people_fully_vaccinated", "people_boosted"]):
            vaccination_path = tmp_dir / "vaccination.csv"
            extract_vaccination_data(df, str(vaccination_path))
            _upload_csv_to_bronze(minio_client, bucket_name, "vaccination.csv", vaccination_path)
            extracted.append("vaccination.csv")

        if any(col in df.columns for col in ["total_deaths", "new_deaths"]):
            mortality_path = tmp_dir / "mortality.csv"
            extract_mortality_data(df, str(mortality_path))
            _upload_csv_to_bronze(minio_client, bucket_name, "mortality.csv", mortality_path)
            extracted.append("mortality.csv")

        if any(col in df.columns for col in ["total_tests", "new_tests", "tests_per_case", "positive_rate"]):
            testing_path = tmp_dir / "testing.csv"
            extract_testing_data(df, str(testing_path))
            _upload_csv_to_bronze(minio_client, bucket_name, "testing.csv", testing_path)
            extracted.append("testing.csv")

        if any(col in df.columns for col in ["total_cases", "new_cases"]):
            cases_path = tmp_dir / "cases.csv"
            extract_cases_data(df, str(cases_path))
            _upload_csv_to_bronze(minio_client, bucket_name, "cases.csv", cases_path)
            extracted.append("cases.csv")

        if not extracted:
            raise RuntimeError(
                "No valid OWID columns were found in the source dataset. "
                "Verify that the input CSV contains at least one of the expected columns for vaccination, mortality, testing, or cases."
            )

        print("\nBronze ingestion completed. Uploaded files:")
        for item in extracted:
            print(f" - {item}")

    return extracted


if __name__ == "__main__":
    ingest_bronze_data()
