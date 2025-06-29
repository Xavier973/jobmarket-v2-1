FILEPATH = "/home/ubuntu/jobmarket-v2-1/data/transformed/wttj/wttj_2025-06-27_02_clean.json"  # À modifier selon le fichier à traiter

import json

def remove_duplicates(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    seen = set()
    unique_data = []
    for entry in data:
        ref = entry.get("wttj_reference")
        if ref and ref not in seen:
            seen.add(ref)
            unique_data.append(entry)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=2)
    print(f"Doublons supprimés. Nombre d'annonces uniques : {len(unique_data)}")

def main():
    remove_duplicates(FILEPATH)

if __name__ == "__main__":
    main() 