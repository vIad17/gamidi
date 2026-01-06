from PIL import Image, ImageDraw, ImageFont
from hardware.akai_fire_controller import AkaiFireController
import math
from typing import Type

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
  is_enemy = False
  is_projectile = False

  last_move_t = -100000

  attack_t = 1000
  last_atack_t = -10000

  sprite_path = ""
  color = [255, 255, 255]
  pxl_sprite_data = []
  
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

  def attackCheck(self,akai: AkaiFireController, t):
    global units
    if (t - self.last_atack_t > self.attack_t):
      tg_x = self.x + (1 if self.do_move else -1)
      for index, u in enumerate(units):
          if u.trySelect(tg_x, self.y) and (u.is_enemy != self.is_enemy):
            self.last_atack_t = t
            u.HP = u.HP - self.Dmg
            if u.HP<0: 
              akai.set_pad_color(tg_x, self.y, 0, 0, 0)
              units.remove(u)
              del(u)
            break

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
    self.attackCheck(akai, t)

    mul = 1
    if (math.floor(t/100)%2 == 0) and is_selected: mul = 0.3
    akai.set_pad_color(self.x,self.y, self.color[0]*mul, self.color[1]*mul, self.color[2]*mul)
  
  def trySelect(self, sel_x, sel_y) -> bool:
    return self.x == sel_x and self.y == sel_y

  def dist_to_enemy(self) -> int:
    global units
    dist = 90
    for index, u in enumerate(units):
      if u.is_enemy == self.is_enemy: continue 
      if u.is_projectile: continue
      if u.y != self.y: continue
      dist = min(dist, abs(self.x-u.x))
      if dist == 1: break
    return dist

units: list[Unit] = []

class UArrow(Unit):
  move_t = 600
  color = (180, 180, 180)
  MaxHP = 90000
  Dmg = 1
  is_projectile = True
  

  def trySelect(self, sel_x, sel_y):
    return False
  def drawTile(self, akai, is_selected, t):
    global units
    if self.last_move_t<0: self.last_move_t = t
    if t - self.last_move_t >= self.move_t:
      self.last_move_t = t
      akai.set_pad_color(self.x,self.y, 0,0,0)
      self.x = self.x - 1
      if self.x < 0:
        units.remove(self)
        del(self)
        return
    if self.attackCheck(akai, t): return

    mul = 1
    if (math.floor(t/30)%2 == 0): mul = 0.3
    akai.set_pad_color(self.x,self.y, self.color[0]*mul, self.color[1]*mul, self.color[2]*mul)

  def attackCheck(self, akai, t):
    for index, u in enumerate(units):
      if u.trySelect(self.x, self.y):
        if u.is_enemy:
          u.HP = u.HP - self.Dmg
          if u.HP<0: 
            akai.set_pad_color(self.x, self.y, 0, 0, 0)
            units.remove(u)
            del(u)
          units.remove(self)
          del(self)
          return True

class UMagic(UArrow):
  def attackCheck(self, akai, t):
    for index, u in enumerate(units):
      if u.trySelect(self.x, self.y):
        if u.is_enemy:
          akai.set_pad_color(self.x, self.y, 255, 0, 0)
          u.HP = u.HP - self.Dmg
          if u.HP<0: 
            akai.set_pad_color(self.x, self.y, 0, 0, 0)
            units.remove(u)
            del(u)
          for i in range(1,3):
            akai.set_pad_color(self.x-i, self.y, 255, 0, 0)
            for index, u2 in enumerate(units):
              if u2.trySelect(self.x-i, self.y):
                if u2.is_enemy:
                  u2.HP = u2.HP - self.Dmg
                  if u2.HP<0: 
                    akai.set_pad_color(self.x-i, self.y, 0, 0, 0)
                    units.remove(u2)
                    del(u2)
            akai.set_pad_color(self.x-i, self.y, 0, 0, 0)
          units.remove(self)
          del(self)
          return True


class UKnight(Unit):
  Name ="knight"
  color = (60, 255, 255)
  MaxHP = 3
  sprite_path = "Res/knights/unit_knight.png"

class UTower(Unit):
  Name ="Tower"
  color = (20, 35, 105)
  MaxHP = 10
  Dmg = 0
  sprite_path = "Res/knights/unit_tower.png"

class ULandman(Unit):
  Name ="Landman"
  color = (255, 255, 25)
  MaxHP = 1
  Dmg = 0
  sprite_path = "Res/knights/unit_landman.png"

class UArcher(Unit):
  Name ="Archer"
  color = (30, 150, 30)
  MaxHP = 3
  Dmg = 0
  attack_t = 4000
  sprite_path = "Res/knights/unit_archer.png"

  def attackCheck(self, akai, t):
    global units
    if (t - self.last_atack_t > self.attack_t):
      self.last_atack_t = t
      new_projectile = UArrow(self.x -1, self.y)
      units.append(new_projectile)


class UMage(Unit):
  Name ="Mage"
  color = (120, 30, 250)
  MaxHP = 3
  Dmg = 0
  attack_t = 6000
  sprite_path = "Res/knights/unit_mage.png"

  def attackCheck(self, akai, t):
    global units
    d = self.dist_to_enemy()
    if (d < 5):
      if (t - self.last_atack_t > self.attack_t):
        self.last_atack_t = t
        new_projectile = UMagic(self.x -1, self.y)
        units.append(new_projectile)



class UGoblin(Unit):
  is_enemy = True
  do_move = True
  move_t = 3000
  color = (255, 60, 255)
  sprite_path = "Res/knights/unit_knight.png"

class UAmogus(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 0, 0)
    sprite_path = "Res/enemies/IMG_Amogus.png"


class UAnt(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_ant.png"


class UBull(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_bull.png"


class UDolphin(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_dolphin.png"


class UDragon(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_dragon.png"


class UFireflies(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_fireflies.png"


class UFlame(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_flame.png"


class UFox(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_fox.png"


class UEye(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_eye.png"


class UJellyfish(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_jellyfish.png"


class USnake(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_snake.png"


class UTurtle(Unit):
    is_enemy = True
    do_move = True
    move_t = 3000
    color = (255, 153, 0)
    sprite_path = "Res/enemies/IMG_turtle.png"
  
unit_classes: dict[str, Type[Unit]] = {
    "Goblin": UGoblin,
    "Amogus": UAmogus,
    "Ant": UAnt,
    "Bull": UBull,
    "Dolphin": UDolphin,
    "Dragon": UDragon,
    "Fireflies": UFireflies,
    "Flame": UFlame,
    "Fox": UFox,
    "Eye": UEye,
    "Jellyfish": UJellyfish,
    "Snake": USnake,
    "Turtle": UTurtle,
}