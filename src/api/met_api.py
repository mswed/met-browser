import requests
from loguru import logger
from pprint import pprint

BASE_URL = "https://collectionapi.metmuseum.org"


class MetAPI:
    def __init__(self) -> None:
        self.records_url = "/public/collection/v1/objects"

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
            logger.error("Failed to fetch all records")
            return {}


ma = MetAPI()
test = ma.get_single_record(438848)
pprint(test)
