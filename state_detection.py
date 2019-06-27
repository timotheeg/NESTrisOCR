from PIL import Image, ImageDraw
import math

STAGE_BLOCK_WIDTH = 10
STAGE_BLOCK_HEIGHT = 20

img = Image.open('assets/das_trainer_sprites/Z.png')

stage_x = 221
stage_y = 92
stage_width = 182
stage_height = 319

stage = img.crop((stage_x, stage_y, stage_x + stage_width, stage_y + stage_height))
stage_bw = stage.copy().convert('L')
stage_bw = stage_bw.load()

block_size_w = stage.width / STAGE_BLOCK_WIDTH
block_size_h = stage.height / STAGE_BLOCK_HEIGHT

offset_x = block_size_w * 0.5
offset_y = block_size_h * 0.5

red = (255, 0, 0, 255)

stage_data = [[0 for i in range(STAGE_BLOCK_WIDTH)] for j in range(STAGE_BLOCK_HEIGHT)]

poly = Image.new('RGBA', (img.width, img.height))
draw = ImageDraw.Draw(poly)

for i in range(STAGE_BLOCK_WIDTH):
	for l in range(STAGE_BLOCK_HEIGHT):
		x = round(offset_x + block_size_w * i)
		y = round(offset_y + block_size_h * l)

		area = (x, y, x, y) # ony need to read one pixel!
		draw.rectangle(area, fill=red)

		brightness = stage_bw[x, y]

		stage_data[l][i] = 1 if brightness >= 10 else 0

stage.paste(poly, mask=poly)

stage.show()

for row in stage_data:
	print(row)





