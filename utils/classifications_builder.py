import csv
import json
from tqdm import tqdm
from src.api.met_api import MetAPI


def build_classification_index(csv_path="../MetObjects.txt"):
    classification_index = {}
    reverse_index = {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in tqdm(reader):
            object_id = row.get("Object ID", "")
            # The ID needs to be a integer
            try:
                object_id = int(object_id)
            except (ValueError, TypeError):
                continue

            classification = row.get("Classification")

            if classification == "":
                classification = "N/A"

            if classification not in classification_index:
                classification_index[classification] = []

            classification_index[classification].append(object_id)

            # add to reverse index
            reverse_index[object_id] = classification

        result = {
            "classification_index": classification_index,
            "reverse_index": reverse_index,
        }

        with open("../data/classification_index.json", "w") as f:
            json.dump(result, f, indent=4)

        return result


def validate_index():
    """
    Make sure we all database records are availabe in the index
    """

    api = MetAPI()
    # We need to convert the db ID's to strings so the matching will work
    all_db_records = set(str(x) for x in api.get_all_records())
    with open("../data/classification_index.json", "r") as f:
        data = json.load(f)

        all_local_records = set(data.get("reverse_index").keys())

        in_db_not_local = all_db_records - all_local_records
        in_local_not_db = all_local_records - all_db_records

        print(f"Records in DB: {len(all_db_records)}")
        print(f"Records in index: {len(all_local_records)}")
        print(f"In DB but not local: {len(in_db_not_local)}")
        print(f"In local but not DB: {len(in_local_not_db)}")


validate_index()
