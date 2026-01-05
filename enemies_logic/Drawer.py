import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

COLOR_GREEN = [0, 255, 0]
COLOR_BLACK = [0, 0, 0]
COLOR_WHITE = [255, 255, 255]

BUTTON_CLEAR = 89
BUTTON_ROW_3 = 19
BUTTON_ROW_2 = 29
BUTTON_ROW_1 = 39
BUTTON_ROW_0 = 49

from Launchpad_Main import LaunchpadInit, GetLP
from enemies_logic.EnemiesArray import enemies, Enemy
from enemies_logic.FileReader import ReadFromFile

from AKAI_Main import OnEnemySpawn
# import time

drawing_array = []
current_enemy: Enemy = None
default_enemy: Enemy = {
    "image": drawing_array,
    "hp": 1,
    "speed": 1,
    "color": COLOR_GREEN
}

def IdToIndex(id : int):
  return (8 - id//10) * 8 + id%10 - 1

def IndexToId(index : int):
  return (8 - index//8) * 10 + index%8 +1

def LaunchpadDrawerInit():
  global lp
  lp = GetLP()
  lp.Reset()
  lp.LedCtrlXYByRGB(8, 1, COLOR_WHITE)
  lp.LedCtrlXYByRGB(8, 5, COLOR_WHITE)
  lp.LedCtrlXYByRGB(8, 6, COLOR_WHITE)
  lp.LedCtrlXYByRGB(8, 7, COLOR_WHITE)
  lp.LedCtrlXYByRGB(8, 8, COLOR_WHITE)

def LaunchpadDrawerUpdate():
  global lp
  lp = GetLP()
  input = lp.ButtonStateRaw()
  _HandleInputs(input)
  _Draw(input)
  
def _Draw(input):
  global lp, drawing_array, enemies, current_enemy
  
  if input == [] or input[1] == 0 or input[0] % 10 > 8:
    return
  
  selected_index = IdToIndex(input[0])
  if selected_index in drawing_array:
    drawing_array.remove(selected_index)
    lp.LedCtrlXYByCode(selected_index % 8, selected_index // 8 + 1, 0)
  else:
    drawing_array.append(selected_index)
  
  drawing_array.sort()

  color = [0, 255, 0] if _IsEnemyReady() else [255, 255, 255]
  for idx in drawing_array:
    lp.LedCtrlXYByRGB(idx % 8, idx // 8 + 1, color)
  
  if _IsEnemyReady():
    current_enemy = default_enemy
    for enemy in enemies:      
      if len(enemy["image"]) != len(drawing_array):
        continue
      
      deltaIdx = enemy["image"][0] - drawing_array[0]
      print(enemy["image"])
      for index, value in enumerate(enemy["image"]):
        print(deltaIdx, value - drawing_array[index])
        if deltaIdx != value - drawing_array[index]:
          break
        if index == len(enemy["image"]) - 1:
          current_enemy = enemy
          for idx in drawing_array:
            lp.LedCtrlXYByRGB(idx % 8, idx // 8 + 1, enemy["color"])

def _HandleInputs(input):
  global lp, drawing_array, current_enemy, drawing_array
  
  if input == []:
    return
  
  lp.LedCtrlXYByRGB(8, 1, COLOR_WHITE)  
  
  if input[0] == BUTTON_CLEAR:
    # color = COLOR_WHITE
    if input[1] != 0:
      drawing_array.clear()
      lp.Reset()
      lp.LedCtrlXYByRGB(8, 1, COLOR_BLACK)
      # color = COLOR_BLACK
    # print(color)
    # lp.LedCtrlXYByRGB(8, 1, color)
  
  # if input[1] != 0:
  #   print(input)
  
  lp.LedCtrlXYByRGB(8, 5, COLOR_WHITE)
  lp.LedCtrlXYByRGB(8, 6, COLOR_WHITE)
  lp.LedCtrlXYByRGB(8, 7, COLOR_WHITE)
  lp.LedCtrlXYByRGB(8, 8, COLOR_WHITE)
  
  row_inputs = [BUTTON_ROW_0, BUTTON_ROW_1, BUTTON_ROW_2, BUTTON_ROW_3]
  if input[0] in row_inputs:
    if input[1] != 0:
      if _IsEnemyReady():
        SpawnEnemy(row_inputs.index(input[0]), current_enemy)
        drawing_array.clear()
        lp.Reset()
      lp.LedCtrlXYByRGB(8, 5, COLOR_WHITE if input[0] != BUTTON_ROW_0 else COLOR_BLACK)
      lp.LedCtrlXYByRGB(8, 6, COLOR_WHITE if input[0] != BUTTON_ROW_1 else COLOR_BLACK)
      lp.LedCtrlXYByRGB(8, 7, COLOR_WHITE if input[0] != BUTTON_ROW_2 else COLOR_BLACK)
      lp.LedCtrlXYByRGB(8, 8, COLOR_WHITE if input[0] != BUTTON_ROW_3 else COLOR_BLACK)
      lp.LedCtrlXYByRGB(8, 1, COLOR_WHITE)
    # else:
    #   lp.LedCtrlXYByRGB(8, 5, COLOR_WHITE)
    #   lp.LedCtrlXYByRGB(8, 6, COLOR_WHITE)
    #   lp.LedCtrlXYByRGB(8, 7, COLOR_WHITE)
    #   lp.LedCtrlXYByRGB(8, 8, COLOR_WHITE)
        

def _IsEnemyReady():
  global drawing_array
  return len(drawing_array) > 5

def SpawnEnemy(row: int, enemy: Enemy):
  # OnEnemySpawn(row, enemy)
  print("Enemy has spawned in line " + str(row))
  print(enemy)