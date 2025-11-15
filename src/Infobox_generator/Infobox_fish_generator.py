from src.ItemService import *


class Fish:
    """
    存储鱼类数据的类

    Attributes:
        info: 解析 Fish.json 得到的原始数据列表
        time: 出没的时间
        season: 出没的季节
        weather: 出没的天气
        difficulty: 难度
        behavior: 行为类型
        size: 尺寸
        fl: 钓鱼等级要求
    """
    def __init__(self, data: str) -> None:
        self.info: list[str] = data.split("/")
        self.time: str = "any"
        self.season: str = "any"
        self.weather: str = "any"
        self.difficulty: str = "0"
        self.behavior: str = "0"
        self.fl: str = "0"

        if len(self.info) == 14:
            self.time = self._get_clock(self.info[5])
            self.season = self._get_season(self.info[6])
            self.weather = self.info[7].replace("both", "any")
            self.difficulty = self.info[1]
            self.behavior = self.info[2]
            self.size = f"{self.info[3]}-{int(self.info[4]) + 1}"
            self.fl = self.info[-2]
        else:
            self.size = f"{self.info[5]}-{self.info[6]}"

    @staticmethod
    def _get_season(seasons: str) -> str:
        """
        将原始季节数据转化为 media wiki 格式
        :param seasons: 季节的纯文本信息
        :return: mw 规格化后的季节信息
        """
        if seasons == "spring summer fall winter":
            return "all"

        seasons = seasons.split(" ")
        if len(seasons) == 1:
            return seasons[0]

        desc = ""
        for season in seasons:
            desc = desc + "{{Season|" + season + "}} • "
        return desc[:-3]

    @staticmethod
    def _get_clock(timerange: str) -> str:
        """
        将原始时间数据转化为标准格式
        :param timerange: 时间的纯文本信息
        :return: 规格化后的季节信息
        """
        if timerange == "600 2600":
            return "any"
        times = ""
        timerange = timerange.split(" ")
        for i in range(0, len(timerange), 2):
            time1 = int((int(timerange[i]) / 100)) % 24
            time2 = int((int(timerange[i + 1]) / 100)) % 24
            times += f"{time1}:00 至 {time2}:00<br/>"

        return times[:-5]


def generate_infobox() -> None:
    """生成 Infobox fish 并打印"""
    objects = game_data.objects_data
    fishes = game_data.fish_data

    for object_id, object_data in objects.items():
        item = Object(object_data, object_id)

        if item.get_field("Category") != -4:
            continue

        eng = item.name
        name = game_data.get_display_name(object_id)
        sellprice = item.sellprice
        edibility = item.edibility
        color = item.color.title()
        fish = Fish(fishes[object_id])

        infobox = f"""{name}：\n
<onlyinclude>{{{{{{{{{{1|Infobox fish}}}}}}
|name       = {name}
|eng        = {eng}
|location   = 
|time       = {fish.time}
|season     = {fish.season}
|weather    = {fish.weather}
|difficulty = {fish.difficulty}
|behavior   = {fish.behavior}
|size       = {fish.size}
|fl         = {fish.fl}
|sellprice  = {sellprice}
|edibility  = {edibility}
|color      = {color}
}}}}</onlyinclude>\n\n"""

        infobox = (infobox.replace("|fl         = 0\n", ""))

        print(infobox)


if __name__ == "__main__":
    generate_infobox()
