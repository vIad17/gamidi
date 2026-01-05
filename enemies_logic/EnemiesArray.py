from enemies_logic.FileReader import ReadFromFile
from typing import List
from units import Unit

class Enemy(TypedDict):
    image: List[int]
    hp: int
    speed: int
    color: List[int]

enemies: List[Enemy] = [
  {
    "Name" : "Goblin",
    "image": ReadFromFile("enemy1"),
    "color": [255, 0, 0],
  },
  {
    "name" : "GoblinB",
    "image": ReadFromFile("enemy2"),
    "color": [255, 153, 0],
  }
]