import random
import time
from src.api.met_api import MetAPI
from src.api.classification_index import ClassificationIndex


def sample_classification_images(classification, sample_size=100):
    """Sample objects to estimate % with images"""
    index = ClassificationIndex()
    api = MetAPI()

    object_ids = index.get_records_in_classification(classification)

    if len(object_ids) < sample_size:
        sample_size = len(object_ids)

    # Random sample
    sample_ids = random.sample(object_ids, sample_size)

    with_images = 0
    for obj_id in sample_ids:
        obj_data = api.get_single_record(int(obj_id))
        if obj_data and obj_data.get("primaryImage"):
            with_images += 1

    try:
        percentage = (with_images / sample_size) * 100

        print(f"\n{classification}:")
        print(f"  Sample size: {sample_size}")
        print(f"  With images: {with_images}")
        print(f"  Percentage: {percentage:.1f}%")
        print(
            f"  To get 80 with images, fetch ~{int(80 / (with_images / sample_size))} objects"
        )
    except ZeroDivisionError:
        print("No images found for", classification)
        percentage = 0

    return percentage


# Test a few classifications
classifications = ["Paintings", "Prints", "Sculptures", "Photographs"]

for classification in classifications:
    sample_classification_images(classification, sample_size=50)
    time.sleep(60)
