import sys
import os
import math
import global_game_state as GameState

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

# import time

moving_line = -1
drawing_array = []
current_enemy: Enemy = None
default_enemy: Enemy = {
    "name": "Custom",
    "image": drawing_array,
    "color": COLOR_GREEN
}

def TimeTick():
  global lp
  segments_left = GameState.game_time_left/GameState.GAME_LENGTH * 8
  lp.LedCtrlXYByRGB(7, 0, _LerpColor(COLOR_GREEN, COLOR_BLACK, 1-max(segments_left - 7, 0)))
  lp.LedCtrlXYByRGB(6, 0, _LerpColor(COLOR_GREEN, COLOR_BLACK, 1-max(segments_left - 6, 0)))
  lp.LedCtrlXYByRGB(5, 0, _LerpColor(COLOR_GREEN, COLOR_BLACK, 1-max(segments_left - 5, 0)))
  lp.LedCtrlXYByRGB(4, 0, _LerpColor(COLOR_GREEN, COLOR_BLACK, 1-max(segments_left - 4, 0)))
  lp.LedCtrlXYByRGB(3, 0, _LerpColor(COLOR_GREEN, COLOR_BLACK, 1-max(segments_left - 3, 0)))
  lp.LedCtrlXYByRGB(2, 0, _LerpColor(COLOR_GREEN, COLOR_BLACK, 1-max(segments_left - 2, 0)))
  lp.LedCtrlXYByRGB(1, 0, _LerpColor(COLOR_GREEN, COLOR_BLACK, 1-max(segments_left - 1, 0)))
  lp.LedCtrlXYByRGB(0, 0, _LerpColor(COLOR_GREEN, COLOR_BLACK, 1-max(segments_left - 0, 0)))

def GameOver():
  lp.Reset()
  lp.LedCtrlString( "Game Over! Game Over! Game Over! Game Over! Game Over!", 255, 0, 0, -1, waitms = 50 )
  
def Win():
  lp.Reset()
  lp.LedCtrlString( "You win! You win! You win! You win! You win!", 0, 255, 0, -1, waitms = 50 )

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

def LaunchpadDrawerUpdate(t, dt):
  # print(t, dt)
  global lp, current_enemy, default_enemy, moving_line
  
  if GameState.is_game_end:
    if GameState.win_player_index == 0:
      Win()
    else:
      GameOver()
    return
  
  lp = GetLP()
  input = lp.ButtonStateRaw()
  _HandleInputs(input)

  if _IsEnemyReady() and moving_line != -1:
    _MoveToBattle(t, dt)
    return
  
  if not _IsEnemyReady() or (moving_line == -1 and current_enemy == default_enemy):
    _Draw(input)
  
  if _IsEnemyReady() and current_enemy != default_enemy and moving_line == -1:
    _Pulsing(t, dt)
    
  TimeTick()
  
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
      # print(enemy["image"])
      for index, value in enumerate(enemy["image"]):
        # print(deltaIdx, value - drawing_array[index])
        if deltaIdx != value - drawing_array[index]:
          break
        if index == len(enemy["image"]) - 1:
          current_enemy = enemy
          # for idx in drawing_array:
          #   # lp.LedCtrlXYByRGB(idx % 8, idx // 8 + 1, enemy["color"])
          #   lp.LedCtrlPulseXYByCode(idx % 8, idx // 8 + 1, 12)

def _HandleInputs(input):
  global lp, drawing_array, current_enemy, drawing_array, moving_line
  
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
      # if _IsEnemyReady():
        # SpawnEnemy(row_inputs.index(input[0]), current_enemy)
        # drawing_array.clear()
        # lp.Reset()
      if _IsEnemyReady():
        moving_line = row_inputs.index(input[0])
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

prev_t = 0
temp_img = []

prev_t = 0
temp_img = []

def _MoveToBattle(t, dt):
  global lp, current_enemy, prev_t, temp_img
  speed = 3
  cur_t = int(t * speed / 1000)

  if prev_t != cur_t:
    prev_t = cur_t

    # инициализируем temp_img один раз, в начале анимации
    if not temp_img:
      temp_img = drawing_array.copy()

    for i, idx in enumerate(temp_img):
      lp.LedCtrlXYByRGB(idx % 8, idx // 8 + 1, COLOR_BLACK)
      if idx % 8 + 1 < 8:
        temp_img[i] += 1
      else:
        temp_img[i] = -1

    temp_img = [idx for idx in temp_img if idx != -1]

    for idx in temp_img:
      lp.LedCtrlXYByRGB(idx % 8, idx // 8 + 1, current_enemy["color"])

    if not temp_img:
      SpawnEnemy(moving_line, current_enemy)
      temp_img = []
      
def _Pulsing(t, dt):
  global current_enemy, lp
  speed = 7
  lerp_value = (math.sin(t/1000*speed) + 1)/2
  print(lerp_value)
  for idx in drawing_array:
    lp.LedCtrlXYByRGB(idx % 8, idx // 8 + 1, _LerpColor(_LerpColor(current_enemy["color"], COLOR_BLACK, 0.4), _LerpColor(current_enemy["color"], COLOR_BLACK, 0.9), lerp_value))

def FadeIn():
  pass

def _Lerp(a: float, b: float, t: float) -> int:
  return int((1 - t) * a + t * b)

def ease_in_out_cubic(a: float, b: float, t: float) -> int:
    eased_t = math.sin((t * math.pi) / 2)
    return int(a + (b - a) * eased_t)

def _LerpColor(a: list[int], b: list[int], t: float):
  return [_Lerp(a[0], b[0], t), _Lerp(a[1], b[1], t), _Lerp(a[2], b[2], t)]

def _EasingColor(a: list[int], b: list[int], t: float):
  return [ease_in_out_cubic(a[0], b[0], t), ease_in_out_cubic(a[1], b[1], t), ease_in_out_cubic(a[2], b[2], t)]


def _IsEnemyReady():
  global drawing_array
  return len(drawing_array) > 5

from AKAI_Main import OnEnemySpawn

def SpawnEnemy(row: int, enemy: Enemy):
  global moving_line, current_enemy, default_enemy
  OnEnemySpawn(row, enemy)
  print("Enemy has spawned in line " + str(row))
  print(enemy)
  
  drawing_array.clear()
  current_enemy = default_enemy
  moving_line = -1
  