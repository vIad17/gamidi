from enemies_logic.FileReader import ReadFromFile
from typing import List, TypedDict
from units import Unit

class Enemy(TypedDict):
    image: List[int]
    hp: int
    speed: int
    color: List[int]

enemies: List[Enemy] = [
  {
    "Name" : "Amogus",
    "image": ReadFromFile("amogus"),
    "color": [255, 0, 0],
  },
  {
    "name" : "Square",
    "image": ReadFromFile("square"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Fox",
    "image": ReadFromFile("fox"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Ant",
    "image": ReadFromFile("ant"),
    "color": [255, 153, 0],
  }
]