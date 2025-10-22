import requests
from pprint import pprint

BASE_URL = "https://collectionapi.metmuseum.org"


all_records = requests.get(f"{BASE_URL}/public/collection/v1/objects")
pprint(all_records.json())

for record in all_records.json().get("objectIDs"):
    print(record)
