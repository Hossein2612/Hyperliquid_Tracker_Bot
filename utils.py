import json
import os
import time

def load_wallets(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_wallets(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def diff_positions(old, new):
    diffs = []
    old_map = {p["coin"]: p for p in old}
    new_map = {p["coin"]: p for p in new}

    for coin, new_pos in new_map.items():
        if coin not in old_map:
            diffs.append({"type": "open", **new_pos})
        elif new_pos["szi"] != old_map[coin]["szi"]:
            diffs.append({"type": "modify", "old": old_map[coin], "new": new_pos})

    for coin in old_map:
        if coin not in new_map:
            diffs.append({"type": "close", **old_map[coin]})

    return diffs

def format_position(wallet, change):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    if change["type"] == "open":
        return f"🚀 *New Position Opened*\nWallet: `{wallet}`\nCoin: {change['coin']}\nSide: {'Long' if change['side'] == 'L' else 'Short'}\nSize: {change['szi']}\nEntry: {change['entryPx']}\nLiq: {change.get('liqPx', 'N/A')}\nTime: {t}"
    elif change["type"] == "close":
        return f"💥 *Position Closed*\nWallet: `{wallet}`\nCoin: {change['coin']}\nSize: {change['szi']}\nTime: {t}"
    elif change["type"] == "modify":
        return f"🔁 *Position Modified*\nWallet: `{wallet}`\nCoin: {change['new']['coin']}\nSize: {change['old']['szi']} → {change['new']['szi']}\nTime: {t}"
