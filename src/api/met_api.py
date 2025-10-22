import requests
from loguru import logger
from pprint import pprint

BASE_URL = "https://collectionapi.metmuseum.org"


class MetAPI:
    def __init__(self) -> None:
        self.records_url = "/public/collection/v1/objects"

    def get_all_records(self) -> list[int]:
        all_records = requests.get(f"{BASE_URL}{self.records_url}")
        if all_records.status_code == 200:
            return all_records.json()["objectIDs"]
        else:
            logger.error("Failed to fetch all records")
            return []
