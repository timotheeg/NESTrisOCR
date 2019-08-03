import asyncio
import datetime
import random
import websockets

import sys
import platform
import argparse
import re
import math

if platform.system() == 'Darwin':
    import QuartzCapture as WindowCapture
    from QuartzWindowMgr import WindowMgr

else:
    import Win32UICapture as WindowCapture
    from Win32WindowMgr import WindowMgr

from PIL import Image, ImageDraw
from fastocr import scoreImage, scoreStage, scoreCurrentPiece, scoreNextPiece
from multiprocessing import Pool
from Networking import TCPClient
import json
import time

from calibration import * #bad!


RATE = 0.016

HIGHLIGHT_COLORS = {
    'red':     (255,   0,   0, 128),
    'blue':    (  0,   0, 255, 128),
    'orange':  (255, 165,   0, 128),
}

# define what can be captured and how many digits they have
CAPTURE_AREAS_ALLOW_LIST = {
    'score':       6,
    'level':       2,
    'lines':       3,
    'stage':       None,
    'next_piece':  None,
    'piece_stats': 3,

    # das trainer specific stats
    'das':           2,
    'cur_piece':     None,
    'cur_piece_das': 2,
    'das_stats':     3
}

CAPTURE_PROFILES = {
    'original':        'score,level,lines,piece_stats',
    'original_all':    'score,level,lines,piece_stats,stage,next_piece',
    'das_trainer':     'score,level,lines,stage,cur_piece,cur_piece_das',
    'das_trainer_all': 'score,level,lines,stage,cur_piece,cur_piece_das,das,das_stats,next_piece',
}

COORDINATES_XYWH = {}
COORDINATES_LTRB = {}

# error print
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def lerp(start, end, perc):
    return perc * (end-start) + start
    
def mult_rect(rect, mult):
    multiplied = (math.floor(rect[2] * mult[0] + rect[0]),
            math.floor(rect[3] * mult[1] + rect[1]),
            math.ceil(rect[2] * mult[2]),
            math.ceil(rect[3] * mult[3]))

    return multiplied

def generate_piece_stats(captureCoords, statBoxPerc, statHeight, do_mult=True):    
    statGap = (statBoxPerc[3] - (7*statHeight))/6
    statGap = statGap + statHeight
    offsets = [i*(statGap) for i in range(7)]
    pieces = ['T','J','Z','O','S','L','I']
    result = {}
    for i, piece in enumerate(pieces):
        offset = offsets[i]
        box = (statBoxPerc[0],statBoxPerc[1]+offset,statBoxPerc[2],statHeight)

        if do_mult:
            result[piece] = mult_rect(captureCoords, box)
        else:
            result[piece] = box

    return result

def generate_das_stats(captureCoords, statBoxPerc, statHeight, do_mult=True):    
    statGap = (statBoxPerc[3] - (4 * statHeight)) / 3
    statGap = statGap + statHeight
    offsets = [i*(statGap) for i in range(7)]
    das_categories = ['great', 'ok', 'bad', 'terrible']
    result = {}
    for i, category in enumerate(das_categories):
        offset = offsets[i]
        box = (statBoxPerc[0], statBoxPerc[1] + offset,statBoxPerc[2], statHeight)

        if do_mult:
            result[category] = mult_rect(captureCoords, box)
        else:
            result[category] = box

    return result


def xywhToLtrb(rect_xywh, offset=(0, 0)):
    left = rect_xywh[0] - offset[0] # substract to be relative to window cut, rather than full window
    top = rect_xywh[1] - offset[1] # substract to be relative to window cut, rather than full window
    right = left + rect_xywh[2]
    bottom = top + rect_xywh[3]
    return (left, top, right, bottom)

def ltrbToxywh(rect_ltrb):
    x = rect_ltrb[0]
    y = rect_ltrb[1]
    width  = rect_ltrb[2] - rect_ltrb[0]
    height = rect_ltrb[3] - rect_ltrb[1]
    return (x, y, width, height)


# we need to compute the minimum window area to extract in one call
# and then compute the coordinates of each capture area in LTRB format for PIL

temp_coordinates = [xywhToLtrb(coordinates) for area_id, coordinates in CAPTURE_AREAS.items()]

min_window_coords_ltrb = (
    min( (coordinates[0] for coordinates in temp_coordinates) ),
    min( (coordinates[1] for coordinates in temp_coordinates) ),
    max( (coordinates[2] for coordinates in temp_coordinates) ),
    max( (coordinates[3] for coordinates in temp_coordinates) ),
)

