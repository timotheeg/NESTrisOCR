import sys
import numpy as np
import cv2

device_index = int(sys.argv[1])

cap = cv2.VideoCapture(device_index)

ret, frame = cap.read()

if ret:
	print('Capture details for device', device_index)

	for idx in range(0, 21):
		print(idx, cap.get(idx))

	while(True):
		ret, frame = cap.read()
		cv2.imshow('frame',frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
else:
	print('Capture device is not readable', device_index)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
