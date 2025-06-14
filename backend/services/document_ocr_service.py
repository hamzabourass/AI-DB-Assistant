"""
OCR service using EasyOCR for document image text extraction.
"""
import os
import fitz  # PyMuPDF
import easyocr
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import List, Dict, Any, Tuple
from pathlib import Path
import zipfile


class DocumentOCRService:
    """Enhanced service for extracting text from images within documents using OCR."""
    
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
            
            print(f"Generated {len(enhanced_images)} enhanced image versions")
            return enhanced_images
            
        except Exception as e:
            print(f"Error enhancing image: {e}")
            # Return original image if enhancement fails
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
            return [gray]
    
    def _extract_text_with_multiple_methods(self, image_array: np.ndarray, languages: List[str] = ['en', 'fr']) -> Dict[str, Any]:
        """
        Extract text using EasyOCR and choose the best result.
        """
        best_result = {"text": "", "confidence": 0, "method": "none"}
        
        # Get multiple enhanced versions of the image
        enhanced_images = self._enhance_image_quality(image_array)
        
        for i, enhanced_img in enumerate(enhanced_images):
            try:
                # EasyOCR
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
        
        print(f"Best OCR result: {best_result['method']} with confidence {best_result['confidence']:.3f}")
        return best_result
    
    def extract_images_from_pdf(self, pdf_path: str) -> List[Tuple[np.ndarray, int, Dict[str, Any]]]:
        """Extract images from PDF document."""
        images = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        # Skip very small images
                        if pix.width < 100 or pix.height < 50:
                            pix = None
                            continue
                        
                        # Convert to numpy array
                        if pix.n - pix.alpha < 4:
                            img_data = pix.tobytes("png")
                            img_array = np.frombuffer(img_data, dtype=np.uint8)
                            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                            
                            if image is not None:
                                img_metadata = {
                                    "width": pix.width,
                                    "height": pix.height,
                                    "page": page_num + 1
                                }
                                images.append((image, page_num + 1, img_metadata))
                                print(f"Extracted image from page {page_num + 1}: {pix.width}x{pix.height}")
                        
                        pix = None
                        
                    except Exception as e:
                        print(f"Error extracting image {img_index}: {e}")
                        continue
            
            doc.close()
            print(f"Total images extracted: {len(images)}")
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
        
        return images
    
    def extract_images_from_docx(self, docx_path: str) -> List[Tuple[np.ndarray, str, Dict[str, Any]]]:
        """
        Extract images from DOCX document with metadata.
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
        Process a document and extract text from any images it contains using OCR.
        """
        file_extension = Path(file_path).suffix.lower()
        extracted_text = ""
        
        try:
            if file_extension == '.pdf':
                print(f"Processing PDF with OCR: {file_path}")
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
                print(f"Processing DOCX with OCR: {file_path}")
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
        """
        file_extension = Path(file_path).suffix.lower()
        image_capable_formats = ['.pdf', '.docx', '.doc']
        return file_extension in image_capable_formats