MIN_WINDOW_COORDS_XYWH = mult_rect(WINDOW_CAPTURE_COORDS, ltrbToxywh(min_window_coords_ltrb))

    
for area_id, coordinates in CAPTURE_AREAS.items():
    if area_id == 'piece_stats':
        COORDINATES_XYWH['piece_stats_whole'] = mult_rect(WINDOW_CAPTURE_COORDS, coordinates)
        COORDINATES_XYWH[area_id] = generate_piece_stats(WINDOW_CAPTURE_COORDS, coordinates, CAPTURE_AREAS["score"][3])
    elif area_id == 'das_stats':
        COORDINATES_XYWH['das_stats_whole'] = mult_rect(WINDOW_CAPTURE_COORDS, coordinates)
        COORDINATES_XYWH[area_id] = generate_das_stats(WINDOW_CAPTURE_COORDS, coordinates, CAPTURE_AREAS["score"][3])
    else:
        COORDINATES_XYWH[area_id] = mult_rect(WINDOW_CAPTURE_COORDS, coordinates)

for area_id, coordinates in COORDINATES_XYWH.items():
    if type(coordinates) is dict:
        COORDINATES_LTRB[area_id] = {}
        for key, coordinates2 in coordinates.items():
            COORDINATES_LTRB[area_id][key] = xywhToLtrb(coordinates2, MIN_WINDOW_COORDS_XYWH)
    else:
        COORDINATES_LTRB[area_id] = xywhToLtrb(coordinates, MIN_WINDOW_COORDS_XYWH)



def getWindow(hwnd=None):
    wm = WindowMgr()

    if hwnd:
        if platform.system() == 'Darwin':
            return wm.getWindow(hwnd['ID'])

    windows = wm.getWindows()

    for window in windows:
        if window[1].startswith(WINDOW_NAME):
            return window[0]

    return None

def highlight_calibration(img, areas):
    poly = Image.new('RGBA', (img.width, img.height))
    draw = ImageDraw.Draw(poly)
    subareas = {}

    for area_id in areas:
        fill = HIGHLIGHT_COLORS['red']

        if area_id in ('piece_stats', 'das_stats'):
            fill = HIGHLIGHT_COLORS['blue']
            subareas = COORDINATES_XYWH[area_id]
            area_id += '_whole'

        coordinates = COORDINATES_XYWH[area_id]

        draw.rectangle(xywhToLtrb(coordinates, WINDOW_CAPTURE_COORDS), fill=fill)

        for _, coordinates in subareas.items():
            draw.rectangle(xywhToLtrb(coordinates, WINDOW_CAPTURE_COORDS), fill=HIGHLIGHT_COLORS['orange'])   

    img.paste(poly, mask=poly)
    del draw
    
def calibrate(areas, only_highlight=True):
    hwnd = getWindow()

    if hwnd is None:
        print ("Unable to find OBS window with title:",  WINDOW_NAME)
        return

    if only_highlight:
        # show main wondow and hoghlight all required areas
        img = WindowCapture.ImageCapture(WINDOW_CAPTURE_COORDS, hwnd)
        highlight_calibration(img, areas)
        img.show()
    else:
        # Extract all areas of interest and show them individually
        for area_id in areas:
            subareas = {}

            if area_id in ('piece_stats', 'das_stats'):
                subareas = COORDINATES_XYWH[area_id]
                area_id += '_whole'

            img = WindowCapture.ImageCapture(COORDINATES_XYWH[area_id], hwnd)
            img.show()

            for _, coordinates in subareas.items():
                img = WindowCapture.ImageCapture(coordinates, hwnd)
                img.show()

def captureAndOCR(coords, window_img, digits, taskName, draw=False, red=False):
    start = time.time()
    img = window_img.crop(coords)
    # print('captureAndOCR', taskName, time.time() - start)
    return taskName, scoreImage(img, digits, draw, red)

def captureStage(coords, window_img, taskName, draw=False, red=False):
    start = time.time()
    img = window_img.crop(coords)
    # print('captureStage', time.time() - start)

    score = scoreStage(img)

    return taskName, score

def captureCurrentPiece(coords, window_img, taskName, draw=False, red=False):
    start = time.time()
    img = window_img.crop(coords)
    # print('captureCurrentPiece', time.time() - start)
    return taskName, scoreCurrentPiece(img)

def captureNextPiece(coords, window_img, taskName, draw=False, red=False):
    start = time.time()
    img = window_img.crop(coords)
    # print('captureNextPiece', time.time() - start)
    return taskName, scoreNextPiece(img)

