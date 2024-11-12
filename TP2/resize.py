from PIL import ImageOps
import sys
import signal

class Resize_image():

    def __init__(self, image, scale):
        self._image = image
        self._scale = scale

    def rescale(self):
        result = ImageOps.scale(self._image, self._scale)
        return result

    def cleanup(self, signum, frame):
        print("Interrupt received, cleaning up...")
        sys.exit(0)
    
    def run(self):
        signal.signal(signal.SIGINT, self.cleanup)
        return self.rescale()


