from PIL import Image, ImageDraw
import math


STAGE_BLOCK_WIDTH = 10
STAGE_BLOCK_HEIGHT = 20
BLOCK_PCT = 0.1
OFFSET_PCT = (1 - BLOCK_PCT) / 2

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

highlight_size_w = math.ceil(block_size_w * BLOCK_PCT)
highlight_size_h = math.ceil(block_size_h * BLOCK_PCT)

print(highlight_size_w, highlight_size_h)

offset_x = block_size_w * OFFSET_PCT
offset_y = block_size_h * OFFSET_PCT

red = (255, 0, 0, 128)

def average_brightness(img, area):
	value = 0
	pixel_count = 0
	for x in range(area[0], area[2]):
		for y in range(area[1], area[3]):
			pixel_count += 1
			value += img[x, y]

	return value / pixel_count
	

stage_data = [[0 for i in range(STAGE_BLOCK_WIDTH)] for j in range(STAGE_BLOCK_HEIGHT)]

for row in stage_data:
	print(row)


poly = Image.new('RGBA', (img.width, img.height))
draw = ImageDraw.Draw(poly)
for i in range(STAGE_BLOCK_WIDTH):
	for l in range(STAGE_BLOCK_HEIGHT):
		x = round(offset_x + block_size_w * i)
		y = round(offset_y + block_size_h * l)

		area = (x, y, x + highlight_size_w, y + highlight_size_h)
		draw.rectangle(area, fill=red)

		brightness = average_brightness(stage_bw, area)

		stage_data[l][i] = '{:>10}'.format(brightness if brightness > 10 else 0)

stage.paste(poly, mask=poly)

stage.show()

for row in stage_data:
	print(row)





