import json

# File to clean
INPUT_FILE = "accessories.json"
OUTPUT_FILE = "accessories_clean.json"

# Accessories to remove (by name)
REMOVE_NAMES = {
    "Combo Mania",
    "Argofay Trinket",
    "Master Skull - Tier 8",
    "Master Skull - Tier 9",
    "Master Skull - Tier 10",
    "Talisman of Space",
    "Ring of Space",
    "Artifact of Space",
    "Bingo Heirloom",
    "Old Boot",
    "Luck Talisman",
    "Cracked Piggy Bank",
    "Broken Piggy Bank",
    "Compass Talisman",
    "Grizzly Paw",
    "Punchcard Artifact",
    "Warding Trinket",
    "Harmonious Surgery Toolkit",
    "Celestial Starstone",
    "Crux Relic",
    "Crux Artifact",
    "Crux Ring",
    "Crux Heirloom",
    "Crux Talisman",
    "Crux Chronomicon",
    "Defective Monitor",
    "Satelite",
    "Perma-Jelled Garlic-Flavored Re-Heated Gummy Polar Bear",
    "Eternal Crystal"
}

def clean_accessories():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        accessories = json.load(f)

    before_count = len(accessories)
    filtered = [acc for acc in accessories if acc["name"] not in REMOVE_NAMES]
    after_count = len(filtered)

    removed = before_count - after_count
    print(f"Removed {removed} accessories.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)

    print(f"Cleaned list saved to {OUTPUT_FILE} with {after_count} accessories.")

if __name__ == "__main__":
    clean_accessories()

# Soulbound accessories
SOULBOUND_NAMES = {
    "Archaeologist's Compass",
    "Sloth Hat of Celebration",
    "Crab Hat of Celebration - 2022 Edition",
    "Crab Hat of Celebration",
    "Odger's Bronze Tooth",
    "Odger's Silver Tooth",
    "Odger's Gold Tooth",
    "Odger's Diamond Tooth",
    "Shady Ring",
    "Crooked Artifact",
    "Seal of the Family",
    "Cat Talisman",
    "Lynx Talisman",
    "Cheetah Talisman",
    "Pig's Foot",
    "Wolf Paw",
    "Frozen Chicken",
    "King Talisman",
    "Book of Progression",
    "Survivor Cube",
    "Jake's Plushie",
    "IQ Point",
    "2 IQ Points",
    "Tiny Dancer",
    "Test Bucket Please Ignore",
    "Big Brain Talisman",
    "Miniaturized Tubulator",
    "Melody's Hair",
    "Kuudra Follower Relic",
    "Kuudra Follower Artifact",
    "Melody's Hair",
    "Soul Campfire Initiate Badge I",
    "Soul Campfire Adept Badge I",
    "Soul Campfire Cultist Badge I",
    "Soul Campfire Scion Badge I",
    "Soul Campfire God Badge I",
    "Campfire Initiate Badge I",
    "Campfire Adept Badge I",
    "Campfire Cultist Badge I",
    "Campfire Scion Badge I",
    "Campfire God Badge I",
    "Ring of Broken Love",
    "Ring of Eternal Love",
    "Rubbish Ring of Love",
    "§eYellow Rock of Love",
    "Classy Ring of Love",
    "Exquisite Ring of Love",
    "Modest Ring of Love",
    "Mediocre Ring of Love",
    "§eShiny Yellow Rock",
    "Invaluable Ring of Love",
    "Refined Ring of Love",
    "Legendary Ring of Love",
    "Future Calories Talisman",
    "Talisman of Power",
    "Relic of Power",
    "Artifact of Power",
    "Personal Deletor 4000",
    "Personal Deletor 5000",
    "Personal Deletor 6000",
    "Personal Deletor 7000"
}

def move_soulbound():
    # Load the cleaned accessories file
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        accessories = json.load(f)

    soulbound = [acc for acc in accessories if acc["name"] in SOULBOUND_NAMES]
    remaining = [acc for acc in accessories if acc["name"] not in SOULBOUND_NAMES]

    print(f"Moving {len(soulbound)} soulbound accessories into accessories_soulbound.json")

    # Save soulbound accessories to a new file
    with open("accessories_soulbound.json", "w", encoding="utf-8") as f:
        json.dump(soulbound, f, indent=2, ensure_ascii=False)

    # Overwrite the cleaned file without the soulbound ones
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(remaining, f, indent=2, ensure_ascii=False)

    print(f"Updated {OUTPUT_FILE} with {len(remaining)} accessories after removing soulbound.")

def remove_special_names():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        accessories = json.load(f)

    filtered = [
        acc for acc in accessories
        if "Campfire" not in acc["name"]
        and "Ring of" not in acc["name"]
        and "Yellow Rock" not in acc["name"]
    ]

    removed_count = len(accessories) - len(filtered)
    print(f"Removed {removed_count} accessories containing 'Campfire', 'Ring of', or 'Yellow Rock'.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)

def remove_campfire_from_clean():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        accessories = json.load(f)

    filtered = [acc for acc in accessories if "Campfire" not in acc["name"]]

    removed_count = len(accessories) - len(filtered)
    print(f"Removed {removed_count} accessories containing 'Campfire' from {OUTPUT_FILE}.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    clean_accessories()
    move_soulbound()
    remove_special_names()
    remove_campfire_from_clean()
