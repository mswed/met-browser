import csv
import json
from pprint import pprint
from tqdm import tqdm


def build_classification_index(csv_path="../MetObjects.txt"):
    classification_index = {}
    reverse_index = {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in tqdm(reader):
            object_id = row.get("Object ID")
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


build_classification_index()
