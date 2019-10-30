from config import config

if config.netProtocol == 'AUTOBAHN' or config.netProtocol == 'AUTOBAHN_V2':
	import Networking.AutoBahnClient as NetClient
elif config.netProtocol == 'FILE':
	import Networking.FileClient as NetClient
else:
	import Networking.TCPClient as NetClient
