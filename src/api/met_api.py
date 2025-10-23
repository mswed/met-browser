import requests
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

    def get_all_records_with_images(self) -> list[int]:
        """
        Fetch all of the records that have an image
        """
        logger.info("Fetching all records with images")
        params = {"q": "*", "hasImages": "true"}
        response = requests.get(f"{BASE_URL}{self.search_url}", params=params)
        if response.status_code == 200:
            return set(response.json()["objectIDs"])
        else:
            logger.error("Failed to fetch all records with images")
            return []
