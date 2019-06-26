STAGE_WIDTH = 10
STAGE_HEIGHT = 20
BLOCK_PCT = 0.5
OFFSET_PCT = (1 - BLOCK_PCT) / 2


from PIL import Image
img = Image.open('assets/das_trainer_sprites/I.png')


x = 221
y = 92

block_size_w = img.width / STAGE_WIDTH
block_size_h = img.height / STAGE_HEIGHT

highlight_size_w = block_size_w * BLOCK_PCT
highlight_size_h = block_size_h * BLOCK_PCT

stage = img.crop((x, y, x + img.width, y + img.height))

red = (255,0,0,128)


poly = Image.new('RGBA', (img.width, img.height))
draw = ImageDraw.Draw(poly)
for i in range(STAGE_WIDTH):
	for l in range(STAGE_HEIGHT):
		x = round(block_size_w * i)
		y = round(block_size_h * l)
		draw.rectangle((x, y, x + highlight_size_w, y + highlight_size_h),fill=red)




