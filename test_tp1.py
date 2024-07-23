# test_tp1.py
import unittest
from unittest.mock import patch, MagicMock, ANY
from PIL import Image, ImageFilter
from tp1 import Image_processing

class Tests_Image_processing(unittest.TestCase):
    def setUp(self):
        self.process = Image_processing()
    
    @patch('tp1.filedialog.askopenfilename')
    @patch('tp1.Image.open')
    def test_search_image(self, mock_open, mock_askopenfilename):
        # Configurar el mock para devolver una ruta de archivo falsa
        mock_askopenfilename.return_value = "fake_path.png"
        
        # Crear una imagen simulada
        mock_image = MagicMock()
        mock_image.size = (100, 200)
        mock_open.return_value = mock_image
        
        # Ejecutar la función
        self.process.search_image()
        
        # Verificar que se llamó a askopenfilename y open con la ruta correcta
        mock_askopenfilename.assert_called_once_with(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        mock_open.assert_called_once_with("fake_path.png")
        
        # Verificar que la imagen y sus dimensiones se asignaron correctamente
        self.assertEqual(self.process.image, mock_image)
        self.assertEqual(self.process.length, 100)
        self.assertEqual(self.process.higth, 200)

    def test_filter(self):
        # Crear una imagen simulada
        mock_image = MagicMock()
        
        # Ejecutar la función de filtro
        filtered_image = self.process.filter(mock_image)
        
        # Verificar que se llamó a filter con el filtro correcto
        mock_image.filter.assert_called_once_with(ANY)
    
    @patch.object(Image_processing, 'image', new_callable=MagicMock)
    def test_division(self, mock_image):
        # Configurar el tamaño de la imagen
        self.process.length = 100
        self.process.higth = 200
        self.process.n = 4
        
        # Configurar el mock para la función crop
        mock_image.size = (100, 200)
        mock_image.crop.side_effect = lambda box: f"Crop({box})"
        
        # Ejecutar la función de división
        divisions = self.process.division()
        
        # Verificar las divisiones esperadas
        expected_divisions = [
            'Crop((0, 0, 100, 50))',
            'Crop((0, 50, 100, 100))',
            'Crop((0, 100, 100, 150))',
            'Crop((0, 150, 100, 200))'
        ]
        
        self.assertEqual(divisions, expected_divisions)
        self.assertEqual(mock_image.crop.call_count, 4)

if __name__ == '__main__':
    unittest.main()
