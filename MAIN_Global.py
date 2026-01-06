from hardware.akai_fire_controller import AkaiFireController
from PyQt6.QtCore import QCoreApplication, QTimer
from PIL import Image, ImageDraw, ImageFont
import sys, time
from AKAI_Main import AKAIinit, AkaiUpdate, AkaiRestart
from Launchpad_Main import LaunchpadInit, LaunchpadMain
from enemies_logic.Drawer import LaunchpadDrawerUpdate, LaunchpadDrawerInit, SpawnEnemy, LaunchpadRestart

from colorama import init, Fore, Style

import global_game_state as GameState

init(autoreset=True)

app = QCoreApplication([])

AKAIinit()
LaunchpadInit()
LaunchpadDrawerInit()

t_old = 0
t = time.time() * 1000
def MainGlobal():
  global t, t_old
  t_old = t
  t = time.time() * 1000
  dt = t-t_old

  if(GameState.request_restart):
    GameState.request_restart = False
    LaunchpadRestart()
    AkaiRestart()

  GameState.Update(t,dt)
  AkaiUpdate(t,dt)
  LaunchpadDrawerUpdate(t, dt)



timer = QTimer()
timer.timeout.connect(MainGlobal)
timer.start(1)



sys.exit(app.exec())