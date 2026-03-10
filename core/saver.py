import os
import json
from config import OUTPUT_DIR


def save_repo(repo, base_name):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_path = f"{OUTPUT_DIR}/{base_name}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(repo, f, indent=4)

    print("Saved ->", file_path)