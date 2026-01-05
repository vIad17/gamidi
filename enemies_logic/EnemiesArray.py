from enemies_logic.FileReader import ReadFromFile
from typing import List
from units import Unit

enemies: List[Unit] = [
    Unit(
      "amogus", # Name
      30, # MaxHP
      10, # Dmg
      1000, # move_t
      True, # do_move
      1000, # attack_t
      ReadFromFile("amogus"), # pxl_sprite_data
      "amogus", # txt_path
      [255, 0, 0] # color
    ),
    Unit(
      "square", # Name
      3, # MaxHP
      1, # Dmg
      1000, # move_t
      True, # do_move
      1000, # attack_t
      "", # sprite_path
      ReadFromFile("square"), # pxl_sprite_data
      [255, 255, 0] # color
    ),
]