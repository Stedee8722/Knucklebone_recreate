import os
import json

DATA_FOLDER = "Data"
LOG_FOLDER = "Logs"

for filename in os.listdir(DATA_FOLDER):
    if filename.endswith(".json"):
        filepath = os.path.join(DATA_FOLDER, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)
            print(f"✔ Cleared {filename}")
        except Exception as e:
            print(f"❌ Failed to clear {filename}: {e}")

for filename in os.listdir(LOG_FOLDER):
    if filename.endswith(".log"):
        filepath = os.path.join(LOG_FOLDER, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)
            print(f"✔ Cleared {filename}")
        except Exception as e:
            print(f"❌ Failed to clear {filename}: {e}")

# Thanks GPT