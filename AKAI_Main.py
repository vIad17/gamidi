from hardware.akai_fire_controller import AkaiFireController
from PyQt6.QtCore import QCoreApplication, QTimer
from PIL import Image, ImageDraw, ImageFont
import sys, time
import math

from colorama import init as ColoramaINIT
from colorama import Fore, Style
ColoramaINIT(autoreset=True)


akai = None

select_x, select_y = -1,-1

def AKAIinit():
  global akai
  #region: Controller connection
  akai = AkaiFireController(None, True)
  print("Akai status:",str(akai.is_connected()))
  print("Available INPUT ports:", AkaiFireController.get_available_input_ports())
  in_ports = AkaiFireController.get_available_input_ports()
  fire_index = next(
      (i for i, name in enumerate(in_ports) if "fire" in name.lower()), None
  )
  if fire_index is None:
      print(Fore.RED +"No INPUT port found")
  else:
      akai.connect_input(in_ports[fire_index])
      print("Using input port:", in_ports[fire_index])
  print("Akai input status:",str(akai.is_input_connected()))

  akai.rec_button_event.connect(on_rec_button)
  akai.stop_button_event.connect(on_stop_button)
  akai.play_button_event.connect(on_play_button)
  akai.metronome_button_event.connect(on_metronome_button)

  akai.alt_button_event.connect(on_alt_button)
  akai.shift_button_event.connect(on_shift_button)
  akai.perform_button_event.connect(on_perform_button)
  akai.drum_button_event.connect(on_drum_button)
  akai.note_button_event.connect(on_note_button)
  akai.step_button_event.connect(on_step_button)

  akai.buttom_row_buttons_event.connect(on_bottom_row)

  akai.pattern_button_event.connect(on_pattern_button)
  akai.browser_button_event.connect(on_browser_button)
  akai.select_button_event.connect(on_select_button)
  akai.grid_button_event.connect(on_grid_button)

  akai.bank_button_event.connect(on_bank_button)

  akai.mute_button_event.connect(on_mute_button)
  akai.pad_button_event.connect(on_pad_button)

  akai.fire_button_event.connect(on_midi_button)
  akai.control_change_event.connect(on_control_change)

  akai.set_global_brightness_factor(1.0)
  #endregion: Controller connection

