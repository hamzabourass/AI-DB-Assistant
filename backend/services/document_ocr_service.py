import os
import fitz 
import easyocr
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import List, Dict, Any, Tuple
from pathlib import Path
import zipfile

# Import your existing Excel table OCR service
from services.excel_table_ocr import ExcelTableOCRService


class DocumentOCRService:
    """Enhanced service for extracting text from images within documents using OCR with Excel table detection."""
    
    def __init__(self):
        """Initialize the Document OCR service."""
        self.easyocr_reader = None
        self.supported_languages = ['en', 'fr', 'es', 'de','ar']
        
        self.excel_table_service = ExcelTableOCRService()
        print("Excel table OCR service initialized")
        
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
    
    def _detect_basic_table_structure(self, image_array: np.ndarray) -> Dict[str, Any]:
        """
        Basic table detection for simple grid tables (fallback method).
        """
        try:
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            # Detect horizontal lines
            horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
            # Detect vertical lines  
            vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
            
            # Count lines to determine if it's likely a table
            horizontal_line_count = cv2.countNonZero(horizontal_lines) / 255
            vertical_line_count = cv2.countNonZero(vertical_lines) / 255
            
            # Simple heuristic: if we have both horizontal and vertical lines, it might be a table
            is_basic_table = horizontal_line_count > 1000 and vertical_line_count > 1000
            confidence = min(horizontal_line_count / 10000, 1.0) if is_basic_table else 0
            
            return {
                "is_basic_table": is_basic_table,
                "confidence": confidence,
                "horizontal_lines": horizontal_line_count,
                "vertical_lines": vertical_line_count
            }
            
        except Exception as e:
            print(f"Error in basic table detection: {e}")
            return {"is_basic_table": False, "confidence": 0}
    
    def _extract_basic_table_with_structure(self, image_array: np.ndarray, languages: List[str] = ['en', 'fr']) -> Dict[str, Any]:
        """
        Extract text from basic table image while preserving structure (fallback method).
        """
        reader = self._get_easyocr_reader(languages)
        
        # Get OCR results with bounding boxes
        results = reader.readtext(image_array)
        
        if not results:
            return {"structured_text": "", "raw_text": "", "table_data": []}
        
        # Sort results by Y coordinate (top to bottom), then X coordinate (left to right)
        sorted_results = sorted(results, key=lambda x: (x[0][0][1], x[0][0][0]))
        
        # Group results into rows based on Y coordinate proximity
        rows = []
        current_row = []
        current_y = sorted_results[0][0][0][1] if sorted_results else 0
        y_threshold = 20  # Pixels tolerance for same row
        
        for bbox, text, confidence in sorted_results:
            if confidence < 0.3:  # Skip low confidence results
                continue
                
            # Get center Y coordinate of bounding box
            center_y = (bbox[0][1] + bbox[2][1]) / 2
            
            if abs(center_y - current_y) <= y_threshold:
                # Same row
                current_row.append((bbox, text, confidence))
            else:
                # New row
                if current_row:
                    rows.append(current_row)
                current_row = [(bbox, text, confidence)]
                current_y = center_y
        
        # Add the last row
        if current_row:
            rows.append(current_row)
        
        # Sort each row by X coordinate (left to right)
        for row in rows:
            row.sort(key=lambda x: x[0][0][0])  # Sort by left X coordinate
        
        # Create structured output
        table_data = []
        structured_text = ""
        raw_text = ""
        
        for i, row in enumerate(rows):
            row_texts = [item[1] for item in row]
            table_data.append(row_texts)
            
            # Create structured text representation
            structured_text += " | ".join(row_texts) + "\n"
            
            # Also keep raw text
            raw_text += " ".join(row_texts) + " "
        
        return {
            "structured_text": structured_text.strip(),
            "raw_text": raw_text.strip(),
            "table_data": table_data,
            "num_rows": len(rows),
            "num_cols": max(len(row) for row in rows) if rows else 0
        }
    
    def _extract_text_with_multiple_methods(self, image_array: np.ndarray, languages: List[str] = ['en', 'fr']) -> Dict[str, Any]:
        """
        Extract text using multiple methods with priority system:
        1. Excel table detection (most sophisticated)
        2. Basic table detection (fallback)
        3. Regular OCR (non-table content)
        """
        print("🔍 Starting intelligent text extraction...")
        
        # PRIORITY 1: Try Excel table detection first (most sophisticated)
        print("📊 Attempting Excel table detection...")
        try:
            excel_result = self.excel_table_service.process_excel_table(image_array, languages)
            
            if excel_result["is_excel_table"] and excel_result["confidence"] > 0.4:
                print(f"✅ Excel table detected with confidence: {excel_result['confidence']:.3f}")
                print(f"   📐 Table dimensions: {excel_result['metadata']['num_rows']}×{excel_result['metadata']['num_cols']}")
                
                return {
                    "text": excel_result["text"],
                    "confidence": excel_result["confidence"],
                    "method": f"Excel Table OCR ({excel_result['metadata']['num_rows']}×{excel_result['metadata']['num_cols']})"
                }
            else:
                print(f"   ℹ️  Excel table detection confidence too low: {excel_result['confidence']:.3f}")
        
        except Exception as e:
            print(f"   ⚠️  Excel table detection failed: {e}")
        
        # PRIORITY 2: Try basic table detection
        print("📋 Attempting basic table detection...")
        try:
            basic_table_features = self._detect_basic_table_structure(image_array)
            
            if basic_table_features["is_basic_table"] and basic_table_features["confidence"] > 0.3:
                print(f"✅ Basic table detected with confidence: {basic_table_features['confidence']:.3f}")
                
                basic_table_result = self._extract_basic_table_with_structure(image_array, languages)
                
                if basic_table_result["num_rows"] > 1:  # Valid table
                    # Create enhanced text with basic table context
                    enhanced_text = f"BASIC TABLE DETECTED ({basic_table_result['num_rows']} rows × {basic_table_result['num_cols']} columns)\n"
                    enhanced_text += "SIMPLE GRID STRUCTURE DETECTED\n\n"
                    enhanced_text += "STRUCTURED CONTENT:\n" + basic_table_result["structured_text"]
                    enhanced_text += "\n\nRAW TEXT: " + basic_table_result["raw_text"]
                    
                    return {
                        "text": enhanced_text,
                        "confidence": basic_table_features["confidence"],
                        "method": f"Basic Table OCR ({basic_table_result['num_rows']}×{basic_table_result['num_cols']})"
                    }
                else:
                    print(f"   ℹ️  Basic table structure invalid (rows: {basic_table_result['num_rows']})")
            else:
                print(f"   ℹ️  Basic table detection confidence too low: {basic_table_features['confidence']:.3f}")
        
        except Exception as e:
            print(f"   ⚠️  Basic table detection failed: {e}")
        
        # PRIORITY 3: Fall back to regular OCR for non-table images
        print("📝 Using regular OCR (no table structure detected)")
        best_result = {"text": "", "confidence": 0, "method": "none"}
        
        # Get multiple enhanced versions of the image
        enhanced_images = self._enhance_image_quality(image_array)
        
        for i, enhanced_img in enumerate(enhanced_images):
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
                    print(f"   📝 EasyOCR v{i+1} confidence: {easyocr_avg_conf:.3f}, text length: {len(easyocr_text)}")
            
            except Exception as e:
                print(f"   ⚠️  EasyOCR failed on version {i+1}: {e}")
        
        print(f"✅ Best OCR result: {best_result['method']} with confidence {best_result['confidence']:.3f}")
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
        Process a document and extract text from any images it contains using enhanced OCR with Excel table detection.
        """
        file_extension = Path(file_path).suffix.lower()
        extracted_text = ""
        
        try:
            if file_extension == '.pdf':
                print(f"🔍 Processing PDF with enhanced OCR (Excel + Basic table detection): {file_path}")
                images = self.extract_images_from_pdf(file_path)
                
                for image_array, page_num, metadata in images:
                    print(f"\n📄 Processing image on page {page_num} ({metadata['width']}x{metadata['height']})")
                    
                    result = self._extract_text_with_multiple_methods(image_array, languages)
                    
                    if result["text"].strip() and result["confidence"] > 0.3:
                        extracted_text += f"\n--- Text from image on page {page_num} (Method: {result['method']}, Confidence: {result['confidence']:.2f}) ---\n"
                        extracted_text += result["text"] + "\n"
                        print(f"✅ Successfully extracted {len(result['text'])} characters from page {page_num}")
                    else:
                        print(f"❌ Low quality text extraction on page {page_num} (confidence: {result['confidence']:.2f})")
            
            elif file_extension in ['.docx', '.doc']:
                print(f"🔍 Processing DOCX with enhanced OCR (Excel + Basic table detection): {file_path}")
                images = self.extract_images_from_docx(file_path)
                
                for image_array, location, metadata in images:
                    print(f"\n📄 Processing {location} ({metadata['width']}x{metadata['height']})")
                    
                    result = self._extract_text_with_multiple_methods(image_array, languages)
                    
                    if result["text"].strip() and result["confidence"] > 0.3:
                        extracted_text += f"\n--- Text from {location} (Method: {result['method']}, Confidence: {result['confidence']:.2f}) ---\n"
                        extracted_text += result["text"] + "\n"
                        print(f"✅ Successfully extracted {len(result['text'])} characters from {location}")
                    else:
                        print(f"❌ Low quality text extraction from {location} (confidence: {result['confidence']:.2f})")
            
            else:
                print(f"File type {file_extension} not supported for image extraction")
                return ""
        
        except Exception as e:
            print(f"Error processing document {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return ""
        
        if extracted_text.strip():
            print(f"🎉 Total extracted text length: {len(extracted_text)} characters")
        else:
            print("❌ No text was successfully extracted from images")
        
        return extracted_text.strip()
    
    def should_process_for_images(self, file_path: str) -> bool:
        """
        Check if a file type might contain images that need OCR processing.
        """
        file_extension = Path(file_path).suffix.lower()
        image_capable_formats = ['.pdf', '.docx', '.doc']
        return file_extension in image_capable_formats