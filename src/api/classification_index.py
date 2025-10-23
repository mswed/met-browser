import json
from pathlib import Path
from typing import List, Optional, Dict
from loguru import logger


class ClassificationIndex:
    """
    Access the local index to allow remote API searches
    """

    def __init__(self, index_path=None) -> None:
        if index_path is None:
            # Default to our index path
            project_root = Path(__file__).parent.parent.parent
            index_path = project_root / "data" / "classification_index.json"

        self.index_path = index_path
        self.data = self.load_index()

    def load_index(self) -> Dict:
        """
        Load the index file for processing
        """

        with open(self.index_path, "r") as f:
            data = json.load(f)
            return data

    def get_classification_list(self) -> List:
        """
        Get all availabe classifications from the index
        """

        if self.data is not None:
            classifications = list(self.data.get("classification_index").keys())
            return sorted(classifications)

        return []

    def get_records_in_classification(self, classification: str) -> List:
        """
        Return the first 80 records in a given classification
        :param classification: Name of classification
        :return: List of records associated with the classification
        """

        if self.data is not None:
            return self.data.get("classification_index", {}).get(classification, [])[
                :80
            ]

        return []

    def get_record_classification(self, record_id: int) -> Optional[str]:
        """
        Get a records classification. This is not actually used, but more of a place holder for a syncing
        functionality with the actual database
        """

        if self.data is not None:
            return self.data.get("reverse_index", {}).get(record_id)

        return None
