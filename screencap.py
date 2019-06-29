import sys
import platform
import argparse
import re

if platform.system() == 'Darwin':
    import QuartzCapture as WindowCapture
    from QuartzWindowMgr import WindowMgr

else:
    import Win32UICapture as WindowCapture
    from Win32WindowMgr import WindowMgr

from PIL import Image, ImageDraw
from fastocr import scoreImage
from multiprocessing import Pool
from Networking import TCPClient
import json
import time

from calibration import * #bad!


RATE = 0.064

HIGHLIGHT_COLORS = {
    'red':     (255,   0,   0, 128),
    'blue':    (  0,   0, 255, 128),
    'orange':  (255, 165,   0, 128),
}

HIGHLIGHT_COLORS['default'] = HIGHLIGHT_COLORS['red']

CAPTURE_AREAS_ALLOW_LIST = set((
    'score',
    'level',
    'lines',
    'stage',
    'next_piece',
    'piece_stats',

    # das trainer specific stats
    'das',
    'cur_piece',
    'cur_piece_das',
    'das_stats'
))

CAPTURE_PROFILES = {
    'original':        'score,level,lines,piece_stats',
    'original_all':    'score,level,lines,piece_stats,stage,next_piece',
    'das_trainer':     'score,level,lines,cur_piece,cur_piece_das',
    'das_trainer_all': 'score,level,lines,cur_piece,cur_piece_das,stage,next_piece',
}

COORDINATES = {}

# error print
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def lerp(start, end, perc):
    return perc * (end-start) + start
    
def mult_rect(rect, mult):
    multiplied =  (round(rect[2] * mult[0] + rect[0]),
            round(rect[3] * mult[1] + rect[1]),
            round(rect[2] * mult[2]),
            round(rect[3] * mult[3]))

    if len(mult) == 5:
        multiplied = multiplied + (mult[4], )

    return multiplied

def generate_line_stats(captureCoords, statBoxPerc, statHeight, do_mult=True):    
    statGap = (statBoxPerc[3] - (7*statHeight))/6
    statGap = statGap + statHeight
    offsets = [i*(statGap) for i in range(7)]
    pieces = ['T','J','Z','O','S','L','I']
    result = {}
    for i, piece in enumerate(pieces):
        offset = offsets[i]
        box = (statBoxPerc[0],statBoxPerc[1]+offset,statBoxPerc[2],statHeight)

        if do_mult:
            result[piece] = mult_rect(captureCoords,box)
        else:
            result[piece] = box

        result[piece] = result[piece] + ('orange', )

    return result


for area_id, coordinates in CAPTURE_AREAS.items():
    if area_id == 'line_stats':
        COORDINATES['line_stats_whole'] = mult_rect(WINDOW_CAPTURE_COORDS, coordinates)
        COORDINATES[area_id] = generate_line_stats(WINDOW_CAPTURE_COORDS, coordinates, CAPTURE_AREAS["score"][3])
    elif area_id == 'das_stats':
        pass
    else:
        COORDINATES[area_id] = mult_rect(WINDOW_CAPTURE_COORDS, coordinates)


def getWindow():
    wm = WindowMgr()
    windows = wm.getWindows()
    for window in windows:
        if window[1].startswith(WINDOW_NAME):
            return window[0]
    return None

def screenPercToPixels(w,h,rect_xywh):
    left = rect_xywh[0] * w
    top = rect_xywh[1] * h
    right = left + rect_xywh[2]*w
    bot = top+ rect_xywh[3]*h
    return (left,top,right,bot)
    
def highlight_calibration(img, areas):
    poly = Image.new('RGBA', (img.width, img.height))
    draw = ImageDraw.Draw(poly)

    for area_id in areas:
        coordinates = COORDINATES[area_id]
        if len(coordinates) == 5:
            fill = HIGHLIGHT_COLORS[ coordinates[4] ]
        else:
            fill = HIGHLIGHT_COLORS[ 'DEFAULT' ]

        if area_id == 'line_stats':
            pass
        elif area_id == 'das_stats':
            pass
        else:
            draw.rectangle(screenPercToPixels(img.width, img.height, COORDINATES['area_id']), fill=fill)

    img.paste(poly, mask=poly)

    #pieces
    #draw.rectangle(screenPercToPixels(img.width,img.height,statsPerc),fill=blue)
    #print(statsPerc)
    #for value in generate_line_stats(WINDOW_CAPTURE_COORDS,statsPerc,scorePerc[3],False).values():
    #    print(value)
    #    draw.rectangle(screenPercToPixels(img.width,img.height,value),fill=orange)
    
