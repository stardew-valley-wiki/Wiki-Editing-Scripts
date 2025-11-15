from src.ItemService import *


class Recipe:
    """配方类，存储配方名称、原料列表和产物

    Attributes:
        recipe_name: 配方的名称
        materials: 配方所需的原材料
        product: 配方产出的物品
    """

    def __init__(self, recipe_name: str, materials: list, product):
        self.recipe_name = recipe_name
        self.materials = materials
        self.product = product


class RecipeData:
    def __init__(self):
        self.cooking_recipes: dict[str, str] = {}
        self.crafting_recipes: dict[str, str] = {}
        self.cooking_recipe_objects: dict[str, Recipe] = {}  # 存储解析后的烹饪配方对象
        self.crafting_recipe_objects: dict[str, Recipe] = {}  # 存储解析后的制作配方对象
        self.ignore_recipes: list[str] = ["Transmute (Fe)", "Transmute (Au)"]  # 需要忽略拆解的配方列表
        # 类别映射
        self.negative_code_mapping = {
            "-4": "鱼类(任意)",
            "-5": "蛋类(任意)",
            "-6": "奶类(任意)",
            "-7": "油类(任意)",
            "-777": "季节种子(任意)",
        }

        json_path = Path(__file__).parent.parent / "json"
        self.crafting_recipes = FileUtils.read_json(json_path / "CraftingRecipes.json")
        self.cooking_recipes = FileUtils.read_json(json_path / "CookingRecipes.json")
        self._parse_all_recipes()

    def _parse_all_recipes(self):
        """解析所有配方"""
        # 解析烹饪配方
        for recipe_name, recipe_str in self.cooking_recipes.items():
            recipe = self._parse_recipe(recipe_name, recipe_str, is_crafting=False)
            self.cooking_recipe_objects[recipe_name] = recipe

        # 解析制作配方
        for recipe_name, recipe_str in self.crafting_recipes.items():
            recipe = self._parse_recipe(recipe_name, recipe_str, is_crafting=True)
            self.crafting_recipe_objects[recipe_name] = recipe

    def _parse_recipe(self, recipe_name: str, recipe_str: str, is_crafting: bool = False) -> Recipe:
        """解析单个配方"""
        # 分割配方字符串
        data = recipe_str.split("/")

        # 解析原料部分
        materials = []

        # 解析每个原料
        material_items = data[0].split()
        i = 0
        while i < len(material_items):
            # 检查是否是带括号的前缀
            if material_items[i].startswith("(") and ")" in material_items[i]:
                # 带前缀的情况
                if i + 1 < len(material_items) and material_items[i + 1].isdigit():
                    item_str = f"{material_items[i]} {material_items[i + 1]}"
                    i += 2
                else:
                    item_str = material_items[i]
                    i += 1
            else:
                # 检查下一个是否是数量
                if i + 1 < len(material_items) and material_items[i + 1].isdigit():
                    item_str = f"{material_items[i]} {material_items[i + 1]}"
                    i += 2
                else:
                    item_str = material_items[i]
                    i += 1

            materials.append(self._parse_item(item_str, is_prod=False))

        # 解析产物部分
        product_str = data[2]

        # 判断是否为BC
        is_bc = False
        if is_crafting and len(data) > 3:
            is_bc = data[3].lower() == "true"

        # 解析产物
        product = self._parse_item(product_str, is_prod=True, is_bc=is_bc)

        return Recipe(recipe_name, materials, product)

    def _parse_item(self, item_str: str, is_prod: bool = False, is_bc: bool = False) -> tuple | Object | BigCraftable:
        """解析物品代码为物品类"""

        # 分离代码和数量
        parts = item_str.split()
        if len(parts) == 2:
            code_part, count = parts[0], int(parts[1])
        else:
            code_part, count = parts[0], 1

        # 解析前缀和代码
        if is_prod:
            # 产物代码处理
            if is_bc:
                prefix = "(BC)"
            else:
                prefix = "(O)"
            code = code_part
        else:
            # 原料代码处理
            if code_part.startswith("-"):
                # 负数情况
                prefix = ""
                code = code_part
            elif code_part.startswith("(") and ")" in code_part:
                # 带括号前缀的情况
                match = re.match(r"\(([^)]+)\)(.+)", code_part)
                if match:
                    prefix = f"({match.group(1)})"
                    code = match.group(2)
                else:
                    prefix = "(O)"
                    code = code_part
            else:
                # 纯数字或英文
                prefix = "(O)"
                code = code_part

        qualified_id = prefix + code
        if qualified_id.startswith("-"):
            return self.negative_code_mapping[qualified_id], count
        elif qualified_id.startswith("(BC)"):
            item = game_data.try_get_bc(qualified_id)
            item.quantity = count
        else:
            item = game_data.try_get_object(qualified_id)
            item.quantity = count

        return item


def materials_to_string(materials: list[tuple | Object | BigCraftable]) -> str:
    out_string = ""
    for obj in materials:
        if type(obj) is tuple:
            out_string += f"{{{{Name|{obj[0]}|{obj[1]}}}}}"
        else:
            out_string += f"{{{{Name|{obj.name}|{obj.quantity}}}}}"
    return out_string


if __name__ != "__main__":
    recipe_data = RecipeData()
