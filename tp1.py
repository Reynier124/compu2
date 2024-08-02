import multiprocessing as mp
from PIL import Image, ImageFilter
import sys
import signal
import time
from tkinter import filedialog

class ImageProcessing:

    def __init__(self):
        self.n = mp.cpu_count()
        self.image = None
        self.length = 0
        self.height = 0
        self.divisions = []
        self.processes = []

    def search_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.image = Image.open(file_path)
            self.length, self.height = self.image.size

    def filter(self, division):
        return division.filter(ImageFilter.CONTOUR)
    
    def division(self):
        division_height = self.height // self.n
        self.divisions = [
            self.image.crop((0, i * division_height, self.length, (i + 1) * division_height))
            for i in range(self.n)
        ]

    def join_images(self, shared_array):
        total_height = sum([self.divisions[i].size[1] for i in range(self.n)])
        new_image = Image.new('RGB', (self.length, total_height))
        y_offset = 0
        for i in range(self.n):
            division_bytes = bytes(shared_array[i * self.length * self.divisions[i].size[1] * 3:(i + 1) * self.length * self.divisions[i].size[1] * 3])
            division = Image.frombytes('RGB', (self.length, self.divisions[i].size[1]), division_bytes)
            new_image.paste(division, (0, y_offset))
            y_offset += division.size[1]
        new_image.save("processed_image.png")

    def image_processing(self):
        queue = mp.Queue()
        shared_array = mp.Array('B', self.length * self.height * 3) 

        def worker(division, index):
            processed_image = self.filter(division)
            division_bytes = processed_image.tobytes()
            start = index * self.length * division.size[1] * 3
            shared_array[start:start + len(division_bytes)] = division_bytes
            queue.put(index)  
            
        for i, division in enumerate(self.divisions):
            p = mp.Process(target=worker, args=(division, i))
            self.processes.append(p)
            p.start()

        for _ in range(self.n):
            queue.get()  

        for p in self.processes:
            p.join()

        self.join_images(shared_array)

    def cleanup(self, signum, frame):
        print("Interrupt received, cleaning up...")
        for p in self.processes:
            if p.is_alive():
                p.terminate()
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.cleanup)
        self.search_image()
        self.division()
        self.image_processing()

if __name__ == '__main__':
    img_proc = ImageProcessing()
    img_proc.run()