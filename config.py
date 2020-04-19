import configparser
from configupdater import ConfigUpdater
from ast import literal_eval #safe version of eval
class Configuration:
    def __init__(self, filename, updater):
        self._filename = filename
        self._updater = updater
        self.initFromParser()
        
    def initFromParser(self):
        parser = configparser.ConfigParser()
        parser.read(self._filename)
        #player
        self.player_name = parser['player']['name']
        self.twitch_url = parser['player']['twitch']        
        #performance
        self.threads = literal_eval(parser['performance']['multi_thread'])
        self.hexSupport = parser['performance'].getboolean('support_hex_score') 
        self.scanRate = literal_eval(parser['performance']['scan_rate'])
        self.tasksCaptureMethod = parser['performance']['tasks_capture_method']
        
        #stats
        self.capture_stats = parser['stats'].getboolean('read_stats')
        self.stats_method = parser['stats']['stats_method'].upper()
        
        #calibration
        self.captureMethod = parser['calibration']['capture_method']
        self.WINDOW_NAME = parser['calibration']['window_name']
        self.CAPTURE_COORDS = literal_eval(parser['calibration']['game_coords'])        
        self.scorePerc = literal_eval(parser['calibration']['scoreperc'])
        self.linesPerc = literal_eval(parser['calibration']['linesperc'])
        self.levelPerc = literal_eval(parser['calibration']['levelperc'])
        self.statsPerc = literal_eval(parser['calibration']['statsperc'])
        
        #field
        self.capture_field = parser['calibration'].getboolean('read_field')
        self.fieldPerc = literal_eval(parser['calibration']['fieldperc'])

        self.colorMethod = parser['calibration']['color_method']
        self.color1Perc = literal_eval(parser['calibration']['color1perc'])
        self.color2Perc = literal_eval(parser['calibration']['color2perc'])
        self.blackPerc = literal_eval(parser['calibration']['blackperc'])
        self.whitePerc = literal_eval(parser['calibration']['whiteperc'])

        #preview
        self.capture_preview = parser['calibration'].getboolean('read_preview')
        self.previewPerc = literal_eval(parser['calibration']['previewperc'])
        
        #das trainer fields
        self.capture_das_trainer = parser['calibration'].getboolean('capture_das_trainer')
        self.currentPiecePerc = literal_eval(parser['calibration']['currentpieceperc'])
        self.currentPieceDasPerc = literal_eval(parser['calibration']['currentpiecedasperc'])
        
        #calculate stats2Perc from field
        self.stats2Perc = self.subImage(self.fieldPerc)

        #network
        self.host = parser['network']['host']
        self.port = literal_eval(parser['network']['port'])
        self.netProtocol = parser['network']['protocol']
        
        #debug
        self.printPacket = literal_eval(parser['debug']['print_packet'])

    # gets the 2x4 region out of the fieldPerc
    def subImage(self, rect):
        #return middle 4 / 10 x values and  2 / 20 y values
        tileX = rect[2]/10.0
        tileY = rect[3]/20.0
        return [rect[0] + tileX * 3,
                rect[1],
                tileX * 4,
                tileY * 2]

    def refresh(self):
        self._updater.update_file()
        self.initFromParser()
    
    def setItem(self,section,var,value):
        self._updater[section][var] = value
        self.refresh()
        
    def setPlayerName(self, name):
        self.setItem('player','name', name)
    
    def setTwitchURL(self, url):
        self.setItem('player','twitch', url)    
    
    def setThreads(self, threads):
        self.setItem('performance','multi_thread', threads)    
    
    def setHexSupport(self, support):
        self.setItem('performance','support_hex_score', support)    
    
    def setCaptureStats(self, toCapture):
        self.setItem('stats','read_stats', toCapture)    
    
    def setStatsMethod(self, val):
        self.setItem('stats','stats_method', val)    
    
    def setWindowName(self, val):
        self.setItem('calibration','window_name', val)    
    
    def setGameCoords(self, val):
        self.setItem('calibration','game_coords', val)    
        
    def setScorePerc(self, val):
        self.setItem('calibration','scoreperc', val)    
        
    def setLinesPerc(self, val):
        self.setItem('calibration','linesperc', val)    
    
    def setLevelPerc(self, val):
        self.setItem('calibration','levelperc', val)    
    
    def setStatsPerc(self, val):
        self.setItem('calibration','statsperc', val)    
    
    def setCaptureField(self,val):
        self.setItem('calibration','read_field', val)

    def setCapturePreview(self,val):
        self.setItem('calibration','read_preview', val)
        
    def setFieldPerc(self, val):
        self.setItem('calibration','fieldperc', val)    

    def setColor1Perc(self, val):
        self.setItem('calibration','color1perc', val)

    def setColor2Perc(self, val):
        self.setItem('calibration','color2perc', val)

    def setPreviewPerc(self, val):
        self.setItem('calibration','previewperc', val)    

    def setCaptureDasTrainer(self, val):
        self.setItem('calibration', 'capture_das_trainer', val)

    def setCurrentPiecePerc(self, val):
        self.setItem('calibration', 'currentpieceperc', val)

    def setCurrentPieceDasPerc(self, val):
        self.setItem('calibration', 'currentpiecedasperc', val)

    def setHost(self, val):
        self.setItem('network','host', val)    
    
    def setPort(self, val):
        self.setItem('network','port', val)    
    
    def setNetProtocol(self, val):
        self.setItem('network','protocol', val)
    
updater = ConfigUpdater()        
updater.read('config.ini')

config = Configuration('config.ini', updater)


