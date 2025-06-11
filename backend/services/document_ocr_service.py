"""
Enhanced service for extracting text from images within documents using OCR.
Improved preprocessing and multiple OCR approaches for better accuracy.
"""
import os
import tempfile
import fitz  # PyMuPDF
import easyocr
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import List, Dict, Any, Tuple
from pathlib import Path
import zipfile
from docx import Document
import io


class DocumentOCRService:
    """Enhanced service for extracting text from images within uploaded documents."""
    
    def __init__(self):
        """Initialize the Document OCR service."""
        self.easyocr_reader = None
        self.supported_languages = ['en', 'fr', 'es', 'de']  # Extended language support
        
    def _get_easyocr_reader(self, languages: List[str] = ['en', 'fr']):
        """Get or initialize EasyOCR reader with specified languages."""
        if self.easyocr_reader is None:
            try:
                self.easyocr_reader = easyocr.Reader(languages, gpu=False)
                print(f"EasyOCR initialized with languages: {languages}")
            except Exception as e:
                print(f"Error initializing EasyOCR: {e}")
                raise e
        return self.easyocr_reader
    
    def _enhance_image_quality(self, image_array: np.ndarray) -> List[np.ndarray]:
        """
        Apply multiple enhancement techniques to improve OCR accuracy.
        Returns multiple processed versions of the image.
        
        Args:
            image_array: Input image as numpy array
            
        Returns:
            List of enhanced image versions
        """
        enhanced_images = []
        
        try:
            # Convert to PIL Image for initial processing
            if len(image_array.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image_array)
            
            # Version 1: Original with basic cleanup
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
            enhanced_images.append(gray)
            
            # Version 2: Enhanced contrast and sharpness
            enhancer = ImageEnhance.Contrast(pil_image)
            contrast_enhanced = enhancer.enhance(2.0)  # Increase contrast
            
            enhancer = ImageEnhance.Sharpness(contrast_enhanced)
            sharp_enhanced = enhancer.enhance(2.0)  # Increase sharpness
            
            # Convert back to numpy array
            enhanced_array = np.array(sharp_enhanced)
            if len(enhanced_array.shape) == 3:
                enhanced_array = cv2.cvtColor(enhanced_array, cv2.COLOR_RGB2GRAY)
            enhanced_images.append(enhanced_array)
            
            # Version 3: Noise reduction and adaptive thresholding
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            adaptive_thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 15, 10
            )
            enhanced_images.append(adaptive_thresh)
            
            # Version 4: Morphological operations for text cleanup
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            morphed = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
            morphed = cv2.morphologyEx(morphed, cv2.MORPH_OPEN, kernel)
            enhanced_images.append(morphed)
            
            # Version 5: High contrast binary
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            enhanced_images.append(binary)
            
            print(f"Generated {len(enhanced_images)} enhanced image versions")
            return enhanced_images
            
        except Exception as e:
            print(f"Error enhancing image: {e}")
            # Return original image if enhancement fails
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
            return [gray]
    
    def _extract_text_with_multiple_methods(self, image_array: np.ndarray, languages: List[str] = ['en', 'fr']) -> Dict[str, Any]:
        """
        Extract text using multiple OCR methods and choose the best result.
        
        Args:
            image_array: Image as numpy array
            languages: Languages for OCR
            
        Returns:
            Dictionary with best extraction results
        """
        best_result = {"text": "", "confidence": 0, "method": "none"}
        
        # Get multiple enhanced versions of the image
        enhanced_images = self._enhance_image_quality(image_array)
        
        for i, enhanced_img in enumerate(enhanced_images):
            try:
                # Method 1: EasyOCR
                try:
                    reader = self._get_easyocr_reader(languages)
                    easyocr_results = reader.readtext(enhanced_img)
                    
                    easyocr_text = ""
                    easyocr_confidences = []
                    
                    for (bbox, text, confidence) in easyocr_results:
                        if confidence > 0.2:  # Lower threshold for difficult images
                            easyocr_text += text + " "
                            easyocr_confidences.append(confidence)
                    
                    easyocr_avg_conf = np.mean(easyocr_confidences) if easyocr_confidences else 0
                    
                    if easyocr_avg_conf > best_result["confidence"] and len(easyocr_text.strip()) > 10:
                        best_result = {
                            "text": easyocr_text.strip(),
                            "confidence": easyocr_avg_conf,
                            "method": f"EasyOCR (enhancement v{i+1})"
                        }
                        print(f"EasyOCR v{i+1} confidence: {easyocr_avg_conf:.3f}, text length: {len(easyocr_text)}")
                
                except Exception as e:
                    print(f"EasyOCR failed on version {i+1}: {e}")
                
                # Method 2: Tesseract with different configurations
                try:
                    # Convert language codes for Tesseract
                    tesseract_lang = '+'.join([self._convert_to_tesseract_lang(lang) for lang in languages])
                    
                    # Try different PSM modes for Tesseract
                    psm_modes = [6, 8, 13, 7, 3]  # Different page segmentation modes
                    
                    for psm in psm_modes:
                        config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,:-'
                        
                        pil_img = Image.fromarray(enhanced_img)
                        tesseract_text = pytesseract.image_to_string(pil_img, lang=tesseract_lang, config=config)
                        
                        # Get confidence data
                        data = pytesseract.image_to_data(
                            pil_img, lang=tesseract_lang, config=config, output_type=pytesseract.Output.DICT
                        )
                        
                        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                        tesseract_avg_conf = (np.mean(confidences) / 100) if confidences else 0
                        
                        if tesseract_avg_conf > best_result["confidence"] and len(tesseract_text.strip()) > 10:
                            best_result = {
                                "text": tesseract_text.strip(),
                                "confidence": tesseract_avg_conf,
                                "method": f"Tesseract PSM{psm} (enhancement v{i+1})"
                            }
                            print(f"Tesseract PSM{psm} v{i+1} confidence: {tesseract_avg_conf:.3f}, text length: {len(tesseract_text)}")
                
                except Exception as e:
                    print(f"Tesseract failed on version {i+1}: {e}")
            
            except Exception as e:
                print(f"OCR failed on version {i+1}: {e}")
        
        print(f"Best OCR result: {best_result['method']} with confidence {best_result['confidence']:.3f}")
        return best_result
    
    def _convert_to_tesseract_lang(self, easyocr_lang: str) -> str:
        """Convert EasyOCR language code to Tesseract language code."""
        lang_mapping = {
            'en': 'eng',
            'fr': 'fra',
            'es': 'spa',
            'de': 'deu',
            'it': 'ita',
            'pt': 'por'
        }
        return lang_mapping.get(easyocr_lang, 'eng')
    
    def extract_images_from_pdf(self, pdf_path: str) -> List[Tuple[np.ndarray, int, Dict[str, Any]]]:
        """
        Extract images from PDF document with metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of tuples (image_array, page_number, image_metadata)
        """
        images = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get images on this page
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        # Get image metadata
                        img_metadata = {
                            "width": pix.width,
                            "height": pix.height,
                            "colorspace": pix.colorspace.name if pix.colorspace else "unknown",
                            "xref": xref
                        }
                        
                        # Skip very small images (likely decorative)
                        if pix.width < 100 or pix.height < 50:
                            print(f"Skipping small image {img_index} on page {page_num + 1}: {pix.width}x{pix.height}")
                            pix = None
                            continue
                        
                        # Convert to numpy array
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            img_array = np.frombuffer(img_data, dtype=np.uint8)
                            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                            
                            if image is not None:
                                images.append((image, page_num + 1, img_metadata))
                                print(f"Extracted image {img_index} from page {page_num + 1}: {pix.width}x{pix.height}")
                        
                        pix = None  # Free memory
                        
                    except Exception as e:
                        print(f"Error extracting image {img_index} from page {page_num + 1}: {e}")
                        continue
            
            doc.close()
            print(f"Extracted {len(images)} images from PDF")
            
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {e}")
        
        return images
    
    def extract_images_from_docx(self, docx_path: str) -> List[Tuple[np.ndarray, str, Dict[str, Any]]]:
        """
        Extract images from DOCX document with metadata.
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            List of tuples (image_array, location_info, image_metadata)
        """
        images = []
        
        try:
            with zipfile.ZipFile(docx_path, 'r') as docx_zip:
                image_files = [f for f in docx_zip.namelist() if f.startswith('word/media/')]
                
                for img_file in image_files:
                    try:
                        img_data = docx_zip.read(img_file)
                        
                        # Basic metadata
                        img_metadata = {
                            "file_size": len(img_data),
                            "source_path": img_file
                        }
                        
                        # Convert to numpy array
                        img_array = np.frombuffer(img_data, dtype=np.uint8)
                        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        
                        if image is not None:
                            img_metadata.update({
                                "width": image.shape[1],
                                "height": image.shape[0]
                            })
                            
                            # Skip very small images
                            if image.shape[1] < 100 or image.shape[0] < 50:
                                print(f"Skipping small image {img_file}: {image.shape[1]}x{image.shape[0]}")
                                continue
                            
                            images.append((image, f"Image from {img_file}", img_metadata))
                            print(f"Extracted image from {img_file}: {image.shape[1]}x{image.shape[0]}")
                            
                    except Exception as e:
                        print(f"Error extracting image {img_file}: {e}")
                        continue
            
            print(f"Extracted {len(images)} images from DOCX")
            
        except Exception as e:
            print(f"Error processing DOCX {docx_path}: {e}")
        
        return images
    
    def process_document_with_ocr(self, file_path: str, languages: List[str] = ['en', 'fr']) -> str:
        """
        Process a document and extract text from any images it contains using enhanced OCR.
        
        Args:
            file_path: Path to the document file
            languages: Languages for OCR
            
        Returns:
            Extracted text from all images in the document
        """
        file_extension = Path(file_path).suffix.lower()
        extracted_text = ""
        
        try:
            if file_extension == '.pdf':
                print(f"Processing PDF with enhanced OCR: {file_path}")
                images = self.extract_images_from_pdf(file_path)
                
                for image_array, page_num, metadata in images:
                    print(f"Processing image on page {page_num} ({metadata['width']}x{metadata['height']})")
                    
                    result = self._extract_text_with_multiple_methods(image_array, languages)
                    
                    if result["text"].strip() and result["confidence"] > 0.3:
                        extracted_text += f"\n--- Text from image on page {page_num} (Method: {result['method']}, Confidence: {result['confidence']:.2f}) ---\n"
                        extracted_text += result["text"] + "\n"
                        print(f"Successfully extracted {len(result['text'])} characters from page {page_num}")
                    else:
                        print(f"Low quality text extraction on page {page_num} (confidence: {result['confidence']:.2f})")
            
            elif file_extension in ['.docx', '.doc']:
                print(f"Processing DOCX with enhanced OCR: {file_path}")
                images = self.extract_images_from_docx(file_path)
                
                for image_array, location, metadata in images:
                    print(f"Processing {location} ({metadata['width']}x{metadata['height']})")
                    
                    result = self._extract_text_with_multiple_methods(image_array, languages)
                    
                    if result["text"].strip() and result["confidence"] > 0.3:
                        extracted_text += f"\n--- Text from {location} (Method: {result['method']}, Confidence: {result['confidence']:.2f}) ---\n"
                        extracted_text += result["text"] + "\n"
                        print(f"Successfully extracted {len(result['text'])} characters from {location}")
                    else:
                        print(f"Low quality text extraction from {location} (confidence: {result['confidence']:.2f})")
            
            else:
                print(f"File type {file_extension} not supported for image extraction")
                return ""
        
        except Exception as e:
            print(f"Error processing document {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return ""
        
        if extracted_text.strip():
            print(f"Total extracted text length: {len(extracted_text)} characters")
        else:
            print("No text was successfully extracted from images")
        
        return extracted_text.strip()
    
    def should_process_for_images(self, file_path: str) -> bool:
        """
        Check if a file type might contain images that need OCR processing.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file might contain images
        """
        file_extension = Path(file_path).suffix.lower()
        image_capable_formats = ['.pdf', '.docx', '.doc']
        return file_extension in image_capable_formats