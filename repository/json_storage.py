import json
import os


class JsonStorage:

    def save(self, repo, base_name):

        os.makedirs("output", exist_ok=True)

        path = f"output/{base_name}.json"

        with open(path, "w", encoding="utf-8") as f:
            json.dump(repo, f, indent=4)

        print("Saved ->", path)