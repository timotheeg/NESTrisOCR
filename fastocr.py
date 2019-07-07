import os
import PIL
import time
from PIL import Image, ImageEnhance

data = {}
redData = {}
digits = ['0','1','2','3','4','5','6','7','8','9','null']

MONO = True
IMAGE_SIZE = 7
BLOCK_SIZE = IMAGE_SIZE + 1
IMAGE_MULT = 2

STAGE_CHECK_5 = True

BLOCK_LUMA_THRESHOLD = 10
STAGE_BLOCK_WIDTH = 10
STAGE_BLOCK_HEIGHT = 20

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

CURRENT_PIECE_BLOCKS = {
    # Alignment 1
    'Z': ((0.115, 0.192), (0.462, 0.192), (0.462, 0.846), (0.769, 0.846)),
    'S': ((0.462, 0.192), (0.769, 0.192), (0.462, 0.846), (0.115, 0.846)),
    'T': ((0.115, 0.192), (0.462, 0.192), (0.769, 0.192), (0.462, 0.846)),

    # Alignment 2
    'L': ((0.115, 0.115), (0.462, 0.115), (0.731, 0.115), (0.115, 0.808)),
    'J': ((0.115, 0.115), (0.462, 0.115), (0.731, 0.115), (0.769, 0.808)),

    # Alignment 3
    'O': ((0.269, 0.231), (0.635, 0.231), (0.269, 0.846), (0.635, 0.846)),

    # Alignment 4
    'I': ((0.096, 0.538), (0.365, 0.538), (0.635, 0.538), (0.904, 0.538)),
}

def setupColour(prefix, outputDict):
    #setup white digits
    for digit in digits:
        filename = prefix + str(digit) + '.png'
        if digit == 'null':
            filename = 'sprite_templates/null.png'
        img = Image.open('assets/' + filename)
        
        img = img.convert('L')

        if IMAGE_MULT != 1:
            img = img.resize(
                (
                    IMAGE_SIZE * IMAGE_MULT,
                    IMAGE_SIZE * IMAGE_MULT
                ),
                PIL.Image.ANTIALIAS
            )

        outputDict[digit] = img.load()
        
def setupData():
    setupColour('sprite_templates/',data) #setup white
    setupColour('samples/red',redData) #setup red

def dist(col):
    return col * col
    
def sub(col1, col2):
    return col1 - col2


def getDigit(img, startX, startY, red):
    scores = {digit:0 for digit in digits}

    template = redData if red else data

    MAX = IMAGE_SIZE * IMAGE_MULT

    y = 0
    while y < MAX:
        x = 0
        while x < MAX:
            b = img[startX + x, startY + y]

            for digit in digits:
                a = template[digit][x, y]

                sub = a - b
                scores[digit] += sub * sub # adding distance

            x += 1
        y += 1

    lowest_score = float("inf")
    lowest_digit = None

    for digit, score in scores.items():
        if score < lowest_score:
            lowest_score = score
            lowest_digit = digit

    return lowest_digit


#convert to black/white, with custom threshold    
def contrastImg(img):  
    if MONO:
        img = img.convert('L')    
    #img = ImageEnhance.Brightness(img).enhance(2.0) # hack to parse red
    #img = ImageEnhance.Contrast(img).enhance(3.0)
    #img = ImageEnhance.Sharpness(img).enhance(1.5)
    return img
    
def convertImg(img, count, show):
    img = contrastImg(img)        
    img = img.resize(
        (
            (BLOCK_SIZE * count - 1) * IMAGE_MULT,
            IMAGE_SIZE * IMAGE_MULT
        ),
        PIL.Image.ANTIALIAS
    )

    if show:
        img.show()

    img = img.load()

    return img    

def scoreImage(img, count, show=False, red=False):
    start = time.time()
    img = convertImg(img, count, show)
    # print('convert', time.time() - start)
    label = ""

    for i in range(count):
        start = time.time()
        digit = getDigit(img, i * BLOCK_SIZE * IMAGE_MULT, 0, red)
        # print('getDigit', time.time() - start)
        if digit == 'null':
            return None
        else:
            label += digit

    return label

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

    if os.environ.get('DEBUG'):
        print(
            (x, y, _luma),
            (x-1, y-1, luma(stage_img[x-1, y-1])),
            (x+1, y-1, luma(stage_img[x+1, y-1])),
            (x-1, y+1, luma(stage_img[x-1, y+1])),
            (x+1, y+1, luma(stage_img[x+1, y+1]))
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


def scorePiece(img, block_map):
    loaded_img = img.load()

    for name, blocks in block_map.items():
        detected = True

        if os.environ.get('DEBUG'):
            print(name, img.width, img.height)
    
        for block in blocks:
            if os.environ.get('DEBUG'):
                print((block[0], block[1]), (block[0] * img.width, block[1] * img.height))
    
            if not is_block_active(loaded_img, round(block[0] * img.width), round(block[1] * img.height)):
                detected = False
                break

        if detected:
            return name


def scoreCurrentPiece(img):
    return scorePiece(img, CURRENT_PIECE_BLOCKS)

def scoreNextPiece(img):
    return scorePiece(img, NEXT_PIECE_BLOCKS)

setupData()
    
if __name__ == '__main__':
    setupData()
    import time
    
    t = time.time()
    for i in range(1):
        img = Image.open("test/"+"{:06d}".format(i*100)+".png")
        
        
    print ("total time:", str(time.time() - t))
    print ("rescale time:", str(time.time() - t2))
    print ("AI time:", str(t2-t))
    