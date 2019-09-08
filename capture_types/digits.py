def captureAndOCR(hwnd, coords, digitPattern):
    t = time.time()
    img = WindowCapture.ImageCapture(coords,hwnd)
    return taskName, scoreImage(img,digitPattern,draw,red)

def extractAndOCR(img, coords, digitPattern)