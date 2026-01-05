from hardware.akai_fire_controller import AkaiFireController
from PyQt6.QtCore import QCoreApplication, QTimer
from PIL import Image, ImageDraw, ImageFont
import sys, time
from AKAI_Main import AKAIinit, AkaiUpdate
from Launchpad_Main import LaunchpadInit, LaunchpadMain
from enemies_logic.Drawer import Update, SpawnEnemy

from colorama import init, Fore, Style
init(autoreset=True)

app = QCoreApplication([])

AKAIinit()
# LaunchpadInit()

t_old = 0
t = time.time() * 1000
def MainGlobal():
  global t, t_old
  t_old = t
  t = time.time() * 1000
  dt = t-t_old
  AkaiUpdate(t,dt)
  # Update()



timer = QTimer()
timer.timeout.connect(MainGlobal)
timer.start(10)



sys.exit(app.exec())