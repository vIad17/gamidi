from hardware.akai_fire_controller import AkaiFireController
from PyQt6.QtCore import QCoreApplication, QTimer
from PIL import Image, ImageDraw, ImageFont
import sys, time

akai = None

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
CustomFont = ImageFont.truetype("Res/fonts/Mx437_Acer710_Mono.ttf", 14)

def IMG_DrawText(img: Image, text, x:int, y:int, white: bool = True):
  global CustomFont
  draw = ImageDraw.Draw(img)
  color = 1 if white else 0
  draw.text([x,y], text, color, CustomFont)

# QTimer.singleShot(500, lambda: OLED_OPEN_IMG("Res/VVAD.png", True))
#endregion OLED

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
  pressed_log_string(is_pressed, "Browser")
  akai.set_browser_led(is_pressed)

def on_select_button(is_pressed):
  pressed_log_string(is_pressed, "Select")

def on_grid_button(is_pressed, dir):
  pressed_log_string(is_pressed, "Grid "+ ("right"if dir==1 else "left"))
  akai.set_grid_led(dir, is_pressed)

def on_bank_button(is_pressed):
  pressed_log_string(is_pressed, "Bank")

def on_mute_button(is_pressed, ind):
  pressed_log_string(is_pressed, f"Mute {ind}")
  akai.set_mute_led(ind, is_pressed)


def on_pad_button(is_pressed, x, y):
  pressed_log_string(is_pressed, f"Pad X:{x:02d} Y:{y:02d}")
  col = 255 if is_pressed else 0
  akai.set_pad_color(x,y,col,col,col)

def on_control_change(index, value):
  print(f"{Fore.BLUE}[KNOB {index}] {value}")
   

def on_midi_button(index, pressed):
  if LOG_BUTTON_MIDI_ID: pressed_log_string(pressed, index)
#endregion Buttons


i = 0
tPadUpd = 0

anim_i = 0
tAnimFrame = 1

def AkaiUpdate(t, dt):
  global i, tPadUpd, tAnimFrame, anim_i

  if(t - tPadUpd > 50):
    tPadUpd = t
    akai.set_pad_color(i,3,0,0,0)
    akai.set_pad_color(i,1,0,0,0)
    akai.set_pad_color(15-i,0,0,0,0)
    akai.set_pad_color(15-i,2,0,0,0)
    akai.set_mute_status_led(i%4, False)
    i=(i+1)%16
    akai.set_pad_color(i,3,255,127,0)
    akai.set_pad_color(i,1,255,127,0)
    akai.set_pad_color(15-i,0,255,127,0)
    akai.set_pad_color(15-i,2,255,127,0)
    akai.set_mute_status_led(i%4, True)
    akai.set_preset_led(i%4)


  if(t-tAnimFrame > 40):
    tAnimFrame = t
    anim_i=((anim_i+1)%6572)+1

    img = IMG_empty(False)
    IMG_DrawProgress(img, val=(anim_i%100)/99, border=1, y= 40)
    IMG_DrawText(img, "Test string", 5, 20)
    # OLED_DRAW_IMG(img)
    OLED_OPEN_IMG(f"Res/Animation/BadApple/frame_{anim_i:05d}.png")