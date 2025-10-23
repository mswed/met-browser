import requests
from pprint import pprint

BASE_URL = "https://collectionapi.metmuseum.org"


# all_records = requests.get(f"{BASE_URL}/public/collection/v1/objects")
#
# base_records = set(all_records.json().get("objectIDs"))
# total_records = all_records.json().get("total")

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
for letter in abc:
    all_search_records = requests.get(
        f"{BASE_URL}/public/collection/v1/search?q={letter}&hasImages=true"
    )

    found = all_search_records.json().get("objectIDs")
    for f in found:
        records.add(f)

records_list = list(records)
print("found", len(records_list), "records with images")
