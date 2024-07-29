from PIL import Image, ImageFilter
import multiprocessing as mp
import signal
import sys
from tkinter import filedialog
import tkinter as tk
import time

class ImageProcessing:
    
    def __init__(self):
        self.n = mp.cpu_count()
        self.image = None
        self.length = 0
        self.height = 0
        self.divisions = []
        self.processes = []  # Track worker processes

    def search_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            image = Image.open(file_path)
            self.image = image
            self.length, self.height = self.image.size

    def filter(self, division):
        return division.filter(ImageFilter.CONTOUR)
    
    def division(self):
        division_height = self.height // self.n
        divisions = []
        for i in range(self.n):
            y_init = i * division_height
            y_end = (i + 1) * division_height if (i + 1) * division_height <= self.height else self.height
            divisions.append(self.image.crop((0, y_init, self.length, y_end)))
        self.divisions = divisions

    def join_images(self, processed_divisions):
        new_image = Image.new('RGB', (self.length, self.height))
        i = 0
        for division in processed_divisions:
            new_image.paste(division, (0, i))
            i += division.size[1]
        new_image.save("processed_image.png")

    def image_processing(self):
        processed_flags = mp.Array('b', self.n)  # Shared array of flags

        def worker(division, index, pipe_conn):
            processed_image = self.filter(division)
            pipe_conn.send((index, processed_image))
            pipe_conn.close()
            processed_flags[index] = 1  # Mark this division as processed

        parent_connections = []
        for i in range(self.n):
            parent_conn, child_conn = mp.Pipe()
            parent_connections.append(parent_conn)
            p = mp.Process(target=worker, args=(self.divisions[i], i, child_conn))
            self.processes.append(p)
            p.start()
            if i == 4:
                time.sleep(20)
        # Collect results from pipes
        processed_divisions = [None] * self.n
        for parent_conn in parent_connections:
            index, processed_image = parent_conn.recv()
            processed_divisions[index] = processed_image

        # Wait for all processes to complete
        for p in self.processes:
            p.join()

        self.join_images(processed_divisions)

    def cleanup(self, signum, frame):
        print("Interrupt received, cleaning up...")
        for p in self.processes:
            if p.is_alive():
                p.terminate()  # Terminate the process
        sys.exit(0)  # Exit the program
        
    def run(self):
        signal.signal(signal.SIGINT, img_proc.cleanup)
        self.search_image()
        self.division()
        self.image_processing()

# Create and run the image processing instance
if __name__ == '__main__':
    img_proc = ImageProcessing()
    # Register the SIGINT signal handler
    img_proc.run()
