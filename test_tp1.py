# test_tp1.py
import unittest
from unittest.mock import patch, MagicMock, call
from PIL import Image, ImageFilter
from tp1 import Image_processing

class Tests_Image_processing(unittest.TestCase):
    def setUp(self):
        self.process = Image_processing()
    
    @patch('tp1.filedialog.askopenfilename')
    @patch('tp1.Image.open')
    def test_search_image(self, mock_open, mock_askopenfilename):
        mock_askopenfilename.return_value = "fake_path.png"
        mock_image = MagicMock()
        mock_image.size = (100, 200)
        mock_open.return_value = mock_image
        
        self.process.search_image()
        
        mock_askopenfilename.assert_called_once_with(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        mock_open.assert_called_once_with("fake_path.png")
        self.assertEqual(self.process.image, mock_image)
        self.assertEqual(self.process.length, 100)
        self.assertEqual(self.process.height, 200)

    @patch('tp1.Image.Image.filter')
    def test_filter(self, mock_filter):
        mock_image = MagicMock(spec=Image.Image)
        mock_filter.return_value = mock_image
        filtered_image = self.process.filter(mock_image)
        mock_filter.assert_called_once_with(ImageFilter.CONTOUR)
    
    def test_division(self):
        self.process.image = MagicMock(spec=Image.Image)
        self.process.image.size = (100, 200)
        self.process.length = 100
        self.process.height = 200
        self.process.n = 4
        
        def mock_crop(box):
            return MagicMock(spec=Image.Image)
        
        self.process.image.crop = mock_crop
        
        # Ejecuta la división
        self.process.division()
        
        # Verifica las llamadas al método crop
        expected_calls = [
            call((0, 0, 100, 50)),
            call((0, 50, 100, 100)),
            call((0, 100, 100, 150)),
            call((0, 150, 100, 200))
        ]
        actual_calls = self.process.image.crop.call_args_list
        self.assertEqual(actual_calls, expected_calls)

    @patch('tp1.Image_processing.division')
    @patch('tp1.Image_processing.filter')
    @patch('PIL.Image.Image.save')
    def test_image_processing(self, mock_save, mock_filter, mock_division):
        # Configura los mocks
        mock_division.return_value = [MagicMock(spec=Image.Image) for _ in range(self.process.n)]
        mock_filter.return_value = MagicMock(spec=Image.Image)
        mock_save.return_value = None
        
        # Ejecuta el procesamiento de la imagen
        self.process.image_processing()
        
        # Verifica que division fue llamada
        mock_division.assert_called_once()
        
        # Verifica que filter fue llamada con cada división
        self.assertEqual(mock_filter.call_count, self.process.n)
        
        # Verifica que save fue llamada
        mock_save.assert_called_once_with("processed_image.png")

if __name__ == '__main__':
    unittest.main()
