import PIL
import numpy as np
import time

from lib import lerp

from config import config
from Networking.ByteStuffer import prePackField

try:
    from OCRAlgo.board_ocr import parseImage2 #if it's built
    #print("loading parseImage2 from compiled")
except:
    from OCRAlgo.BoardOCR2 import parseImage2
    print("Warning, loaded parseImage2 from llvmlite: please run buildBoardOCR2 to build a compiled version")

LEVEL_COLORS = (
    { 'color1': (0x4A, 0x32, 0xFF), 'color2': (0x4A, 0xAF, 0xFE) },
    { 'color1': (0x00, 0x96, 0x00), 'color2': (0x6A, 0xDC, 0x00) },
    { 'color1': (0xB0, 0x00, 0xD4), 'color2': (0xFF, 0x56, 0xFF) },
    { 'color1': (0x4A, 0x32, 0xFF), 'color2': (0x00, 0xE9, 0x00) },
    { 'color1': (0xC8, 0x00, 0x7F), 'color2': (0x00, 0xE6, 0x78) },
    { 'color1': (0x00, 0xE6, 0x78), 'color2': (0x96, 0x8D, 0xFF) },
    { 'color1': (0xC4, 0x1E, 0x0E), 'color2': (0x66, 0x66, 0x66) },
    { 'color1': (0x82, 0x00, 0xFF), 'color2': (0x78, 0x00, 0x41) },
    { 'color1': (0x4A, 0x32, 0xFF), 'color2': (0xC4, 0x1E, 0x0E) },
    { 'color1': (0xC4, 0x1E, 0x0E), 'color2': (0xF6, 0x9B, 0x00) },
)

def parseImageReadColors(img, color1, color2):
    color1 = color1.resize((1,1), PIL.Image.ANTIALIAS)
    color1 = color1.getpixel((0,0))
    color2 = color2.resize((1,1), PIL.Image.ANTIALIAS)
    color2 = color2.getpixel((0,0))

    black = np.array((10,10,10), dtype=np.uint8)
    white = np.array((240,240,240), dtype=np.uint8)


    return parseImage(img, black, white, color1, color2)


def parseImageInterpolateColors(img, black, white, level=0):
    black = black.resize((1,1), PIL.Image.NEAREST)
    black = black.getpixel((0,0))
    white = white.resize((1,1), PIL.Image.NEAREST)
    white = white.getpixel((0,0))

    color1 = LEVEL_COLORS[level % 10]['color1']
    color2 = LEVEL_COLORS[level % 10]['color2']

    color1 = (
        lerp(black[0], white[0], color1[0]/0xFF),
        lerp(black[1], white[1], color1[1]/0xFF),
        lerp(black[2], white[2], color1[2]/0xFF)
    )

    color2 = (
        lerp(black[0], white[0], color2[0]/0xFF),
        lerp(black[1], white[1], color2[1]/0xFF),
        lerp(black[2], white[2], color2[2]/0xFF)
    )

    black = np.array(black,dtype=np.uint8)
    white = np.array(white,dtype=np.uint8)
    color1 = np.array(color1,dtype=np.uint8)
    color2 = np.array(color2,dtype=np.uint8)

    return parseImage(img, black, white, color1, color2)

    
def parseImage(img, black, white, color1, color2):    
    img = img.resize((10,20),PIL.Image.NEAREST)
    img = np.array(img,dtype=np.uint8)
    
    result = parseImage2(img, black, white, color1, color2)
    
    if config.netProtocol == 'AUTOBAHN_V2':
        result = prePackField(result)
        result = result.tobytes()
    else:
        result2 = []
        for y in range(20):
            temp = "".join(str(result[y, x]) for x in range(10))        
            result2.append(temp)
        result = "".join(str(r) for r in result2)
    
    return result



#run as python -m OCRAlgo.BoardOCR
if __name__ == '__main__':    
    
    
    from PIL import Image
    img = Image.open("assets/test/board.jpg")
    color1 = Image.open("assets/test/color1.jpg")
    color2 = Image.open("assets/test/color2.jpg")
    t = time.time()
    for i in range(100):
        parseImage(img, color1, color2)
    print(time.time() - t)
    
    