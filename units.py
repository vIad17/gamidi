from PIL import Image, ImageDraw, ImageFont
from hardware.akai_fire_controller import AkaiFireController
import math

from AKAI_Main import OLED_OPEN_IMG, IMG_DrawProgress, IMG_DrawText,IMG_load

units = []
castleHP = 3


class Unit:
  Name = "Nonoame"
  MaxHP = 3
  Dmg = 1
  cost = 1
  move_t = 1000
  do_move = False

  last_move_t = -100000

  attack_t = 1000
  last_atack_t = -10000

  sprite_path = ""
  color = [255, 255, 255]
  def __init__(self, x, y):
    self.HP = self.MaxHP
    self.x = x
    self.y = y
    self.AKAI_Sprite = IMG_load(self.sprite_path)

  def generateSprite(self, data, name) -> Image:
    img = Image.new("1", (128, 64), 0)
    draw = ImageDraw.Draw(img)
    for i in data:
      x = (i%8)*4 +80
      y = (math.floor(i/8))*4 +13
      draw.rectangle([x,y,x+4,y+4], outline=1, fill=1, width=0)
    IMG_DrawText(img, name, 6, 6)
    self.AKAI_Sprite = img

  def drawIMG(self)-> Image.Image:
    if self.AKAI_Sprite is None:
      img = Image.new("1", (128, 64), 0)
    else:
      img = self.AKAI_Sprite.copy()

    draw = ImageDraw.Draw(img)
    for i in range(self.Dmg):
      x = 30+i*8
      y = 28
      draw.rectangle([x, y, x+5, y+5], outline=1, fill=1, width=0)
    for i in range(self.MaxHP):
      x = 30+i*8
      y = 38
      draw.rectangle([x, y, x+5, y+5], outline=1, fill=1, width=0)
    IMG_DrawProgress(img, self.HP/self.MaxHP, 8, 52, 70,3, 1)

    return img

  def drawTile(self, akai: AkaiFireController, is_selected: bool, t):
    global units, castleHP
    if self.do_move:
      if self.last_move_t<0: self.last_move_t = t
      if t - self.last_move_t >= self.move_t:
        self.last_move_t = t
        can_move = True
        for index, u in enumerate(units):
          if u.trySelect(self.x+1, self.y):
            can_move = False
            break
        if can_move:
          akai.set_pad_color(self.x,self.y, 0,0,0)
          self.x = self.x + 1
          if self.x >= 15:
            self.x = 15
            castleHP = castleHP - 1
            units.remove(self)
            del(self)
            return

    if (t - self.last_atack_t > self.attack_t):
      tg_x = self.x + (1 if self.do_move else -1)
      for index, u in enumerate(units):
          if u.trySelect(tg_x, self.y):
            self.last_atack_t = t
            u.HP = u.HP - self.Dmg
            if u.HP<0: 
              akai.set_pad_color(tg_x, self.y, 0, 0, 0)
              units.remove(u)
              del(u)
            break

    mul = 1
    if (math.floor(t/100)%2 == 0) and is_selected: mul = 0.3
    akai.set_pad_color(self.x,self.y, self.color[0]*mul, self.color[1]*mul, self.color[2]*mul)
  
  def trySelect(self, sel_x, sel_y) -> bool:
    return self.x == sel_x and self.y == sel_y


units: list[Unit] = []

class UKnight(Unit):
  Name ="knight"
  color = (60, 255, 255)
  MaxHP = 3
  sprite_path = "Res/knights/unit_knight.png"

class UTower(Unit):
  Name ="Tower"
  color = (20, 25, 75)
  MaxHP = 10
  Dmg = 0
  sprite_path = "Res/knights/unit_tower.png"

class ULandman(Unit):
  Name ="Tower"
  color = (255, 255, 25)
  MaxHP = 1
  Dmg = 0
  sprite_path = "Res/knights/unit_landman.png"

class UArcher(Unit):
  Name ="Archer"
  color = (255, 255, 25)
  MaxHP = 3
  Dmg = 2
  sprite_path = "Res/knights/unit_archer.png"


class UGoblin(Unit):
  do_move = True
  move_t = 3000
  color = (255, 60, 255)
  sprite_path = "Res/knights/unit_knight.png"

  
