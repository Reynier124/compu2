from PIL import Image, ImageFilter
import os, signal, mmap, time 
import multiprocessing as mp
from tkinter import filedialog
import tkinter as tk

class Image_processing():
    
    def __init__(self):
        self.n = mp.cpu_count()
        self.image = None
        self.length = 0
        self.height = 0
        self.divisions = []
        
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
        return new_image

    def image_processing(self):
        with mp.Pool(self.n) as pool:
            processed_images = pool.map(self.filter, self.divisions)
        final_image = self.join_images(processed_images)
        final_image.save("processed_image.png")
    
    def run(self):
        self.search_image()
        self.division()
        self.image_processing()
