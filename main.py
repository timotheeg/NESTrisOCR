from PIL import Image, ImageDraw
from fastocr import scoreImage
from calibration import * #bad!
from lib import * #bad!
from ScoreFixer import ScoreFixer
from CachedSender import CachedSender
from multiprocessing import Pool
import threading
from Networking import TCPClient
from textstats import generate_stats
import boardocr
import time
import config


#patterns for digits. 
#A = 0->9 + A->F, 
#D = 0->9
SCORE_PATTERN = 'DDDDDD' #change to DDDDDD if you don't have A-F enabled.
LINES_PATTERN = 'DDD'
LEVEL_PATTERN = 'DD'
STATS_PATTERN = 'DDD'

SCORE_COORDS = mult_rect(CAPTURE_COORDS,scorePerc)
LINES_COORDS = mult_rect(CAPTURE_COORDS,linesPerc)
LEVEL_COORDS = mult_rect(CAPTURE_COORDS,levelPerc)

#piece stats and method. Recommend using FIELD
STATS_ENABLE  = True
STATS_COORDS  = generate_stats(CAPTURE_COORDS,statsPerc,scorePerc[3])
STATS2_COORDS = mult_rect(CAPTURE_COORDS, stats2Perc)
STATS_METHOD  = 'FIELD' #can be TEXT or FIELD. 

USE_STATS_FIELD = (STATS_ENABLE and STATS_METHOD == 'FIELD')

CALIBRATION = True
MULTI_THREAD = 1 # shouldn't need more than four if using FieldStats + score/lines/level

#limit how fast we scan.
RATE_FIELDSTATS = 0.004
RATE_TEXTONLY = 0.064

if USE_STATS_FIELD and MULTI_THREAD == 1:    
    RATE = RATE_FIELDSTATS
else:
    RATE = RATE_TEXTONLY


def highlight_calibration(img):    
    poly = Image.new('RGBA', (img.width,img.height))
    draw = ImageDraw.Draw(poly)
    
    red = (255,0,0,128)    
    blue = (0,0,255,128)       
    orange = (255,165,0,128)
    
    #score
    draw.rectangle(screenPercToPixels(img.width,img.height,scorePerc),fill=red)
    #lines
    draw.rectangle(screenPercToPixels(img.width,img.height,linesPerc),fill=red)
    #level
    draw.rectangle(screenPercToPixels(img.width,img.height,levelPerc),fill=red)    
    if STATS_METHOD == 'TEXT':
        #pieces
        draw.rectangle(screenPercToPixels(img.width,img.height,statsPerc),fill=blue)
        for value in generate_stats(CAPTURE_COORDS,statsPerc,scorePerc[3],False).values():
            draw.rectangle(screenPercToPixels(img.width,img.height,value),fill=orange)
    else: #STATS_METHOD == 'FIELD':        
        draw.rectangle(screenPercToPixels(img.width,img.height,stats2Perc),fill=blue)
        for x in range (4):
            for y in range(2):                
                blockPercX = lerp(stats2Perc[0], stats2Perc[0]+stats2Perc[2], x/4.0 + 1/8.0)
                blockPercY = lerp(stats2Perc[1], stats2Perc[1]+stats2Perc[3], y/2.0 + 1/4.0)
                rect = (blockPercX-0.01, blockPercY-0.01, 0.02, 0.02)
                draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=red)
        
    img.paste(poly,mask=poly)    
    del draw
    
def calibrate():
    hwnd = getWindow()
    if hwnd is None:
        print ("Unable to find window with title:",  WINDOW_NAME)
        return
    
    img = WindowCapture.ImageCapture(CAPTURE_COORDS,hwnd)
    highlight_calibration(img)
    img.show()
    return

def captureAndOCR(coords,hwnd,digitPattern,taskName,draw=False,red=False):
    t = time.time()
    img = WindowCapture.ImageCapture(coords,hwnd)    
    return taskName, scoreImage(img,digitPattern,draw,red)

def captureAndOCRBoard(coords, hwnd):
    img = WindowCapture.ImageCapture(coords, hwnd)
    rgbo = boardocr.parseImage(img)    
    return ('board_ocr', rgbo)

