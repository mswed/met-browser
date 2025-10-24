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
            return []

    def get_single_record(self, record_id):
        response = requests.get(f"{BASE_URL}{self.records_url}/{record_id}")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch record {record_id}")
            return {}

    def get_all_records_with_images(self) -> set[int]:
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
        for letter in tqdm(abc):
            all_search_records = requests.get(
                f"{BASE_URL}/public/collection/v1/search?hasImages=true&q={letter}"
            )

            found = all_search_records.json().get("objectIDs")
            for f in found:
                records.add(f)

            logger.info(f"Collected {len(list(records))} records")

        return records