def runFunc(func, args):
    return func(*args)

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def getCLIArguments():
    parser = argparse.ArgumentParser(description='NESTrisOCR')

    parser.add_argument('--calibrate', action='store_true',
                       default=False,
                       help='Indicate whether this should be a calibration run')

    parser.add_argument('--only_highlight', type=str2bool, nargs='?',
                       const=True, default=True,
                       help='Indicate whether this should be a calibration run')

    parser.add_argument('--capture', action='store',
                       default='',
                       help='Supply list of areas IDs to capture. Comma separated from list [score, level, lines, stage, next_piece, piece_stats, cur_piece, das, cur_piece_das, das_stats]')

    parser.add_argument('--profile', action='store',
                       default='original',
                       help='Specify which list of capture area will be considered, Allowed values [original, das_trainer]. Note that if --capture is specified profile is ignored.')

    parser.add_argument('--threads', action='store', nargs='?',
                       type=int, default=1,
                       help='sum the integers (default: find the max)')

    args = parser.parse_args()


    # Validate profile and area ids
    if args.profile:
        if args.profile in CAPTURE_PROFILES:
            capture_areas = CAPTURE_PROFILES[args.profile]
        else:
            eprint('Invalid profile', args.profile)
            sys.exit(1)

    if args.capture:
        if re.search('^[a-z_]+(,[a-z_]+)*$', args.capture):
            capture_areas = args.capture
        else:
            eprint('Invalid capture argument format', args.capture)
            sys.exit(2)

    area_ids = set(capture_areas.split(','))

    if not area_ids.issubset(set([key for key in CAPTURE_AREAS_ALLOW_LIST])):
        eprint('Invalid capture area id', args.capture)
        sys.exit(3)

    # override args to the validated set so we don't do it again later
    args.capture = area_ids

    return args



async def main(websocket, path):
    args = getCLIArguments()

    if args.calibrate:
        calibrate(args.capture, only_highlight=args.only_highlight)
        sys.exit()

    if args.threads >= 2:
        p = Pool(args.threads)
    else:
        p = None
    
    while True:
        frame_start  = time.time()
        hwnd = getWindow()
        # print('getWindow()', time.time() - frame_start)

        if not hwnd:
            frame_end = frame_start + RATE
            while time.time() < frame_end:
                time.sleep(0.001)

            continue

        while True:
            frame_start  = time.time()
            hwnd = getWindow(hwnd)
            # print('getWindow(hwnd)', time.time() - frame_start)

            if not hwnd:
                break

            pitstop = time.time()
            window_img = WindowCapture.ImageCapture(MIN_WINDOW_COORDS_XYWH, hwnd)
            # print('window_capture', time.time() - pitstop)

            # window_img.show()
            # sys.exit()

            result = {}
            rawTasks = []

            for area_id in args.capture:
                ocr_char_len = CAPTURE_AREAS_ALLOW_LIST[area_id]
                coordinates = COORDINATES_LTRB[area_id]

                if area_id in ('piece_stats', 'das_stats'):
                    for key, coordinates in COORDINATES_LTRB[area_id].items():
                        rawTasks.append((captureAndOCR, (coordinates, window_img, ocr_char_len, area_id + '.' + key)))
                elif area_id == 'stage':
                    rawTasks.append((captureStage, (coordinates, window_img, area_id)))
                elif area_id == 'next_piece':
                    rawTasks.append((captureNextPiece, (coordinates, window_img, area_id)))
                elif area_id == 'cur_piece':
                    rawTasks.append((captureCurrentPiece, (coordinates, window_img, area_id)))
                else:
                    rawTasks.append((captureAndOCR, (coordinates, window_img, ocr_char_len, area_id)))

            result = {}
            if p: #multithread
                tasks = []

                for task in rawTasks:
                    tasks.append(p.apply_async(task[0], task[1]))

                taskResults = [res.get(timeout=1) for res in tasks]

                for key, number in taskResults:
                    result[key] = number
                
            else: #single thread
                pitstop = time.time()
                # print('before capture', pitstop - frame_start)
                for task in rawTasks:
                    key, number = runFunc(task[0], task[1])
                    result[key] = number
                    # print(key, time.time() - pitstop)
                    pitstop = time.time()

            payload = json.dumps(result)

            # print(payload)

            await websocket.send(payload)
            # onCap(result)

            #print('TOTAL PROCESSING', time.time() - frame_start)

            now = time.time()
            frame_end = frame_start + RATE

            if (now < frame_end):
                await asyncio.sleep(frame_end - now)

            # while time.time() < frame_end:
            #     time.sleep(0.001)
        
class CachedSender(object):
    def __init__(self, client):
        self.client = client
        self.lastMessage = None

    #convert message to jsonstr and then send if its new.
    def sendResult(self, message):
        for row in message['stage'][1]:
            print(row);
        jsonMessage = json.dumps(message,indent=2)
        self.client.sendMessage(jsonMessage)

    
def sendResult(client, message):    
    jsonStr = json.dumps(message, indent=2)
    client.sendMessage(jsonStr)
        
if __name__ == '__main__':

    start_server = websockets.serve(main, '127.0.0.1', 3338)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


    # client = TCPClient.CreateClient('127.0.0.1', 3338)
    # cachedSender = CachedSender(client)
    # main(cachedSender.sendResult)
    

        
