import requests
from tqdm import tqdm
from loguru import logger

BASE_URL = "https://collectionapi.metmuseum.org"


class MetAPI:
    def __init__(self) -> None:
        self.records_url = "/public/collection/v1/objects"
        self.search_url = "/public/collection/v1/search"

    def get_all_records(self) -> list[int]:
        response = requests.get(f"{BASE_URL}{self.records_url}")
        if response.status_code == 200:
            return response.json()["objectIDs"]
        else:
            logger.error("Failed to fetch all records")
            raise ConnectionError("Failed to fetch all reccords")

    def get_single_record(self, record_id):
        response = requests.get(f"{BASE_URL}{self.records_url}/{record_id}")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch record {record_id}")
            raise ConnectionError(f"Failed to fetch record {record_id}")

    def get_all_records_with_images(self, progress_callback=None) -> set[int]:
        """
        Fetch all of the records that have an image
        """
        logger.info("Fetching all records with images")
        records = set()
        abc = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
        ]
        for i, letter in enumerate(abc):
            if progress_callback:
                progress_callback(i + 1, len(abc), f"Searching for letter {letter}")
            response = requests.get(
                f"{BASE_URL}/public/collection/v1/search?hasImages=true&q={letter}"
            )

            if response.status_code == 200:
                found = response.json().get("objectIDs")
                records.update(found)

                logger.info(f"Collected {len(list(records))} records")
            else:
                raise ConnectionError(f"Failed to fetch records for {letter}")

        return records
