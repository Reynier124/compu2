import multiprocessing as mp
from PIL import Image, ImageFilter
import numpy as np
import sys
import signal
import tempfile
import os
from tkinter import filedialog
import mmap

class ImageProcessing:
    def __init__(self):
        self.n = mp.cpu_count()
        self.image = None
        self.length = 0
        self.height = 0
        self.divisions = []
        self.processes = []
        self.temp_file = None

    def search_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.image = Image.open(file_path)
            self.length, self.height = self.image.size

    def filter(self, division):
        return division.filter(ImageFilter.CONTOUR)

    def division(self):
        # Convertir la imagen a un array de NumPy
        image_array = np.array(self.image)
        division_height = self.height // self.n

        self.divisions = [
            image_array[i * division_height:(i + 1) * division_height]
            for i in range(self.n)
        ]

    def join_images(self, shared_array):
        # Crear una nueva imagen usando NumPy
        total_height = self.height
        new_image_array = np.zeros((total_height, self.length, 3), dtype=np.uint8)
        y_offset = 0

        for i in range(self.n):
            division_height = self.divisions[i].shape[0]
            start = i * self.length * division_height * 3
            end = (i + 1) * self.length * division_height * 3
            division_bytes = shared_array[start:end]
            division_array = np.frombuffer(division_bytes, dtype=np.uint8).reshape((division_height, self.length, 3))
            new_image_array[y_offset:y_offset + division_height] = division_array
            y_offset += division_height

        new_image = Image.fromarray(new_image_array)
        new_image.save("processed_image.png")

    def image_processing(self):
        queue = mp.Queue()

        # Convertir la imagen a bytes y obtener su tamaño
        image_array = np.array(self.image)
        image_bytes = image_array.tobytes()
        total_size = len(image_bytes)

        # Crear un archivo temporal para mmap
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            self.temp_file = temp_file.name
            with open(self.temp_file, 'wb') as f:
                f.write(b'\x00' * total_size)  # Inicializar el archivo con el tamaño total

        def worker(division_array, index):
            processed_image = self.filter(Image.fromarray(division_array))
            division_array = np.array(processed_image)
            division_bytes = division_array.tobytes()
            with open(self.temp_file, 'r+b') as f:
                start = index * division_array.size
                f.seek(start)
                f.write(division_bytes)
            queue.put(index)

        for i, division in enumerate(self.divisions):
            p = mp.Process(target=worker, args=(division, i))
            self.processes.append(p)
            p.start()

        processed_indices = []
        for _ in range(self.n):
            index = queue.get()
            processed_indices.append(index)

        # Asegurar que todos los procesos han terminado
        for p in self.processes:
            p.join()

        # Ordenar los índices procesados para asegurarse de que se unan en orden
        processed_indices.sort()

        # Usar mmap para leer el archivo temporal
        with open(self.temp_file, 'r+b') as f:
            shared_array = mmap.mmap(f.fileno(), 0)
            self.join_images(shared_array)
            shared_array.close()

        # Eliminar el archivo temporal
        os.remove(self.temp_file)

    def cleanup(self, signum, frame):
        print("Interrupt received, cleaning up...")
        for p in self.processes:
            if p.is_alive():
                p.terminate()
        if self.temp_file and os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.cleanup)
        self.search_image()
        self.division()
        self.image_processing()

if __name__ == '__main__':
    img_proc = ImageProcessing()
    img_proc.run()
