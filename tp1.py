from PIL import Image, ImageFilter
import os, signal, mmap, time 
import multiprocessing as mp
from tkinter import filedialog
import tkinter as tk

class Image_processing():
    
    def __init__(self):
        self.n = mp.cpu_count()
        self.image = 0
        self.length = 0
        self.higth = 0
        
    def search_image(self):
        # Abre un cuadro de diálogo para seleccionar una imagen
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        
        if file_path:
            # Cargar la imagen usando Pillow
            image = Image.open(file_path)
            self.image = image
            self.length, self.higth = self.image.size
            
# Uso de la función (por ejemplo, dentro de una clase)
# image = self.search_image()
# image.show()  # Esto mostrará la imagen seleccionada

    def filter(self,division):
        return division.filter(ImageFilter.GaussianBlur(5))
    
    def division(self):
        division_higth = self.higth//self.n
        divisions = []
        for i in range(self.n):
            y_init = i*division_higth
            y_end = (i+1)*division_higth if i != division_higth else self.higth
            divisions.append(self.image.crop((0,y_init,self.length,y_end)))
        return divisions 
    
     