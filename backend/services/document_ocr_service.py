import os
import fitz 
import easyocr
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import List, Dict, Any, Tuple
from pathlib import Path
import zipfile

# Compatible imports for native table extraction (no camelot)
import pandas as pd
from docx import Document
import pdfplumber
# import tabula  # Only if you can install it without conflicts

# Import your existing Excel table OCR service
from services.excel_table_ocr import ExcelTableOCRService


class DocumentOCRService:
    """Enhanced service for extracting text from images AND native tables within documents."""
    
    def __init__(self):
        """Initialize the Document OCR service."""
        self.easyocr_reader = None
        self.supported_languages = ['en', 'fr', 'es', 'de','ar']
        
        self.excel_table_service = ExcelTableOCRService()
        print("Excel table OCR service initialized")
        print("Native table extraction support enabled (compatible mode)")
        
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
    
    # ==================== NATIVE TABLE EXTRACTION METHODS ====================
    
    def extract_pdf_native_tables_pdfplumber(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract native tables from PDF using PDFPlumber (most compatible).
        """
        all_tables = []
        
        print("🔍 Extracting native tables from PDF using PDFPlumber...")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"  📄 Scanning page {page_num}...")
                    page_tables = page.find_tables()
                    
                    for table_idx, table in enumerate(page_tables):
                        table_data = table.extract()
                        
                        if table_data and len(table_data) > 1:  # Must have header + data
                            headers = table_data[0] if table_data[0] else []
                            data_rows = table_data[1:]
                            
                            # Filter out empty rows
                            data_rows = [row for row in data_rows if row and any(cell for cell in row if cell)]
                            
                            if data_rows:  # Only include if we have actual data
                                table_dict = {
                                    "method": "pdfplumber",
                                    "page": page_num,
                                    "accuracy": 1.0,
                                    "table_data": data_rows,
                                    "headers": headers,
                                    "num_rows": len(data_rows),
                                    "num_cols": len(headers) if headers else (len(data_rows[0]) if data_rows else 0),
                                    "table_index": table_idx,
                                    "source": "native_pdf"
                                }
                                all_tables.append(table_dict)
                                print(f"    ✅ Extracted table {table_idx+1} from page {page_num} ({len(data_rows)} data rows)")
        except Exception as e:
            print(f"  ⚠️ PDFPlumber extraction failed: {e}")
        
        return all_tables
    
    def extract_pdf_native_tables_tabula(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract native tables from PDF using Tabula (if available).
        """
        all_tables = []
        
        try:
            import tabula
            print("🔍 Extracting native tables from PDF using Tabula...")
            
            tabula_tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            
            for i, df in enumerate(tabula_tables):
                if not df.empty and len(df) > 1:  # At least header + 1 data row
                    # Clean the dataframe
                    df = df.dropna(how='all')  # Remove completely empty rows
                    
                    if len(df) > 0:
                        table_dict = {
                            "method": "tabula",
                            "page": "auto-detected",
                            "accuracy": 1.0,
                            "table_data": df.values.tolist(),
                            "headers": df.columns.tolist(),
                            "num_rows": len(df),
                            "num_cols": len(df.columns),
                            "table_index": i,
                            "source": "native_pdf"
                        }
                        all_tables.append(table_dict)
                        print(f"  ✅ Tabula: Extracted table {i+1} ({len(df)} rows)")
        except ImportError:
            print("  ℹ️ Tabula not available (requires Java)")
        except Exception as e:
            print(f"  ⚠️ Tabula extraction failed: {e}")
        
        return all_tables
    
    def extract_pdf_native_tables_pymupdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract native tables from PDF using PyMuPDF (fallback method).
        """
        all_tables = []
        
        print("🔍 Extracting native tables from PDF using PyMuPDF...")
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Try to find tables using PyMuPDF's table detection
                try:
                    page_tables = page.find_tables()
                    
                    for table_idx, table in enumerate(page_tables):
                        table_data = table.extract()
                        
                        if table_data and len(table_data) > 1:
                            headers = table_data[0] if table_data[0] else []
                            data_rows = table_data[1:]
                            
                            # Filter out empty rows
                            data_rows = [row for row in data_rows if row and any(cell for cell in row if cell)]
                            
                            if data_rows:
                                table_dict = {
                                    "method": "pymupdf",
                                    "page": page_num + 1,
                                    "accuracy": 1.0,
                                    "table_data": data_rows,
                                    "headers": headers,
                                    "num_rows": len(data_rows),
                                    "num_cols": len(headers) if headers else (len(data_rows[0]) if data_rows else 0),
                                    "table_index": table_idx,
                                    "source": "native_pdf"
                                }
                                all_tables.append(table_dict)
                                print(f"  ✅ PyMuPDF: Extracted table {table_idx+1} from page {page_num+1}")
                except AttributeError:
                    # find_tables() might not be available in older PyMuPDF versions
                    print(f"  ℹ️ PyMuPDF table detection not available on page {page_num+1}")
            
            doc.close()
        except Exception as e:
            print(f"  ⚠️ PyMuPDF extraction failed: {e}")
        
        return all_tables
    
    def extract_pdf_native_tables(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract native tables from PDF using all available compatible methods.
        """
        all_tables = []
        
        print("🔍 Starting PDF native table extraction...")
        
        # Method 1: PDFPlumber (most reliable and compatible)
        pdfplumber_tables = self.extract_pdf_native_tables_pdfplumber(pdf_path)
        all_tables.extend(pdfplumber_tables)
        
        # Method 2: Tabula (if available)
        tabula_tables = self.extract_pdf_native_tables_tabula(pdf_path)
        all_tables.extend(tabula_tables)
        
        # Method 3: PyMuPDF (fallback)
        pymupdf_tables = self.extract_pdf_native_tables_pymupdf(pdf_path)
        all_tables.extend(pymupdf_tables)
        
        print(f"📊 Total native tables found: {len(all_tables)}")
        return all_tables
    
    def extract_docx_native_tables(self, docx_path: str) -> List[Dict[str, Any]]:
        """
        Extract native tables from DOCX files.
        """
        tables = []
        
        print("🔍 Extracting native tables from DOCX...")
        
        try:
            doc = Document(docx_path)
            
            for table_idx, table in enumerate(doc.tables):
                table_data = []
                headers = []
                
                for row_idx, row in enumerate(table.rows):
                    row_data = []
                    for cell in row.cells:
                        # Clean cell text
                        cell_text = cell.text.strip().replace('\n', ' ').replace('\r', '')
                        row_data.append(cell_text)
                    
                    if row_idx == 0:
                        # First row as headers
                        headers = row_data
                    else:
                        # Only add non-empty rows
                        if any(cell.strip() for cell in row_data):
                            table_data.append(row_data)
                
                # Only include tables with actual content
                if table_data and any(any(cell for cell in row if cell.strip()) for row in table_data):
                    table_dict = {
                        "method": "python_docx",
                        "page": f"Table {table_idx + 1}",
                        "accuracy": 1.0,
                        "table_data": table_data,
                        "headers": headers,
                        "num_rows": len(table_data),
                        "num_cols": len(headers) if headers else (len(table_data[0]) if table_data else 0),
                        "table_index": table_idx,
                        "source": "native_docx"
                    }
                    tables.append(table_dict)
                    print(f"  ✅ DOCX: Extracted table {table_idx+1} ({len(table_data)} rows × {len(headers)} cols)")
        
        except Exception as e:
            print(f"  ⚠️ DOCX native table extraction failed: {e}")
        
        return tables
    
    def extract_csv_excel_tables(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from CSV and Excel files.
        """
        tables = []
        file_extension = Path(file_path).suffix.lower()
        
        print(f"🔍 Extracting data from {file_extension.upper()} file...")
        
        try:
            if file_extension == '.csv':
                # Try different encodings for CSV
                encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        print(f"  ✅ Successfully read CSV with {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is not None and not df.empty:
                    # Clean the dataframe
                    df = df.dropna(how='all')  # Remove completely empty rows
                    
                    table_dict = {
                        "method": "pandas_csv",
                        "page": "CSV File",
                        "accuracy": 1.0,
                        "table_data": df.values.tolist(),
                        "headers": df.columns.tolist(),
                        "num_rows": len(df),
                        "num_cols": len(df.columns),
                        "table_index": 0,
                        "source": "native_csv"
                    }
                    tables.append(table_dict)
                    print(f"  ✅ CSV: Extracted table ({len(df)} rows × {len(df.columns)} cols)")
                else:
                    print("  ⚠️ Could not read CSV file or file is empty")
            
            elif file_extension in ['.xlsx', '.xls']:
                excel_file = pd.ExcelFile(file_path)
                
                for sheet_idx, sheet_name in enumerate(excel_file.sheet_names):
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        
                        if not df.empty:
                            # Clean the dataframe
                            df = df.dropna(how='all')  # Remove completely empty rows
                            
                            if not df.empty:
                                table_dict = {
                                    "method": "pandas_excel",
                                    "page": f"Sheet: {sheet_name}",
                                    "accuracy": 1.0,
                                    "table_data": df.values.tolist(),
                                    "headers": df.columns.tolist(),
                                    "num_rows": len(df),
                                    "num_cols": len(df.columns),
                                    "table_index": sheet_idx,
                                    "sheet_name": sheet_name,
                                    "source": "native_excel"
                                }
                                tables.append(table_dict)
                                print(f"  ✅ Excel: Extracted table from '{sheet_name}' ({len(df)} rows × {len(df.columns)} cols)")
                    except Exception as e:
                        print(f"  ⚠️ Error reading sheet '{sheet_name}': {e}")
        
        except Exception as e:
            print(f"  ⚠️ {file_extension.upper()} extraction failed: {e}")
        
        return tables
    
    def deduplicate_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate tables based on content similarity.
        """
        if not tables:
            return tables
        
        unique_tables = []
        seen_signatures = set()
        
        for table in tables:
            # Create a signature based on table dimensions and some content
            signature = f"{table['num_rows']}x{table['num_cols']}_{table['page']}"
            
            # Add some content to the signature to distinguish similar-sized tables
            if table['table_data'] and len(table['table_data']) > 0:
                first_row = str(table['table_data'][0][:2]) if table['table_data'][0] else ""
                signature += f"_{hash(first_row) % 10000}"
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_tables.append(table)
                print(f"  ✅ Keeping table: {table['method']} - {table['num_rows']}×{table['num_cols']} from {table['page']}")
            else:
                print(f"  🔄 Skipping duplicate table: {table['method']} - {table['num_rows']}×{table['num_cols']}")
        
        return unique_tables
    
    def format_native_tables_for_rag(self, tables: List[Dict[str, Any]]) -> str:
        """
        Format native tables for RAG system consumption.
        """
        if not tables:
            return ""
        
        formatted_text = "\n=== NATIVE TABLES EXTRACTED ===\n"
        
        for i, table in enumerate(tables):
            formatted_text += f"\n--- NATIVE TABLE {i+1} ({table['source'].upper()}) ---\n"
            formatted_text += f"Source: {table['method']} from {table['page']}\n"
            formatted_text += f"Dimensions: {table['num_rows']} rows × {table['num_cols']} columns\n"
            
            if 'accuracy' in table and table['accuracy'] < 1.0:
                formatted_text += f"Extraction Accuracy: {table['accuracy']:.2f}\n"
            
            # Add headers if available
            if table['headers'] and any(str(h).strip() for h in table['headers'] if h is not None):
                clean_headers = [str(h).strip() if h is not None else "" for h in table['headers']]
                formatted_text += "HEADERS: " + " | ".join(clean_headers) + "\n"
                formatted_text += "-" * (len(" | ".join(clean_headers)) + 9) + "\n"
            
            # Add table data
            for row in table['table_data']:
                if row and any(str(cell).strip() for cell in row if cell is not None):  # Skip empty rows
                    clean_row = [str(cell).strip() if cell is not None else "" for cell in row]
                    formatted_text += " | ".join(clean_row) + "\n"
            
            formatted_text += "\n"
        
        return formatted_text.strip()
    
    # ==================== EXISTING OCR METHODS (UNCHANGED) ====================
    
    def _enhance_image_quality(self, image_array: np.ndarray) -> List[np.ndarray]:
        """Apply multiple enhancement techniques to improve OCR accuracy."""
        enhanced_images = []
        
        try:
            if len(image_array.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image_array)
            
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
            enhanced_images.append(gray)
            
            enhancer = ImageEnhance.Contrast(pil_image)
            contrast_enhanced = enhancer.enhance(2.0)
            
            enhancer = ImageEnhance.Sharpness(contrast_enhanced)
            sharp_enhanced = enhancer.enhance(2.0)
            
            enhanced_array = np.array(sharp_enhanced)
            if len(enhanced_array.shape) == 3:
                enhanced_array = cv2.cvtColor(enhanced_array, cv2.COLOR_RGB2GRAY)
            enhanced_images.append(enhanced_array)
            
            denoised = cv2.fastNlMeansDenoising(gray)
            
            adaptive_thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 15, 10
            )
            enhanced_images.append(adaptive_thresh)
            
            print(f"Generated {len(enhanced_images)} enhanced image versions")
            return enhanced_images
            
        except Exception as e:
            print(f"Error enhancing image: {e}")
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
            return [gray]
    
    def _detect_basic_table_structure(self, image_array: np.ndarray) -> Dict[str, Any]:
        """Basic table detection for simple grid tables (fallback method)."""
        try:
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
            
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            
            horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
            
            horizontal_line_count = cv2.countNonZero(horizontal_lines) / 255
            vertical_line_count = cv2.countNonZero(vertical_lines) / 255
            
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
        """Extract text from basic table image while preserving structure (fallback method)."""
        reader = self._get_easyocr_reader(languages)
        
        results = reader.readtext(image_array)
        
        if not results:
            return {"structured_text": "", "raw_text": "", "table_data": []}
        
        sorted_results = sorted(results, key=lambda x: (x[0][0][1], x[0][0][0]))
        
        rows = []
        current_row = []
        current_y = sorted_results[0][0][0][1] if sorted_results else 0
        y_threshold = 20
        
        for bbox, text, confidence in sorted_results:
            if confidence < 0.3:
                continue
                
            center_y = (bbox[0][1] + bbox[2][1]) / 2
            
            if abs(center_y - current_y) <= y_threshold:
                current_row.append((bbox, text, confidence))
            else:
                if current_row:
                    rows.append(current_row)
                current_row = [(bbox, text, confidence)]
                current_y = center_y
        
        if current_row:
            rows.append(current_row)
        
        for row in rows:
            row.sort(key=lambda x: x[0][0][0])
        
        table_data = []
        structured_text = ""
        raw_text = ""
        
        for i, row in enumerate(rows):
            row_texts = [item[1] for item in row]
            table_data.append(row_texts)
            
            structured_text += " | ".join(row_texts) + "\n"
            raw_text += " ".join(row_texts) + " "
        
        return {
            "structured_text": structured_text.strip(),
            "raw_text": raw_text.strip(),
            "table_data": table_data,
            "num_rows": len(rows),
            "num_cols": max(len(row) for row in rows) if rows else 0
        }
    
    def _extract_text_with_multiple_methods(self, image_array: np.ndarray, languages: List[str] = ['en', 'fr']) -> Dict[str, Any]:
        """Extract text using multiple methods with priority system."""
        print("🔍 Starting intelligent text extraction...")
        
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
        
        print("📋 Attempting basic table detection...")
        try:
            basic_table_features = self._detect_basic_table_structure(image_array)
            
            if basic_table_features["is_basic_table"] and basic_table_features["confidence"] > 0.3:
                print(f"✅ Basic table detected with confidence: {basic_table_features['confidence']:.3f}")
                
                basic_table_result = self._extract_basic_table_with_structure(image_array, languages)
                
                if basic_table_result["num_rows"] > 1:
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
        
        print("📝 Using regular OCR (no table structure detected)")
        best_result = {"text": "", "confidence": 0, "method": "none"}
        
        enhanced_images = self._enhance_image_quality(image_array)
        
        for i, enhanced_img in enumerate(enhanced_images):
            try:
                reader = self._get_easyocr_reader(languages)
                easyocr_results = reader.readtext(enhanced_img)
                
                easyocr_text = ""
                easyocr_confidences = []
                
                for (bbox, text, confidence) in easyocr_results:
                    if confidence > 0.2:
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
                        
                        if pix.width < 100 or pix.height < 50:
                            pix = None
                            continue
                        
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
        """Extract images from DOCX document with metadata."""
        images = []
        
        try:
            with zipfile.ZipFile(docx_path, 'r') as docx_zip:
                image_files = [f for f in docx_zip.namelist() if f.startswith('word/media/')]
                
                for img_file in image_files:
                    try:
                        img_data = docx_zip.read(img_file)
                        
                        img_metadata = {
                            "file_size": len(img_data),
                            "source_path": img_file
                        }
                        
                        img_array = np.frombuffer(img_data, dtype=np.uint8)
                        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        
                        if image is not None:
                            img_metadata.update({
                                "width": image.shape[1],
                                "height": image.shape[0]
                            })
                            
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
    
    # ==================== MAIN PROCESSING METHOD (ENHANCED) ====================
    
    def process_document_with_ocr(self, file_path: str, languages: List[str] = ['en', 'fr']) -> str:
        """
        Process a document and extract text from BOTH images and native tables.
        """
        file_extension = Path(file_path).suffix.lower()
        extracted_text = ""
        
        print(f"🔍 Processing document: {file_path}")
        print(f"📄 File type: {file_extension}")
        
        try:
            # STEP 1: Extract native tables first
            native_tables = []
            
            if file_extension == '.pdf':
                print("\n🔍 STEP 1: Extracting native tables from PDF...")
                native_tables = self.extract_pdf_native_tables(file_path)
            
            elif file_extension in ['.docx', '.doc']:
                print("\n🔍 STEP 1: Extracting native tables from DOCX...")
                native_tables = self.extract_docx_native_tables(file_path)
            
            elif file_extension in ['.csv', '.xlsx', '.xls']:
                print(f"\n🔍 STEP 1: Extracting data from {file_extension.upper()}...")
                native_tables = self.extract_csv_excel_tables(file_path)
            
            # Process native tables
            if native_tables:
                print(f"✅ Found {len(native_tables)} native tables")
                unique_native_tables = self.deduplicate_tables(native_tables)
                native_table_text = self.format_native_tables_for_rag(unique_native_tables)
                extracted_text += native_table_text
            else:
                print("ℹ️  No native tables found")
            
            # STEP 2: Extract from images (existing functionality)
            image_text = ""
            
            if file_extension == '.pdf':
                print(f"\n🔍 STEP 2: Processing images in PDF with enhanced OCR...")
                images = self.extract_images_from_pdf(file_path)
                
                for image_array, page_num, metadata in images:
                    print(f"\n📄 Processing image on page {page_num} ({metadata['width']}x{metadata['height']})")
                    
                    result = self._extract_text_with_multiple_methods(image_array, languages)
                    
                    if result["text"].strip() and result["confidence"] > 0.3:
                        image_text += f"\n--- IMAGE TABLE/TEXT from page {page_num} (Method: {result['method']}, Confidence: {result['confidence']:.2f}) ---\n"
                        image_text += result["text"] + "\n"
                        print(f"✅ Successfully extracted {len(result['text'])} characters from page {page_num}")
                    else:
                        print(f"❌ Low quality text extraction on page {page_num} (confidence: {result['confidence']:.2f})")
            
            elif file_extension in ['.docx', '.doc']:
                print(f"\n🔍 STEP 2: Processing images in DOCX with enhanced OCR...")
                images = self.extract_images_from_docx(file_path)
                
                for image_array, location, metadata in images:
                    print(f"\n📄 Processing {location} ({metadata['width']}x{metadata['height']})")
                    
                    result = self._extract_text_with_multiple_methods(image_array, languages)
                    
                    if result["text"].strip() and result["confidence"] > 0.3:
                        image_text += f"\n--- IMAGE TABLE/TEXT from {location} (Method: {result['method']}, Confidence: {result['confidence']:.2f}) ---\n"
                        image_text += result["text"] + "\n"
                        print(f"✅ Successfully extracted {len(result['text'])} characters from {location}")
                    else:
                        print(f"❌ Low quality text extraction from {location} (confidence: {result['confidence']:.2f})")
            
            # Combine native tables and image text
            if image_text.strip():
                if extracted_text:
                    extracted_text += "\n\n=== IMAGE-BASED TABLES AND TEXT ===\n" + image_text
                else:
                    extracted_text = image_text
            
            # STEP 3: Summary
            if extracted_text.strip():
                total_length = len(extracted_text)
                native_count = len(unique_native_tables) if native_tables else 0
                image_count = len(images) if 'images' in locals() else 0
                
                print(f"\n🎉 EXTRACTION COMPLETE!")
                print(f"   📊 Native tables found: {native_count}")
                print(f"   🖼️  Images processed: {image_count}")
                print(f"   📝 Total text length: {total_length} characters")
                
                # Add summary header
                summary = f"=== DOCUMENT PROCESSING SUMMARY ===\n"
                summary += f"File: {Path(file_path).name}\n"
                summary += f"Type: {file_extension.upper()}\n"
                summary += f"Native tables extracted: {native_count}\n"
                summary += f"Images processed: {image_count}\n"
                summary += f"Total content length: {total_length} characters\n"
                summary += "=" * 50 + "\n\n"
                
                extracted_text = summary + extracted_text
            else:
                print("❌ No text or tables were successfully extracted")
                
        except Exception as e:
            print(f"Error processing document {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return f"Error processing {file_path}: {str(e)}"
        
        return extracted_text.strip()
    
    def should_process_for_images(self, file_path: str) -> bool:
        """
        Check if a file type might contain images that need OCR processing.
        """
        file_extension = Path(file_path).suffix.lower()
        image_capable_formats = ['.pdf', '.docx', '.doc']
        return file_extension in image_capable_formats
    
    def should_process_for_native_tables(self, file_path: str) -> bool:
        """
        Check if a file type might contain native tables.
        """
        file_extension = Path(file_path).suffix.lower()
        table_capable_formats = ['.pdf', '.docx', '.doc', '.csv', '.xlsx', '.xls']
        return file_extension in table_capable_formats
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get all supported file formats and their capabilities.
        """
        return {
            "image_ocr": ['.pdf', '.docx', '.doc'],
            "native_tables": ['.pdf', '.docx', '.doc', '.csv', '.xlsx', '.xls'],
            "excel_table_detection": ['.pdf', '.docx', '.doc'],  # For image-based Excel tables
            "all_supported": ['.pdf', '.docx', '.doc', '.csv', '.xlsx', '.xls']
        }