
FILE_PATH = "Res/enemies/"

def ReadFromFile(enemy_name: str):
  with open(FILE_PATH + enemy_name + ".txt") as file:
    content = list(file.read())
    arr = []
    line_num = 0
    for i, c in enumerate(content):
      if c == '\n':
        line_num+=1
      if c == '*':
        arr.append(i - line_num)
    return arr