#run this as fast as possible    
def statsFieldMulti(ocr_stats, pool):
    while True:
        t = time.time()
        hwnd = getWindow()
        _, pieceType = pool.apply(captureAndOCRBoard, (STATS2_COORDS, hwnd))
        ocr_stats.update(pieceType,t)
        if (time.time() - t > 1/60.0):
            print ("Warning, not scanning field fast enough")
        
        # only sleep once.
        if time.time() < t + RATE_FIELDSTATS:
            time.sleep(0.001)


def main(onCap):    
    if CALIBRATION:
        calibrate()
        return
    
    if MULTI_THREAD >= 2:
        p = Pool(MULTI_THREAD)
    else:
        p = None      
        
    if USE_STATS_FIELD:
        accum = boardocr.OCRStatus()
        lastLines = None #use to reset accumulator
        if MULTI_THREAD >= 2: #run Field_OCR as fast as possible; unlock from mainthread.
            thread = threading.Thread(target=statsFieldMulti, args=(accum,p))
            thread.start()        
    
    scoreFixer = ScoreFixer(SCORE_PATTERN)
    
    while True:
        # outer loop waits for the window to exists
        frame_start = time.time()
        frame_end = frame_start + RATE
        hwnd = getWindow()

        if not hwnd:
            while time.time() < frame_end:
                time.sleep(0.001)
            continue

        while checkWindow(hwnd):
            # inner loop gets fresh data for just the desired window
            frame_start  = time.time()
            frame_end = frame_start + RATE

            result = {}
            rawTasks = []
            rawTasks.append((captureAndOCR,(SCORE_COORDS,hwnd,SCORE_PATTERN,"score")))
            rawTasks.append((captureAndOCR,(LINES_COORDS,hwnd,LINES_PATTERN,"lines")))
            rawTasks.append((captureAndOCR,(LEVEL_COORDS,hwnd,LEVEL_PATTERN,"level")))

            if STATS_ENABLE:
                if STATS_METHOD == 'TEXT':
                    rawTasks.append((captureAndOCR,(STATS_COORDS[key],hwnd,STATS_PATTERN,key,False,True)))
                elif MULTI_THREAD == 1: #run FIELD_PIECE in main thread if necessary
                    rawTasks.append((captureAndOCRBoard, (STATS2_COORDS, hwnd)))

            # run all tasks (in separate threads if MULTI_THREAD is enabled)
            result = runTasks(p, rawTasks)

            #fix score's first digit. 8 to B and B to 8 depending on last state.
            result['score'] = scoreFixer.fix(result['score'])

            # update our accumulator
            if USE_STATS_FIELD:
                if lastLines is None and result['lines'] == '000':
                    accum.reset()

                if MULTI_THREAD == 1:
                    accum.update(result['board_ocr'], frame_start)
                    del result['board_ocr']

                result.update(accum.toDict())
                lastLines = result['lines']

                # warning for USE_STATS_FIELD if necessary
                if MULTI_THREAD == 1 and time.time() > frame_start + 1/60.0:
                    print ("Warning, not scanning field fast enough")

            onCap(result)

            while time.time() < frame_end:
                time.sleep(0.001)

def compile_tasks(args):
    if ()



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

    parser.add_argument('--fields', action='store',
                       default='',
                       help='Supply list of areas IDs to capture. Comma separated list.')

    args = parser.parse_args()


    if args.fields:
        if re.search('^[a-z_]+(,[a-z_]+)*$', args.capture):
            fields = args.fields
        else:
            eprint('Invalid capture argument format', args.capture)
            sys.exit(2)

        fields = set(fields.split(','))

        if not fields.issubset(set([key for key in base_config.fields])):
            eprint('Invalid capture area id', args.capture)
            sys.exit(3)

        # override args to the validated set so we don't do it again later
        args.fields = fields
    else:
        args.fields = set([k for k, v in config.fields.items()])


    return args



if __name__ == '__main__':
    args = getCLIArguments()

    validate_config(args)

    if args.calibrate:
        import calibrate
        calibrate.run(args)

    else:
        compile_tasks(args)

        client = TCPClient.CreateClient('127.0.0.1',3338)
        cachedSender = CachedSender(client)
        
        main(cachedSender.sendResult)
    

        
