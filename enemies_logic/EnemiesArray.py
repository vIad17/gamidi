from enemies_logic.FileReader import ReadFromFile
from typing import List, TypedDict
# from units import Unit

class Enemy(TypedDict):
    image: List[int]
    hp: int
    speed: int
    color: List[int]

enemies: List[Enemy] = [
  {
    "name" : "Amogus",
    "image": ReadFromFile("amogus"),
    "color": [255, 0, 0],
  },
  {
    "name" : "Ant",
    "image": ReadFromFile("ant"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Bull",
    "image": ReadFromFile("bull"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Dolphin",
    "image": ReadFromFile("dolphin"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Dragon",
    "image": ReadFromFile("dragon"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Fireflies",
    "image": ReadFromFile("fireflies"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Flame",
    "image": ReadFromFile("flame"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Fox",
    "image": ReadFromFile("fox"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Eye",
    "image": ReadFromFile("eye"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Jellyfish",
    "image": ReadFromFile("jellyfish"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Snake",
    "image": ReadFromFile("snake"),
    "color": [255, 153, 0],
  },
  {
    "name" : "Turtle",
    "image": ReadFromFile("turtle"),
    "color": [255, 153, 0],
  }
]