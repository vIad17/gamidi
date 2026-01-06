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
    "color": [150, 48, 48],
  },
  {
    "name" : "Bull",
    "image": ReadFromFile("bull"),
    "color": [201, 25, 22],
  },
  {
    "name" : "Dolphin",
    "image": ReadFromFile("dolphin"),
    "color": [69, 165, 255],
  },
  {
    "name" : "Dragon",
    "image": ReadFromFile("dragon"),
    "color": [255, 0, 0],
  },
  {
    "name" : "Fireflies",
    "image": ReadFromFile("fireflies"),
    "color": [59, 255, 235],
  },
  {
    "name" : "Flame",
    "image": ReadFromFile("flame"),
    "color": [255, 89, 89],
  },
  {
    "name" : "Fox",
    "image": ReadFromFile("fox"),
    "color": [255, 102, 0],
  },
  {
    "name" : "Eye",
    "image": ReadFromFile("eye"),
    "color": [191, 0, 255],
  },
  {
    "name" : "Jellyfish",
    "image": ReadFromFile("jellyfish"),
    "color": [0, 183, 255],
  },
  {
    "name" : "Snake",
    "image": ReadFromFile("snake"),
    "color": [0, 255, 102],
  },
  {
    "name" : "Turtle",
    "image": ReadFromFile("turtle"),
    "color": [0, 255, 13],
  }
]