
_started_time = -1000

GAME_LENGTH = 1000 * 60 * 0.1
current_game_time = 0
game_time_left = GAME_LENGTH

is_game_end = False
win_player_index = 1 #0 = Lauchpad; 1 = AKAI

request_restart = False


def restart():
  global _started_time, GAME_LENGTH, current_game_time, game_time_left, is_game_end, win_player_index, request_restart
  _started_time = -1000
  current_game_time = 0
  game_time_left = GAME_LENGTH

  is_game_end = False
  win_player_index = 1

  request_restart = True

def Update(t, dt):
  global _started_time, GAME_LENGTH, current_game_time, game_time_left, is_game_end, win_player_index
  if(_started_time<0): _started_time = t

  current_game_time = t - _started_time
  game_time_left = max(0, GAME_LENGTH-current_game_time)

  if(game_time_left <= 0) and not is_game_end:
    is_game_end = True
    win_player_index = 1
