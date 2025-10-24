from datetime import datetime
import json
from pathlib import Path
from loguru import logger
from src.api.met_api import MetAPI


class ImageRecordCache:
    """
    Class to cache a list of record ids for records which are marked as having an image
    """

    def __init__(self) -> None:
        self.api = MetAPI()
        self.project_root = Path(__file__).parent.parent.parent
        self.cache_path = self.project_root / "data" / "image_cache.json"

    def save_cache(self, progress_callback=None):
        """
        Save the records as a json file
        """
        logger.info(f"Saving cache to {self.cache_path}")
        record_ids = self.api.get_all_records_with_images(
            progress_callback=progress_callback
        )

        data = {
            "updated_on": datetime.now().isoformat(),
            "record_ids": list(record_ids),
        }

        with open(self.cache_path, "w") as f:
            json.dump(data, f, indent=2)

    def load_cache(self) -> set:
        """
        Load the cach into the app
        :returns: A set of all record ids that are marked as having an image on the database
        """
        with open(self.cache_path, "r") as f:
            data = json.load(f)
            record_ids = [int(r) for r in data.get("record_ids")]
            return set(record_ids)
