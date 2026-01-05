import sys

try:
	import launchpad_py as launchpad
except ImportError as e:
	print("Failed to import launchpad_py:", e)
	sys.exit("error loading launchpad_py")

import random
import time

lp = None
mode = None


def LaunchpadInit():
  global lp, mode

	# create an instance for the Pro
  if launchpad.LaunchpadPro().Check( 0 ):
    lp = launchpad.LaunchpadPro()
    if lp.Open( 0 ):
      print("Launchpad Pro")
      mode = "Pro"

  elif launchpad.LaunchpadProMk3().Check( 0 ):
    lp = launchpad.LaunchpadProMk3()
    if lp.Open( 0 ):
      print("Launchpad Pro Mk3")
      mode = "ProMk3"

  # experimental MK3 implementation
  # The MK3 has two MIDI instances per device; we need the 2nd one.
  # If you have two MK3s attached, its "1" for the first and "3" for the 2nd device
  elif launchpad.LaunchpadMiniMk3().Check( 1 ):
    lp = launchpad.LaunchpadMiniMk3()
    if lp.Open( 1, "minimk3" ):
      print("Launchpad Mini Mk3")
      mode = "Pro"

  # experimental LPX implementation
  # Like the Mk3, the LPX also has two MIDI instances per device; we need the 2nd one.
  # If you have two LPXs attached, its "1" for the first and "3" for the 2nd device
  elif launchpad.LaunchpadLPX().Check( 1 ):
    lp = launchpad.LaunchpadLPX()
    if lp.Open( 1, "lpx" ):
      print("Launchpad X")
      mode = "Pro"
      
  elif launchpad.LaunchpadMk2().Check( 0 ):
    lp = launchpad.LaunchpadMk2()
    if lp.Open( 0, "mk2" ):
      print("Launchpad Mk2")
      mode = "Mk2"

  elif launchpad.LaunchControlXL().Check( 0 ):
    lp = launchpad.LaunchControlXL()
    if lp.Open( 0, "control xl" ):
      print("Launch Control XL")
      mode = "XL"
      
  elif launchpad.LaunchKeyMini().Check( 0 ):
    lp = launchpad.LaunchKeyMini()
    if lp.Open( 0, "launchkey" ):
      print("LaunchKey (Mini)")
      mode = "LKM"

  elif launchpad.Dicer().Check( 0 ):
    lp = launchpad.Dicer()
    if lp.Open( 0, "dicer" ):
      print("Dicer")
      mode = "Dcr"

  elif launchpad.MidiFighter64().Check( 0 ):
    lp = launchpad.MidiFighter64()
    if lp.Open( 0 ):
      print("Midi Fighter 64")
      mode = "MF64"

  else:
    lp = launchpad.Launchpad()
    if lp.Open():
      print("Launchpad Mk1/S/Mini")
      mode = "Mk1"

  if mode is None:
    print("Did not find any Launchpads, meh...")
    return


x = 5
y = 5	
x_delta = 0
y_delta = 0
is_snake_eat_apple = False
is_game_over = False

apple = [random.randint(0,7), random.randint(1, 8)]

snake = [[3, 5], [4, 5], [5, 5], [6, 5]]
 	
def LaunchpadMain(t, dt):
  global lp, x, y, x_delta, y_delta, is_snake_eat_apple, is_game_over, snake, apple
  time.sleep(0.6)
  lp.Reset()

  if snake[0][0] < 0 or snake[0][0] > 7 or snake[0][1] < 1 or snake[0][1] > 8:
    is_game_over = True

  x = x + x_delta
  y = y + y_delta

  input = lp.ButtonStateRaw()
  if input != []:
    if input[0] == 94 and x_delta != -1:
      x_delta = 1
      y_delta = 0
  
    if input[0] == 93 and x_delta != 1:
      x_delta = -1
      y_delta = 0
    if input[0] == 92 and y_delta != -1:
      x_delta = 0
      y_delta = 1
    if input[0] == 91 and y_delta != 1:
      x_delta = 0
      y_delta = -1
  y_delta = 0
  if snake[0] == apple:
    is_snake_eat_apple = True
    snake.append([-1,-1])
    apple = [random.randint(0,7), random.randint(1, 8)]

  for i in reversed(range(1, len(snake))):
    if (snake[0] == snake[i]):
      is_game_over = True
  
    if x_delta != 0 or y_delta != 0:
      if is_snake_eat_apple and i == (len(snake) - 1):
        is_snake_eat_apple = False
      else:
        snake[i][0] = snake[i-1][0]
        snake[i][1] = snake[i-1][1]
    print(i, snake[i])
  
    lp.LedCtrlXYByCode(snake[i][0], snake[i][1], 17)

  snake[0][0] += x_delta
  snake[0][1] += y_delta
  lp.LedCtrlXYByCode(snake[0][0], snake[0][1], 25)
  print(snake)

  lp.LedCtrlXYByCode(apple[0], apple[1], 60)

  # lp.LedCtrlXYByCode(0, 1, 60)

  if is_game_over:
    pass


# Gameover
# lp.LedCtrlString( "Game Over!", 0, 63, 0, -1, waitms = 50 )

# print("Quitting might raise a 'Bad Pointer' error (~almost~ nothing to worry about...:).\n\n")

# lp.Reset()
# lp.Close()

	
