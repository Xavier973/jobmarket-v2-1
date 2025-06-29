import os
import json
import re

INPUT_DIR = "/home/ubuntu/jobmarket-v2-1/data/transformed/wttj/"

def extract_wttj_reference(link):
    if not isinstance(link, str):
        return None
    # On cherche la partie entre '/companies/' et le prochain '?', ou la fin du lien
    match = re.search(r"/companies/([^?]+)", link)
    if match:
        return match.group(1)
    return None

def add_reference_to_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    for entry in data:
        link = entry.get("link", "")
        ref = extract_wttj_reference(link)
        entry["wttj_reference"] = ref
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(INPUT_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        print(f"Traitement de : {filename}")
        add_reference_to_file(filepath)
    print("Ajout des références terminé.")

if __name__ == "__main__":
    main() 