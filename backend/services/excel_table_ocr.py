import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import easyocr
import re

class ExcelTableOCRService:
    """OCR service optimized for Excel-style structured tables."""
    
    def __init__(self):
        self.easyocr_reader = None
        
    def _get_easyocr_reader(self, languages: List[str] = ['en', 'fr']):
        """Get or initialize EasyOCR reader."""
        if self.easyocr_reader is None:
            self.easyocr_reader = easyocr.Reader(languages, gpu=False)
        return self.easyocr_reader
    
    def _detect_excel_table_features(self, image_array: np.ndarray) -> Dict[str, Any]:
        """
        Detect Excel-specific table features.
        
        Returns:
            Dict with detection results for Excel-style tables
        """
        try:
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY) if len(image_array.shape) == 3 else image_array
            
            # Multiple detection methods
            features = {
                "has_grid_lines": False,
                "has_alternating_rows": False,
                "has_headers": False,
                "grid_confidence": 0,
                "structure_confidence": 0
            }
            
            # 1. Grid line detection (improved)
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 10)
            
            # Detect horizontal lines (more flexible)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (min(40, image_array.shape[1]//10), 1))
            horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Detect vertical lines (more flexible)  
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, min(40, image_array.shape[0]//10)))
            vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
            
            # Count line pixels
            h_line_pixels = cv2.countNonZero(horizontal_lines)
            v_line_pixels = cv2.countNonZero(vertical_lines)
            
            # More sophisticated grid detection
            total_pixels = image_array.shape[0] * image_array.shape[1]
            h_line_ratio = h_line_pixels / total_pixels
            v_line_ratio = v_line_pixels / total_pixels
            
            # Excel tables typically have both horizontal and vertical structure
            if h_line_ratio > 0.001 and v_line_ratio > 0.001:
                features["has_grid_lines"] = True
                features["grid_confidence"] = min((h_line_ratio + v_line_ratio) * 1000, 1.0)
            
            # 2. Detect alternating row patterns (Excel's default styling)
            row_samples = []
            height = gray.shape[0]
            for y in range(0, height, max(1, height//20)):
                if y < height:
                    row_mean = np.mean(gray[y, :])
                    row_samples.append(row_mean)
            
            # Check for alternating brightness patterns
            if len(row_samples) > 4:
                differences = [abs(row_samples[i] - row_samples[i+1]) for i in range(len(row_samples)-1)]
                avg_diff = np.mean(differences)
                if avg_diff > 10:  # Some alternating pattern detected
                    features["has_alternating_rows"] = True
            
            # 3. Header detection (top area typically darker/different)
            if height > 50:
                top_quarter = gray[:height//4, :]
                bottom_quarter = gray[3*height//4:, :]
                
                top_mean = np.mean(top_quarter)
                bottom_mean = np.mean(bottom_quarter)
                
                # If top is significantly different from bottom, might have headers
                if abs(top_mean - bottom_mean) > 20:
                    features["has_headers"] = True
            
            # Overall structure confidence
            confidence_factors = []
            if features["has_grid_lines"]:
                confidence_factors.append(features["grid_confidence"])
            if features["has_alternating_rows"]:
                confidence_factors.append(0.3)
            if features["has_headers"]:
                confidence_factors.append(0.2)
            
            features["structure_confidence"] = min(sum(confidence_factors), 1.0)
            
            return features
            
        except Exception as e:
            print(f"Error in Excel table detection: {e}")
            return {"has_grid_lines": False, "structure_confidence": 0}
    
    def _extract_with_cell_detection(self, image_array: np.ndarray, languages: List[str] = ['en', 'fr']) -> Dict[str, Any]:
        """
        Extract text using cell-by-cell detection for better Excel table handling.
        """
        reader = self._get_easyocr_reader(languages)
        
        # Get all OCR results with detailed bounding boxes
        ocr_results = reader.readtext(image_array, detail=1)
        
        if not ocr_results:
            return {"structured_text": "", "raw_text": "", "table_data": [], "cells": []}
        
        # Enhanced cell processing
        cells = []
        for i, (bbox, text, confidence) in enumerate(ocr_results):
            if confidence < 0.2:  # Lower threshold for Excel tables
                continue
                
            # Calculate cell properties
            x1, y1 = bbox[0]
            x2, y2 = bbox[2]
            
            cell_info = {
                "text": text.strip(),
                "confidence": confidence,
                "bbox": bbox,
                "center_x": (x1 + x2) / 2,
                "center_y": (y1 + y2) / 2,
                "width": x2 - x1,
                "height": y2 - y1,
                "area": (x2 - x1) * (y2 - y1)
            }
            cells.append(cell_info)
        
        # Smart row grouping with flexible thresholds
        cells.sort(key=lambda x: (x["center_y"], x["center_x"]))
        
        rows = []
        current_row = []
        
        if cells:
            current_y = cells[0]["center_y"]
            
            for cell in cells:
                # Dynamic threshold based on average cell height
                avg_height = np.mean([c["height"] for c in cells])
                y_threshold = max(avg_height * 0.5, 15)  # Adaptive threshold
                
                if abs(cell["center_y"] - current_y) <= y_threshold:
                    current_row.append(cell)
                else:
                    if current_row:
                        # Sort row by X coordinate
                        current_row.sort(key=lambda x: x["center_x"])
                        rows.append(current_row)
                    current_row = [cell]
                    current_y = cell["center_y"]
            
            # Add last row
            if current_row:
                current_row.sort(key=lambda x: x["center_x"])
                rows.append(current_row)
        
        # Create structured output with Excel-style formatting
        table_data = []
        structured_text = ""
        raw_text = ""
        
        # Detect if first row is likely a header
        has_header = len(rows) > 1 and self._is_likely_header(rows[0], rows[1:] if len(rows) > 1 else [])
        
        for i, row in enumerate(rows):
            row_texts = [cell["text"] for cell in row]
            table_data.append(row_texts)
            
            # Format as table with proper alignment
            if i == 0 and has_header:
                # Header row - make it stand out
                structured_text += "HEADER: " + " | ".join(row_texts) + "\n"
                structured_text += "-" * (len(" | ".join(row_texts)) + 8) + "\n"
            else:
                structured_text += " | ".join(row_texts) + "\n"
            
            raw_text += " ".join(row_texts) + " "
        
        return {
            "structured_text": structured_text.strip(),
            "raw_text": raw_text.strip(),
            "table_data": table_data,
            "cells": cells,
            "num_rows": len(rows),
            "num_cols": max(len(row) for row in rows) if rows else 0,
            "has_header": has_header
        }
    
    def _is_likely_header(self, first_row: List[Dict], other_rows: List[List[Dict]]) -> bool:
        """
        Determine if the first row is likely a header based on content analysis.
        """
        if not first_row or not other_rows:
            return False
        
        # Check for header indicators
        header_indicators = 0
        
        for cell in first_row:
            text = cell["text"].lower()
            
            # Common header patterns
            if any(word in text for word in ["total", "name", "id", "date", "amount", "price", "quantity", "description"]):
                header_indicators += 1
            
            # Headers often don't contain numbers (except for dates/IDs)
            if not re.search(r'\d+', text) or re.search(r'\d{4}', text):  # No numbers or year patterns
                header_indicators += 0.5
            
            # Headers are often shorter
            if len(text) < 20:
                header_indicators += 0.3
        
        # If more than half the cells look like headers
        return header_indicators > len(first_row) * 0.4
    
    def process_excel_table(self, image_array: np.ndarray, languages: List[str] = ['en', 'fr']) -> Dict[str, Any]:
        """
        Main method to process Excel-style tables with enhanced detection.
        """
        # Detect Excel table features
        excel_features = self._detect_excel_table_features(image_array)
        
        # Extract with cell-based method
        extraction_result = self._extract_with_cell_detection(image_array, languages)
        
        # Calculate overall confidence
        structure_confidence = excel_features["structure_confidence"]
        text_confidence = np.mean([cell["confidence"] for cell in extraction_result["cells"]]) if extraction_result["cells"] else 0
        overall_confidence = (structure_confidence + text_confidence) / 2
        
        # Create enhanced output with Excel context
        if overall_confidence > 0.3 and extraction_result["num_rows"] > 1:
            enhanced_text = f"EXCEL-STYLE TABLE DETECTED ({extraction_result['num_rows']} rows × {extraction_result['num_cols']} columns)\n"
            
            if extraction_result["has_header"]:
                enhanced_text += "TABLE HAS HEADER ROW\n"
            
            if excel_features["has_alternating_rows"]:
                enhanced_text += "ALTERNATING ROW FORMATTING DETECTED\n"
            
            enhanced_text += "\nSTRUCTURED CONTENT:\n" + extraction_result["structured_text"]
            enhanced_text += "\n\nRAW TEXT: " + extraction_result["raw_text"]
            
            return {
                "method": "excel_table_ocr",
                "is_excel_table": True,
                "confidence": overall_confidence,
                "text": enhanced_text,
                "table_data": extraction_result["table_data"],
                "features": excel_features,
                "metadata": {
                    "num_rows": extraction_result["num_rows"],
                    "num_cols": extraction_result["num_cols"],
                    "has_header": extraction_result["has_header"],
                    "cell_count": len(extraction_result["cells"])
                }
            }
        else:
            # Fall back to regular OCR
            return {
                "method": "regular_ocr_fallback",
                "is_excel_table": False,
                "confidence": text_confidence,
                "text": extraction_result["raw_text"],
                "table_data": extraction_result["table_data"],
                "features": excel_features,
                "metadata": {}
            }