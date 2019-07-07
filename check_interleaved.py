from PIL import Image

STAGE_CHECK_5 = True

BLOCK_LUMA_THRESHOLD = 10
STAGE_BLOCK_WIDTH = 10
STAGE_BLOCK_HEIGHT = 20


def luma(pixel):
    return pixel[0] * 0.299 + pixel[1] * 0.587 + pixel[2] * 0.114

def is_block_active(stage_img, x, y):
    # fastest, but perhaps not so accurate?
    _luma = luma(stage_img[x, y])
    active = _luma > BLOCK_LUMA_THRESHOLD

    # better check for piece
    if STAGE_CHECK_5:
        active = (active
            and (luma(stage_img[x-1, y-1]) > BLOCK_LUMA_THRESHOLD)
            and (luma(stage_img[x+1, y-1]) > BLOCK_LUMA_THRESHOLD)
            and (luma(stage_img[x-1, y+1]) > BLOCK_LUMA_THRESHOLD)
            and (luma(stage_img[x+1, y+1]) > BLOCK_LUMA_THRESHOLD)
        )

    return 1 if active else 0


def scoreStage(stage_img):
    block_size_w = stage_img.width / STAGE_BLOCK_WIDTH
    block_size_h = stage_img.height / STAGE_BLOCK_HEIGHT

    offset_x = block_size_w * 0.5
    offset_y = block_size_h * 0.5

    stage_data = [[] for j in range(STAGE_BLOCK_HEIGHT)]

    j = 0
    active_blocks = 0

    loaded_stage = stage_img.load()

    while j < STAGE_BLOCK_HEIGHT:
        i = 0
        while i < STAGE_BLOCK_WIDTH:
            x = round(offset_x + block_size_w * i)
            y = round(offset_y + block_size_h * j)

            active = is_block_active(loaded_stage, x, y)
            active_blocks += (1 if active else 0)
            stage_data[j].append(active)

            i += 1
        j += 1

    return active_blocks, stage_data



img = Image.open('/Users/timothee/interleaved.png')

score = scoreStage(img)

print(score[0])

for row in score[1]:
	print(row)



