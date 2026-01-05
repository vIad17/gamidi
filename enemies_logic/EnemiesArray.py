from enemies_logic.FileReader import ReadFromFile
from typing import TypedDict, List

class Enemy(TypedDict):
    image: List[int]
    hp: int
    speed: int
    color: List[int]

enemies: List[Enemy] = [
  {
    "image": ReadFromFile("enemy1"),
    "hp": 1,
    "speed": 1,
    "color": [255, 0, 0]
  },
  {
    "image": ReadFromFile("enemy2"),
    "hp": 1,
    "speed": 1,
    "color": [255, 153, 0]
  }
]