#region OLED
OLED_WIDTH = 128
OLED_HEIGHT = 64
def pack_pil_image_to_7bit_stream(pil_image: Image.Image) -> bytearray:
    if pil_image.mode != "1" or pil_image.size != (OLED_WIDTH, OLED_HEIGHT):
        raise ValueError("Image must be mode '1' and size 128x64")

    pixels = pil_image.load()

    def pixel_accessor(x, y):
        return pixels[x, y] != 0  # non-zero = "lit" pixel

    packed_stream = bytearray(1176)

    a_bit_mutate = [
        [13, 19, 25, 31, 37, 43, 49],
        [0, 20, 26, 32, 38, 44, 50],
        [1, 7, 27, 33, 39, 45, 51],
        [2, 8, 14, 34, 40, 46, 52],
        [3, 9, 15, 21, 41, 47, 53],
        [4, 10, 16, 22, 28, 48, 54],
        [5, 11, 17, 23, 29, 35, 55],
        [6, 12, 18, 24, 30, 36, 42],
    ]

    for y_coord in range(OLED_HEIGHT):
        for x_coord in range(OLED_WIDTH):
            if not pixel_accessor(x_coord, y_coord):
                continue

            fire_col = x_coord + OLED_WIDTH * (y_coord // 8)
            fire_y = y_coord % 8

            k = a_bit_mutate[fire_y][fire_col % 7]
            group_offset = (fire_col // 7) * 8
            byte_offset = k // 7
            bit_in_byte = k % 7

            packed_idx = group_offset + byte_offset
            if 0 <= packed_idx < len(packed_stream):
                packed_stream[packed_idx] |= (1 << bit_in_byte)

    return packed_stream

def OLED_DRAW_IMG(img: Image):
  packed = pack_pil_image_to_7bit_stream(img)
  akai.oled_send_full_bitmap(packed)

def OLED_OPEN_IMG(path, log=False):
  img = Image.open(path)
  img = img.convert("1")
  img = img.resize((128, 64))
  OLED_DRAW_IMG(img)
  if log: print(Fore.LIGHTBLACK_EX +"[IMAGE]", path)



def IMG_empty(white: bool = False):
  color = 1 if white else 0
  return Image.new("1", (OLED_WIDTH, OLED_HEIGHT), color)

def IMG_load(path):
  img = None
  if(path != ""):
    img = Image.open(path)
    img = img.convert("1")
    img = img.resize((128, 64))
  else:
    img = IMG_empty()
  return img

def IMG_DrawProgress(img: Image, val: float, x: int = 4, y: int = 52, w: int = 60, h: int = 3, border: int = 1):
  fill_w = float(w) * val
  draw = ImageDraw.Draw(img)

  left = x-border
  top = y-border
  right = x + w+border
  bottom = y + h+border
  rect = [left, top, right, bottom]
  draw.rectangle(rect, outline=1, fill=0, width=border)
  draw.rectangle([left, top, x+int(fill_w), bottom], outline=1, fill=1, width=0)

# CustomFont = ImageFont.load_default()
# CustomFont = ImageFont.truetype("Res/fonts/Mx437_IBM_EGA_8x14.ttf", 8)
CustomFont = ImageFont.truetype("Res/fonts/ARIAL.TTF", 16)
# CustomFont = ImageFont.truetype("Res/fonts/Mx437_Acer710_Mono.ttf", 14)

def IMG_DrawText(img: Image, text, x:int, y:int, white: bool = True):
  global CustomFont
  draw = ImageDraw.Draw(img)
  color = 1 if white else 0
  draw.text([x,y], text, color, CustomFont)

# QTimer.singleShot(500, lambda: OLED_OPEN_IMG("Res/VVAD.png", True))
#endregion OLED

import units as units_logic
from units import *
from shop import *


selected_unit = -1

mana_value = 0
mana_max_value = 12
last_mana_t = 0

is_shop_open = False
is_placing_unit = False
shop_item_i = 0
shop_items: list[shopEntry] = [
    ShopLandman(),
    ShopKnight(),
    ShopTower(),
    ShopArcher(),
    ShopMage()]
unit_to_place = None

#region Buttons
LOG_BUTTONS = True
LOG_BUTTON_MIDI_ID = False

def pressed_log_string(is_pressed, bt_name):
  if LOG_BUTTONS: 
    print((Fore.LIGHTBLUE_EX + "[PRESSED]") if is_pressed 
      else (Fore.MAGENTA +  "[RELEASE]"), bt_name)
  

def on_rec_button(is_pressed):
  pressed_log_string(is_pressed, "Rec")

def on_stop_button(is_pressed):
  pressed_log_string(is_pressed, "Stop")

def on_play_button(is_pressed):
  pressed_log_string(is_pressed, "Play")

def on_metronome_button(is_pressed):
  pressed_log_string(is_pressed, "Metronome")


def on_alt_button(is_pressed):
  pressed_log_string(is_pressed, "Alt")

def on_shift_button(is_pressed):
  pressed_log_string(is_pressed, "Shift")

def on_perform_button(is_pressed):
  pressed_log_string(is_pressed, "Perform")

def on_drum_button(is_pressed):
  pressed_log_string(is_pressed, "Drum")

def on_note_button(is_pressed):
  pressed_log_string(is_pressed, "Note")

def on_step_button(is_pressed):
  pressed_log_string(is_pressed, "Step")

def on_bottom_row(is_pressed, ind):
  akai.set_bottom_row_led(ind, is_pressed, False)

def on_pattern_button(is_pressed, dir):
  pressed_log_string(is_pressed, "Pattern "+ ("up"if dir==1 else "down"))
  akai.set_pattern_led(dir, is_pressed)

def on_browser_button(is_pressed):
  global is_shop_open
  pressed_log_string(is_pressed, "Browser")
  if is_pressed:
    is_shop_open = not is_shop_open
    akai.set_browser_led(is_shop_open)

def on_select_button(is_pressed):
  global shop_item_i,shop_items, unit_to_place, is_placing_unit, is_shop_open, mana_value
  pressed_log_string(is_pressed, "Select")
  if(is_pressed and is_shop_open):
    if mana_value-shop_items[shop_item_i].cost < 0:
      # TODO ADD MESSAGE
      return
    else:
      unit_to_place = shop_items[shop_item_i].unit_class
      mana_value = mana_value - shop_items[shop_item_i].cost
      is_placing_unit = True
      is_shop_open = False
    akai.set_browser_led(is_shop_open)
    

def on_grid_button(is_pressed, dir):
  global shop_item_i,shop_items
  pressed_log_string(is_pressed, "Grid "+ ("right"if dir==1 else "left"))
  akai.set_grid_led(dir, is_pressed)
  if(is_pressed):
    shop_item_i = (shop_item_i + dir) % len(shop_items)


def on_bank_button(is_pressed):
  pressed_log_string(is_pressed, "Bank")

def on_mute_button(is_pressed, ind):
  pressed_log_string(is_pressed, f"Mute {ind}")
  akai.set_mute_led(ind, is_pressed)


def on_pad_button(is_pressed, x, y):
  global select_x, select_y, selected_unit, is_shop_open
  global is_placing_unit, units, unit_to_place
  pressed_log_string(is_pressed, f"Pad X:{x:02d} Y:{y:02d}")
  col = 255 if is_pressed else 0
  akai.set_pad_color(x,y,col,col,col)
  if is_pressed:
    if is_placing_unit:
      if x<4: return
      if x==15: return
      for index, u in enumerate(units):
        if u.trySelect(x,y):
          return
      new_unit = unit_to_place(x,y)
      is_placing_unit = False
      unit_to_place = None
      units.append(new_unit)
    else:
      for index, u in enumerate(units):
        if u.trySelect(x,y):
          selected_unit = index
          is_shop_open = False
          akai.set_browser_led(is_shop_open)
      select_x = x
      select_y = y

def on_control_change(index, value):
  global shop_item_i,shop_items
  print(f"{Fore.BLUE}[KNOB {index}] {value}")
  if(index==4):
    shop_item_i = (shop_item_i + value) % len(shop_items)

def on_midi_button(index, pressed):
  if LOG_BUTTON_MIDI_ID: pressed_log_string(pressed, index)
#endregion Buttons

from enemies_logic.EnemiesArray import *

def OnEnemySpawn(row: int, enemy):
    global units
    unit_class = unit_classes.get(enemy["Name"])

    print(enemy["Name"])
    print(unit_class)

    if unit_class == None:
      return
    new_unit = unit_class(0, row)
    units.append(new_unit)


def DrawManaUpdate(mana: int):
  for i in range(6):
    akai.set_bottom_row_led(i, mana-2 >= i*2 -1, False, mana-2 >= i*2)

def DrawHpUpdate(hp: int):
  for i in range(6,10):
    akai.set_bottom_row_led(i, hp>=(i-5))

anim_i = 0
tAnimFrame = 1

# knight = UKnight(5, 1)
units.append(UKnight(5, 1))
units.append(UMage(13, 2))
units.append(UKnight(7, 2))
units.append(UGoblin(0, 2))
units.append(UGoblin(1, 2))
units.append(UGoblin(2, 2))
units.append(UGoblin(3, 2))
units.append(UGoblin(3, 3))
units.append(UTower(8, 3))

def AkaiUpdate(t, dt):
  global i, tPadUpd, tAnimFrame, anim_i, akai
  global select_x, select_y, units
  global mana_value, last_mana_t
  global is_placing_unit, is_shop_open, shop_items, shop_item_i

  num_landman = 0
  for index, u in enumerate(units):
    if u.__class__ == ULandman: num_landman = num_landman+1

  
  # print(5000 - 300*min(num_landman,15))

  if(t-last_mana_t > (5000 - 300*min(num_landman,15))):
    last_mana_t = t
    mana_value = min(mana_value+1, mana_max_value)

  if (is_shop_open and math.floor(t/200)%2==0):
    DrawManaUpdate(mana_value - shop_items[shop_item_i].cost)
    if(mana_value - shop_items[shop_item_i].cost < 0): akai.set_bottom_row_led(0,True,True,True)
  else:
    DrawManaUpdate(mana_value)

  akai.set_pad_color(15,0, 0, 255*(units_logic.castleHP/3),0)
  akai.set_pad_color(15,1, 0, 255*(units_logic.castleHP/3),0)
  akai.set_pad_color(15,2, 0, 255*(units_logic.castleHP/3),0)
  akai.set_pad_color(15,3, 0, 255*(units_logic.castleHP/3),0)
  DrawHpUpdate(units_logic.castleHP)


  if(t-tAnimFrame > 40):
    tAnimFrame = t
    anim_i=((anim_i+1)%6572)+1

    
    # IMG_DrawProgress(img, val=(anim_i%100)/99, border=1, y= 40)
    # IMG_DrawText(img, "Test string", 5, 20)
    # OLED_DRAW_IMG(img)
    # OLED_OPEN_IMG(f"Res/Animation/BadApple/frame_{anim_i:05d}.png")
    # OLED_OPEN_IMG(f"Res/knights/unit_knight.png")
  
  img = IMG_empty(False)
  for index, u in enumerate(units):
    u.drawTile(akai, selected_unit == index, t)
    if(selected_unit == index):
      img = u.drawIMG()

  
  if(is_shop_open):
    img = IMG_empty(False)
    img = IMG_load(shop_items[shop_item_i].img_path)

  if(is_placing_unit):
    img = IMG_empty(False)
    IMG_DrawText(img, "Разместите\nюнит", 5, 15)
    pass
    # akai.set_pad_color(select_x,select_y, 0,0,0)

  OLED_DRAW_IMG(img)

