from PIL import Image

BLACK_LIMIT = 20

NEXT_PIECE_BLOCKS = {
    # Alignment 1
    'J': ((0.253, 0.125), (0.500, 0.125), (0.775, 0.125), (0.775, 0.875)),
    'L': ((0.253, 0.125), (0.500, 0.125), (0.775, 0.125), (0.253, 0.875)),
    'Z': ((0.253, 0.125), (0.500, 0.125), (0.500, 0.875), (0.775, 0.875)),
    'S': ((0.500, 0.125), (0.775, 0.125), (0.500, 0.875), (0.253, 0.875)),
    'T': ((0.253, 0.125), (0.500, 0.125), (0.775, 0.125), (0.500, 0.875)),

    # Alignment 2
    'O': ((0.380, 0.125), (0.630, 0.125), (0.380, 0.875), (0.630, 0.875)),
    'I': ((0.110, 0.500), (0.380, 0.500), (0.630, 0.500), (0.890, 0.500)),
}

def luma(pixel):
    return pixel[0] * 0.299 + pixel[1] * 0.587 + pixel[2] * 0.114

def is_block_active(stage_img, x, y):
    # fastest, but perhaps not so accurate?
    _luma = luma(stage_img[x, y])
    return _luma > BLACK_LIMIT

def parseImage(img):
    loaded_img = img.load()

    for name, blocks in NEXT_PIECE_BLOCKS.items():
        detected = True

        for block in blocks:
            if not is_block_active(loaded_img, round(block[0] * img.width), round(block[1] * img.height)):
                detected = False
                break

        if detected:
            return name

