from src.ShopService import *


def get_infobox(weapon_id, weapon_data) -> str:
    """生成 Infobox weapon 并打印"""
    name: str = weapon_data.get("DisplayName")
    eng: str = weapon_data.get("Name")
    wtype: str = weapon_data.get("Type")
    level: int = weapon_data.get("Level")
    damage: str = weapon_data.get("Damage")
    csc: str = weapon_data.get("CritChance")
    csm: str = weapon_data.get("CritMultiplier")
    price: int = get_shop_price(weapon_id)
    sellprice: int = weapon_data.get("SellPrice")
    stats: str = stats_to_string(weapon_data.get("Statistics"))

    infobox = f"""<onlyinclude>{{{{{{{{{{1|Infobox weapon}}}}}}
|name            = {name}
|eng             = {eng}
|source          = 
|type            = {wtype}
|level           = {level}
|damage          = {damage}
|csc             = {csc}
|csm             = {csm}
|price           = {price}
|sellprice       = {sellprice}
|stats           = {stats}
}}}}</onlyinclude>
"""

    return (infobox
            .replace("|csc             = \n", "")
            .replace("|csm             = \n", "")
            .replace("|stats           = \n", ""))


def get_shop_price(code: str) -> int | None:
    shop: ShopData = ShopManager().adventure_guild
    for good in shop.goods:
        if good.id == code:
            return good.price
    return -1


def stats_to_string(stats: dict[str, str | None]) -> str:
    out_string = ""
    for attr, value in stats.items():
        if value is None:
            continue
        attr = attr.replace("Crit", "Crit. ").replace("Speed", "Speed w")
        out_string += f"{{{{Name|{attr}|{value}}}}}"
    return out_string


if __name__ == "__main__":
    ...
