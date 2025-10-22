import requests
import time
from loguru import logger
from tqdm import tqdm
from pprint import pprint


class RateLimitedSession:
    """
    The Met API asks us to limit our queries to 80 per second. This class allows us to do that
    """

    def __init__(self, requests_per_second=80) -> None:
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0

    def get(self, url, **kwargs):
        """
        Send a request to the API if enough time has passed
        """
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            logger.info("not enough time has passed! Sleeping")
            # Not enough time has past since the last query. Sleep.
            time.sleep(self.min_interval - elapsed)

        # Run the query
        self.last_request_time = time.time()
        return requests.get(url, **kwargs)


def build_local_index(requests_per_second=75):
    """
    Build a local index of record ids and their classifications for a faster/easier search
    """

    session = RateLimitedSession(requests_per_second=requests_per_second)

    logger.info("Getting all record ids")
    response = session.get(
        "https://collectionapi.metmuseum.org/public/collection/v1/objects"
    )
    record_ids = response.json().get("objectIDs", [])
    if not record_ids:
        raise RuntimeError("No records found")

    total_records = len(record_ids)
    logger.info(
        f"Total records found {total_records}. Indexing will take ~{total_records / requests_per_second / 60:.1f} minutes"
    )

    classifications_index = {}
    reverese_index = {}
    errors = []

    for i, record_id in enumerate(tqdm(record_ids[:160])):
        # Get record details
        res = session.get(
            f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{record_id}"
        )

        if res.status_code == 200:
            # We got the info from the API
            data = res.json()
            classification = data.get("classification", "wtf")
            logger.info(f"{record_id} --> {classification}")
            if classification == "":
                classification = "N/A"

            if classification not in classifications_index:
                classifications_index[classification] = []

            classifications_index[classification].append(record_id)

        else:
            errors.append(f"Record {record_id}: returned status {res.status_code}")
            raise

    pprint(classifications_index)
    pprint(errors)


build_local_index()
