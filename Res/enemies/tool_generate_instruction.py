from pathlib import Path
from PIL import Image, ImageDraw

CELL_SIZE = 32                # pixels per square
BG_COLOR = (255, 255, 255)    # background color (white)
FG_COLOR = (0, 0, 0)          # filled square color (black)
GRID_COLOR = (200, 200, 200)  # gray grid lines

EMPTY_CHAR = '.'
FILLED_CHAR = '*'
ALLOWED_CHARS = {EMPTY_CHAR, FILLED_CHAR}

def load_text(txt_path: Path) -> str | None:
    encodings_to_try = [
        "utf-8",
        "utf-8-sig",
        "utf-16",
        "utf-16le",
        "utf-16be",
        "latin-1",
    ]

    for enc in encodings_to_try:
        try:
            return txt_path.read_text(encoding=enc)
        except UnicodeError:
            continue

    print(f"[SKIP] {txt_path} – cannot decode with {encodings_to_try}")
    return None

def parse_pattern(txt_path: Path):
    text = load_text(txt_path)
    if text is None:
        return None

    raw_lines = [line.rstrip("\r\n") for line in text.splitlines() if line.strip() != ""]
    if len(raw_lines) != 8:
        print(f"[SKIP] {txt_path} – expected 8 non-empty lines, got {len(raw_lines)}")
        return None

    for i, row in enumerate(raw_lines):
        if len(row) != 8:
            print(f"[SKIP] {txt_path} – line {i+1} length {len(row)} != 8")
            return None

    for i, row in enumerate(raw_lines):
        for j, ch in enumerate(row):
            if ch not in ALLOWED_CHARS:
                print(f"[SKIP] {txt_path} – unexpected char {ch!r} at ({i+1},{j+1})")
                return None

    return raw_lines

def pattern_to_png(lines, out_path: Path):
    height = len(lines)       # 8
    width = len(lines[0])     # 8

    img_w = width * CELL_SIZE
    img_h = height * CELL_SIZE

    img = Image.new("RGB", (img_w, img_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # draw filled cells
    for y, row in enumerate(lines):
        for x, ch in enumerate(row):
            if ch == FILLED_CHAR:
                x0 = x * CELL_SIZE
                y0 = y * CELL_SIZE
                x1 = x0 + CELL_SIZE - 1
                y1 = y0 + CELL_SIZE - 1
                draw.rectangle([x0, y0, x1, y1], fill=FG_COLOR)

    # draw grid lines on top
    # vertical lines
    for i in range(width + 1):
        x = i * CELL_SIZE
        draw.line([(x, 0), (x, img_h - 1)], fill=GRID_COLOR)

    # horizontal lines
    for j in range(height + 1):
        y = j * CELL_SIZE
        draw.line([(0, y), (img_w - 1, y)], fill=GRID_COLOR)

    img.save(out_path)
    print(f"[OK]  {out_path}")

def txt_to_png(txt_path: Path):
    lines = parse_pattern(txt_path)
    if lines is None:
        return
    out_path = txt_path.with_suffix(".png")
    pattern_to_png(lines, out_path)

def main():
    root = Path(".")
    for txt_path in root.rglob("*.txt"):
        txt_to_png(txt_path)

if __name__ == "__main__":
    main()
