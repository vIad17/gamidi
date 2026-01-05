from PIL import Image, ImageDraw, ImageFont
from units import *
from typing import Type


class shopEntry:
  cost = 1
  img_path = ""
  unit_class: Type[Unit] | None = None

class ShopKnight(shopEntry):
  cost = 4
  img_path = "Res/knights/unit_knight.png"
  unit_class = UKnight

class ShopTower(shopEntry):
    cost = 8          # примерная цена, подправь под баланс
    img_path = "Res/knights/unit_tower.png"
    unit_class = UTower

class ShopLandman(shopEntry):
    cost = 2
    img_path = "Res/knights/unit_landman.png"
    unit_class = ULandman

class ShopArcher(shopEntry):
    cost = 5
    img_path = "Res/knights/unit_archer.png"
    unit_class = UArcher


