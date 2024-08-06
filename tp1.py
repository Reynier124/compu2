import multiprocessing as mp
from PIL import Image, ImageFilter
import sys
import signal
from tkinter import filedialog
import mmap
import numpy as np

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

    def join_images(self, shared_mmap, queue):
        new_image = Image.new('RGB', (self.length, self.height))
        y_offset = 0
        
        for _ in range(self.n):
            index = queue.get()
            division_height = self.divisions[index].size[1]
            division_size = self.length * division_height * 3
            start = index * division_size
            end = start + division_size

            if end > len(shared_mmap):
                end = len(shared_mmap)  # Ensure end does not exceed the mmap size

            # Debug: Print sizes and bounds
            print(f"Joining image - index={index}, start={start}, end={end}, size={division_size}")

            division_bytes = shared_mmap[start:end]
            # Convert bytes to image correctly
            division = Image.frombytes('RGB', (self.length, division_height), bytes(division_bytes))
            new_image.paste(division, (0, y_offset))
            y_offset += division_height
        
        new_image.save("processed_image.png")

    def image_processing(self):
        queue = mp.Queue()
        total_size = self.length * self.height * 3
        with mmap.mmap(-1, total_size) as shared_mmap:

            def worker(division, index, shared_mmap, queue):
                processed_image = self.filter(division)
                division_bytes = np.array(processed_image).tobytes()
                division_height = division.size[1]
                division_size = self.length * division_height * 3
                start = index * division_size
                end = start + len(division_bytes)

                if end > len(shared_mmap):
                    end = len(shared_mmap)  # Ensure end does not exceed the mmap size

                # Debug: Print sizes and bounds
                print(f"Worker {index}: start={start}, end={end}, len(division_bytes)={len(division_bytes)}")

                # Ensure we're writing exactly the expected number of bytes
                write_length = min(len(division_bytes), end - start)
                shared_mmap[start:start + write_length] = division_bytes[:write_length]
                queue.put(index)

            for i, division in enumerate(self.divisions):
                p = mp.Process(target=worker, args=(division, i, shared_mmap, queue))
                self.processes.append(p)
                p.start()

            for p in self.processes:
                p.join()

            self.join_images(shared_mmap, queue)

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
