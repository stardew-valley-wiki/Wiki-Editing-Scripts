from src.RecipeService import *


def generate_infobox() -> None:
    """生成 Infobox craft 并打印"""
    recipes = recipe_data.crafting_recipe_objects

    for recipe_name, recipe_info in recipes.items():
        product: Object | BigCraftable = recipe_info.product
        eng = recipe_name
        name = game_data.get_display_name(product.itemID)
        sellprice = product.get_field("Price")
        produces = product.quantity if int(product.quantity) > 1 else ""
        ingredients = materials_to_string(recipe_info.materials)

        infobox = f"""{name}：\n
<onlyinclude>{{{{{{{{{{1|Infobox craft}}}}}}
|name            = {name}
|eng             = {eng}
|description     = {{{{Description|{eng}}}}}
|source          = [[打造]]
|sellprice       = {sellprice}
|recipe          = ---------- 配方来源，这里要自己填 ----------
|ingredients     = {ingredients}
|produces        = {produces}
}}}}</onlyinclude>
'''{name}'''是一种[[打造|打造物品]]，\n"""
        print(infobox)


if __name__ == "__main__":
    generate_infobox()
