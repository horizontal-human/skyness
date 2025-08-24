import json
import requests
import time
import random
from math import inf

# --- Config ---

ACCESSORY_FILES = ["accessories_fixed.json"]

COFL_RECOMBO_PRICE = "https://sky.coflnet.com/api/bazaar/RECOMBOBULATOR_3000/snapshot"

# Magical Power per Rarity
magical_power = {
    "COMMON": 3,
    "UNCOMMON": 5,
    "RARE": 8,
    "EPIC": 12,
    "LEGENDARY": 16,
    "MYTHIC": 22,
    "SPECIAL": 3,
    "VERY SPECIAL": 5
}

# MP gained from recombobulating X rarity
recombobulate = {
    "COMMON": 2,
    "UNCOMMON": 3,
    "RARE": 4,
    "EPIC": 4,
    "LEGENDARY": 6,
    "MYTHIC": 0,
    "SPECIAL": 2,
    "VERY SPECIAL": 0
}


# --- Helpers ---

def polite_delay():
    """Random short sleep to avoid hammering APIs."""
    time.sleep(random.uniform(0.4, 0.8))


def fetch_recombobulator_price():
    try:
        resp = requests.get(COFL_RECOMBO_PRICE, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        price_per_unit = data.get("buyPrice")
        return float(price_per_unit) if price_per_unit else None
    except Exception as e:
        print(f"[ERROR] Failed to fetch Recombobulator 3000 price: {e}")
        return None
    finally:
        polite_delay()


def best_price_for_accessory(acc):
    # Return best available price (auction > craft > npc) or None.
    for k in ("auction_price", "craft_price", "npc_price"):
        v = acc.get(k)
        if v is not None:
            try:
                return float(v)
            except Exception:
                pass
    return None


# --- Main ---

def main():
    all_acc = []
    for fn in ACCESSORY_FILES:
        try:
            with open(fn, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    all_acc.extend(data)
        except FileNotFoundError:
            continue

    parsed = []
    for a in all_acc:
        price = best_price_for_accessory(a)
        if price is None:
            print(f"Failed to fetch price for {a.get('name','')}")
            continue

        rarity = a.get("rarity", "")
        mp = magical_power.get(rarity)
        if mp is None:
            print(f"Failed to fetch MP for {a.get('name','')}")
            continue

        coins_per_mp = price / mp if mp else inf
        parsed.append({
            "name": a.get("name"),
            "rarity": rarity,
            "price": price,
            "mp": mp,
            "coins_per_mp": coins_per_mp
        })

    # Sort by coins/MP ascending
    parsed.sort(key=lambda x: x["coins_per_mp"])

    recombo_price = fetch_recombobulator_price()

    # Per-rarity counters
    rarity_counts = {r: 0 for r in magical_power.keys()}

    final_output = []

    for item in parsed:
        name = item["name"]
        rarity = item["rarity"]
        price = int(item["price"])
        mp = item["mp"]
        cpp = int(item["coins_per_mp"])

        # Check recombobulation for each rarity separately
        if recombo_price is not None:
            for r, count in rarity_counts.items():
                if count > 0:
                    recomb_mp = recombobulate.get(r, 0)
                    if recomb_mp > 0:
                        recomb_cpp = recombo_price / recomb_mp
                        # If recombob is better than buying next cheapest
                        if item["coins_per_mp"] > recomb_cpp:
                            total_price = int(recombo_price * count)
                            total_mp = recomb_mp * count
                            coins_per_mp_total = int(total_price / total_mp) if total_mp else 0

                            # Plural for recombobulation name
                            plural = "ies" if count != 1 else "y"

                            recomb_to = ""

                            if r == "COMMON":
                                recomb_to = "UNCOMMON"
                            elif r == "UNCOMMON":
                                recomb_to = "RARE"
                            elif r == "RARE":
                                recomb_to = "EPIC"
                            elif r == "EPIC":
                                recomb_to = "LEGENDARY"
                            elif r == "LEGENDARY":
                                recomb_to = "MYTHIC"
                            elif r == "MYTHIC":
                                recomb_to = "SPECIAL"
                            elif r == "SPECIAL":
                                recomb_to = "VERY SPECIAL"

                            final_output.append({
                                "name": f"Recombobulate {count} {r} accessor{plural}",
                                "rarity": recomb_to,
                                "price": total_price,
                                "mp": total_mp,
                                "coinsPerMP": coins_per_mp_total
                            })

                            # Print recombobulation with accessory singular/plural
                            print(
                                f"Recombobulate {count} {r} accessor{plural} | "
                                f"{total_price} coins | {total_mp} MP | {coins_per_mp_total} coins/MP"
                            )

                            # Reset only THIS rarity counter
                            rarity_counts[r] = 0

        final_output.append({
            "name": name,
            "rarity": rarity,
            "price": price,
            "mp": mp,
            "coinsPerMP": cpp
        })

        # Print the accessory
        print(f"{name} | {price} coins | {mp} MP | {cpp} coins/MP")

        # Increment counter for its rarity
        rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1

    with open("accessory_plan.json", "w", encoding="utf-8") as fh:
        json.dump(final_output, fh, indent=4, ensure_ascii=False)

    print(f"Saved {len(final_output)} items to accessory_plan.json")

if __name__ == "__main__":
    main()
