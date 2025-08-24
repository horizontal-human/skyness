import json
import requests
import time
import random
from statistics import median

# --- Config ---

COFL_LOWEST_BIN = "https://sky.coflnet.com/api/item/lowestbin/{}"
COFL_RECENT_OVERVIEW = "https://sky.coflnet.com/api/auctions/tag/{}/recent/overview"
COFL_AUCTION_DETAILS = "https://sky.coflnet.com/api/auction/{}"

INPUT_FILE = "accessories_clean.json"
OUTPUT_FILE = "accessories_fixed.json"


# --- Helpers ---

def polite_delay():
    """Random short sleep to avoid hammering APIs."""
    time.sleep(random.uniform(0.4, 0.8))


def fetch_sold_auctions(item_id, rarity, max_matches=5):
    """
    Find recent auction prices for item_id with the desired rarity.
    Returns the median of up to `max_matches` matching sales.
    """
    url = COFL_RECENT_OVERVIEW.format(item_id)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        matched_prices = []

        for entry in data:
            auction_id = entry.get("uuid")
            if not auction_id:
                continue

            try:
                # fetch full auction details
                detail_url = COFL_AUCTION_DETAILS.format(auction_id)
                d_resp = requests.get(detail_url, timeout=15)
                d_resp.raise_for_status()
                auction_data = d_resp.json()

                # rarity comes from "tier"
                auction_rarity = (
                    auction_data.get("item", {}).get("tier")
                    or auction_data.get("tier")
                )

                if auction_rarity and auction_rarity.upper() == rarity.upper():
                    matched_prices.append(int(entry["price"]))
                    print(f"[MATCH] {item_id} {rarity} sold for {entry['price']}")

                    if len(matched_prices) >= max_matches:
                        break

            except Exception as e:
                print(f"[DETAIL ERROR] {auction_id}: {e}")

            polite_delay()

        if matched_prices:
            return int(median(matched_prices))

    except Exception as e:
        print(f"[FETCH SOLD ERROR] {item_id} {rarity}: {e}")

    return None


def fetch_cofl_median(item_id):
    """Fetch the median of the last 3 sales from CoflNet."""
    url = COFL_RECENT_OVERVIEW.format(item_id)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if not data or "price" not in data[0]:
            return None
        last_prices = [entry["price"] for entry in data[:3] if "price" in entry]
        if last_prices:
            return int(median(last_prices))
    except Exception as e:
        print(f"[COFL MEDIAN ERROR] {item_id}: {e}")
    return None


def fetch_price(item_id, name):
    """Try CoflNet BIN, then CoflNet recent median."""
    if item_id is None:
        return None

    item_id = str(item_id)  # ensure always string
    price = None

    # Try recent sales median
    price = fetch_cofl_median(item_id)
    polite_delay()
    if price:
        return price

    print(f"[WARN] No price found anywhere for {name}")
    return None

# --- Fix Missing Prices ---

def fix_missing_prices():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        accessories = json.load(f)

    updated = []

    for acc in accessories:
        name = acc.get("name")
        item_id = acc.get("id")
        rarity = acc.get("rarity")

        # --- Default rarity to COMMON if missing ---
        if not rarity:
            acc["rarity"] = "COMMON"
            print(f"[FIX] {name} had no rarity, set to COMMON")

        needs_price = not acc.get("auction_price") and not acc.get("craft_price") and not acc.get("npc_price")

        # --- Hardcoded NPC prices ---
        if name in ["Scavenger Talisman", "Mine Affinity Talisman", "Village Affinity Talisman",
                    "Intimidation Talisman"]:
            acc["npc_price"] = 200
            print(f"[FIX] {name} set NPC=200")
            updated.append(acc)
            continue
        if name in ["Skeleton Talisman", "Zombie Talisman"]:
            acc["npc_price"] = 50
            print(f"[FIX] {name} set NPC=50")
            updated.append(acc)
            continue
        if name == "Jacobus Register":
            acc["npc_price"] = 21_500_000
            print(f"[FIX] Jacobus Register set NPC=21,500,000")
            updated.append(acc)
            continue

        # --- Fried Frozen Chicken special case ---
        if name == "Fried Frozen Chicken":
            recipe = {
                "FRIED_FEATHER": 256,
                "ENCHANTED_GLACITE": 128,
                "ENCHANTED_BLAZE_POWDER": 128
            }
            craft_price = 0
            for ingredient, qty in recipe.items():
                try:
                    url = f"https://sky.coflnet.com/api/bazaar/{ingredient}/snapshot"
                    resp = requests.get(url, timeout=15)
                    resp.raise_for_status()
                    data = resp.json()
                    price_per_unit = data.get("buyPrice")
                    if price_per_unit:
                        craft_price += price_per_unit * qty
                        print(f"[FRIED CHICKEN] {ingredient} x{qty} = {price_per_unit * qty}")
                    else:
                        print(f"[WARN] No buyPrice for {ingredient}")
                except Exception as e:
                    print(f"[ERROR] Failed to fetch {ingredient} price: {e}")
                polite_delay()
            acc["craft_price"] = int(craft_price)
            print(f"[FIX] Fried Frozen Chicken craft_price = {int(craft_price)}")
            updated.append(acc)
            continue

        # --- Runebook special case ---
        if name == "Runebook":
            rarities = ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
            for r in rarities:
                clone = dict(acc)
                clone["rarity"] = r
                price = fetch_sold_auctions(str(item_id), r)  # <--- new function
                if price:
                    clone["auction_price"] = price
                    print(f"[FIX] Runebook ({r}) price={price}")
                else:
                    print(f"[WARN] No recent sales found for Runebook ({r})")
                updated.append(clone)
                polite_delay()
            continue

        # --- Abicase special case ---
        if name == "Abicase":
            samsung_id = "ABICASE_SUMSUNG_1"
            url = COFL_RECENT_OVERVIEW.format(samsung_id)
            try:
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                data = resp.json()
                last_prices = [entry["price"] for entry in data[:3] if "price" in entry]
                if last_prices:
                    median_price = int(median(last_prices))
                    acc["auction_price"] = median_price
                    print(f"[FIX] Samsung Abicase median of last 3 sales = {median_price}")
                else:
                    print(f"[WARN] No recent sales found for Samsung Abicase")
            except Exception as e:
                print(f"[COFL MEDIAN ERROR] Samsung Abicase: {e}")
            updated.append(acc)
            continue

        # --- General case ---
        if needs_price:
            price = fetch_price(item_id, name)
            if price:
                acc["auction_price"] = price
                print(f"[PRICE] {name} = {price}")
            else:
                print(f"[WARN] Still no price for {name}")

        updated.append(acc)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2, ensure_ascii=False)

    print(f"✅ Fixed prices saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    fix_missing_prices()
