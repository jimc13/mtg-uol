import json
import random

def get_mtgjson_data(set_id):
    with open(f"mtgjson/{set_id.upper()}.json", encoding="utf-8") as f:
        return json.load(f)

def generate_pack(mtgjson_data):
    pack = []
    pack_data = mtgjson_data["data"]["booster"]["default"]
    boosters = pack_data["boosters"]
    sheets = random.choices(boosters, [booster["weight"] for booster in boosters])[0]["contents"]
    for sheet, card_count in sheets.items():
        sheet_cards = pack_data["sheets"][sheet]["cards"]
        # np and random choice will return duplicate picks when k > 1
        # np and random sample do not support weights
        # add card ids to a set until the required number have been added
        sheet_picks = set()
        while len(sheet_picks) < card_count:
            cards = list(sheet_cards.keys())
            weights = list(sheet_cards.values())
            sheet_picks.add(random.choices(cards, weights)[0])

        # TODO: check if pack contains all colors
        pack += sheet_picks

    names = []
    for mtgjson_id in pack:
        card_data_list = list(filter(lambda x: x["uuid"] == mtgjson_id, mtgjson_data["data"]["cards"]))
        assert len(card_data_list) == 1
        card_data = card_data_list[0]
        names.append(card_data["name"])

    return names

def main():
    mtgjson_data = {}
    players = 10
    pools = ("A", "B")
    packs = ["znr"] * 6
    players_pools = {}
    for player in range(players):
        for pool in pools:
            for set_id in packs:
                if set_id not in mtgjson_data:
                    mtgjson_data[set_id] = get_mtgjson_data(set_id)

                if not player in players_pools:
                    players_pools[player] = {}

                if not pool in players_pools[player]:
                    players_pools[player][pool] = []

                players_pools[player][pool] += generate_pack(mtgjson_data[set_id])

    with open("export.csv", "w") as f:
        pool_string = ",Pool ".join(pools)
        f.write(f"Player, Pool {pool_string}\n")
        for player, pool in players_pools.items():
            row = str(player)
            for pool_name, pool in pool.items():
                cards = "\n".join(pool)
                row += f',"{cards}"'

            f.write(f"{row}\n")

if __name__ == "__main__":
    main()