def calibrate(areas, only_highlight=True):
    hwnd = getWindow()

    if hwnd is None:
        print ("Unable to find OBS window with title:",  WINDOW_NAME)
        return

    if only_highlight:
        img = WindowCapture.ImageCapture(WINDOW_CAPTURE_COORDS, hwnd)
        highlight_calibration(img, areas)
        img.show()
    else:
        for area_id in areas:
            if area_id == 'line_stats':
                pass
            elif area_id == 'das_stats':
                pass
            else:
                img = WindowCapture.ImageCapture(COORDINATES[area_id], hwnd)
                img.show()

def captureAndOCR(coords,hwnd,digits,taskName,draw=False,red=False):
    img = WindowCapture.ImageCapture(coords,hwnd)
    return taskName, scoreImage(img,digits,draw,red)

def runFunc(func, args):
    return func(*args)

def getCLIArguments():
    parser = argparse.ArgumentParser(description='NESTrisOCR')

    parser.add_argument('--calibrate', action='store_true',
                       default=False,
                       help='Indicate whether this should be a calibration run')

    parser.add_argument('--only_highlight', action='store_const',
                       const=bool, default=True,
                       help='Indicate whether this should be a calibration run')

    parser.add_argument('--capture', action='store',
                       default='',
                       help='Supply list of areas IDs to capture. Comma separated from list [score, level, lines, stage, next_piece, piece_stats, cur_piece, das, cur_piece_das, das_stats]')

    parser.add_argument('--profile', action='store',
                       default='original',
                       help='Specify which list of capture area will be considered, Allowed values [original, das_trainer]. Note that if --capture is specified profile is ignored.')

    parser.add_argument('--threads', action='store_const',
                       const=int, default=1,
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
        if re.search('^[a-z]+(,[a-z]+)*$', args.capture):
            capture_areas = args.capture
        else:
            eprint('Invalid capture argument format', args.capture)
            sys.exit(2)

    area_ids = set(capture_areas.split(','))

    if not area_ids.issubset(CAPTURE_AREAS_ALLOW_LIST):
        eprint('Invalid capture area id', args.capture)
        sys.exit(3)

    # override args to the validated set so we don't do it again later
    args.capture = area_ids

    return args



def main(onCap):
    args = getCLIArguments()

    if args.calibrate:
        calibrate(args.capture, only_highlight=args.only_highlight)
        sys.exit()

    if args.threads >= 2:
        p = Pool(args.threads)
    else:
        p = None
    
    while True:
        frame_end = time.time() + RATE
        hwnd = getWindow()
        result = {}
        if hwnd:       
            rawTasks = []
            rawTasks.append((captureAndOCR,(SCORE_COORDS,hwnd,6,"score")))
            rawTasks.append((captureAndOCR,(LINES_COORDS,hwnd,3,"lines")))
            rawTasks.append((captureAndOCR,(LEVEL_COORDS,hwnd,2,"level")))
            #for key in STATS_COORDS:
            #    rawTasks.append((captureAndOCR,(STATS_COORDS[key],hwnd,3,key,False,True)))
                
            result = {}
            if p: #multithread
                tasks = []
                for task in rawTasks:
                    tasks.append(p.apply_async(task[0],task[1]))                
                taskResults = [res.get(timeout=1) for res in tasks]
                for key, number in taskResults:
                    result[key] = number
                
            else: #single thread                   
                for task in rawTasks:
                    key, number = runFunc(task[0],task[1])
                    result[key] = number
        
            onCap(result)  
        while time.time() < frame_end:
            time.sleep(0.001)
        
class CachedSender(object):
    def __init__(self, client):
        self.client = client
        self.lastMessage = None

    #convert message to jsonstr and then send if its new.
    def sendResult(self, message):
        print(message)
        jsonMessage = json.dumps(message,indent=2)        
        self.client.sendMessage(jsonMessage)

    
def sendResult(client, message):    
    jsonStr = json.dumps(message, indent=2)
    client.sendMessage(jsonStr)
        
if __name__ == '__main__':
    client = TCPClient.CreateClient('127.0.0.1', 3338)
    cachedSender = CachedSender(client)
    main(cachedSender.sendResult)
    

        