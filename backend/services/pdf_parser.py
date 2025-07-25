import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
import PyPDF2
import fitz  # PyMuPDF
import pdfplumber

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LegalPDFParser:
    """
    Parser especializado para documentos legales en PDF
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'files_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_pages': 0,
            'total_characters': 0,
        }
    
    def extract_text_from_pdf(self, pdf_path: str, method: str = "auto") -> Dict[str, Any]:
        """
        Extrae texto de un PDF usando múltiples métodos para mayor robustez
        """
        self.logger.info(f"Procesando PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")
        
        result = {
            'filename': os.path.basename(pdf_path),
            'filepath': pdf_path,
            'text': "",
            'pages': 0,
            'method_used': method,
            'success': False,
            'error': None
        }
        
        try:
            # Probar diferentes métodos de extracción
            if method == "auto":
                # Intentar pdfplumber primero (mejor para texto estructurado)
                text = self._extract_with_pdfplumber(pdf_path)
                if text and len(text.strip()) > 100:
                    result['text'] = text
                    result['method_used'] = "pdfplumber"
                else:
                    # Fallback a PyMuPDF
                    text = self._extract_with_pymupdf(pdf_path)
                    if text and len(text.strip()) > 100:
                        result['text'] = text
                        result['method_used'] = "pymupdf"
                    else:
                        # Último recurso: PyPDF2
                        text = self._extract_with_pypdf2(pdf_path)
                        result['text'] = text
                        result['method_used'] = "pypdf2"
            
            elif method == "pdfplumber":
                result['text'] = self._extract_with_pdfplumber(pdf_path)
                result['method_used'] = "pdfplumber"
            
            elif method == "pymupdf":
                result['text'] = self._extract_with_pymupdf(pdf_path)
                result['method_used'] = "pymupdf"
                
            elif method == "pypdf2":
                result['text'] = self._extract_with_pypdf2(pdf_path)
                result['method_used'] = "pypdf2"
            
            # Limpiar y procesar el texto
            if result['text']:
                result['text'] = self._clean_legal_text(result['text'])
                result['pages'] = self._count_pdf_pages(pdf_path)
                result['success'] = True
                
                # Actualizar estadísticas
                self.stats['successful_extractions'] += 1
                self.stats['total_characters'] += len(result['text'])
                self.stats['total_pages'] += result['pages']
                
                self.logger.info(f"✅ Extraído exitosamente: {result['pages']} páginas, {len(result['text'])} caracteres")
            
        except Exception as e:
            result['error'] = str(e)
            self.stats['failed_extractions'] += 1
            self.logger.error(f"❌ Error procesando {pdf_path}: {e}")
        
        finally:
            self.stats['files_processed'] += 1
        
        return result
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto usando pdfplumber (mejor para tablas y estructura)"""
        text_content = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        # Extraer texto regular
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(f"\n--- PÁGINA {page_num} ---\n")
                            text_content.append(page_text)
                        
                        # Extraer tablas si las hay
                        tables = page.extract_tables()
                        for table in tables:
                            if table:
                                text_content.append("\n--- TABLA ---\n")
                                for row in table:
                                    if row:
                                        text_content.append(" | ".join(str(cell) if cell else "" for cell in row))
                                        text_content.append("\n")
                    
                    except Exception as e:
                        self.logger.warning(f"Error en página {page_num}: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error con pdfplumber: {e}")
            return ""
        
        return "\n".join(text_content)
    
    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extrae texto usando PyMuPDF (fitz) - Bueno para texto simple"""
        text_content = []
        
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    text = page.get_text()
                    if text.strip():
                        text_content.append(f"\n--- PÁGINA {page_num + 1} ---\n")
                        text_content.append(text)
                
                except Exception as e:
                    self.logger.warning(f"Error en página {page_num + 1}: {e}")
                    continue
            
            doc.close()
        
        except Exception as e:
            self.logger.error(f"Error con PyMuPDF: {e}")
            return ""
        
        return "\n".join(text_content)
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extrae texto usando PyPDF2 (fallback)"""
        text_content = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            text_content.append(f"\n--- PÁGINA {page_num} ---\n")
                            text_content.append(text)
                    
                    except Exception as e:
                        self.logger.warning(f"Error en página {page_num}: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error con PyPDF2: {e}")
            return ""
        
        return "\n".join(text_content)
    
    def _count_pdf_pages(self, pdf_path: str) -> int:
        """Cuenta el número de páginas del PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except:
            return 0
    
    def _clean_legal_text(self, text: str) -> str:
        """Limpia y normaliza texto legal"""
        if not text:
            return ""
        
        # Normalizar espacios en blanco
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar caracteres de control
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Normalizar saltos de línea múltiples
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Limpiar espacios al inicio y final
        text = text.strip()
        
        # Normalizar algunos caracteres comunes en PDFs legales
        replacements = {
            '\u2013': '-',  # en dash
            '\u2014': '-',  # em dash
            '\u2018': "'",  # left single quote
            '\u2019': "'",  # right single quote
            '\u201c': '"',  # left double quote
            '\u201d': '"',  # right double quote
            '\u2022': '•',  # bullet
            '\uf0b7': '•',  # bullet variant
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def extract_all_pdfs_from_directory(self, directory: str) -> Dict[str, Any]:
        """
        Procesa todos los PDFs de un directorio
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directorio no encontrado: {directory}")
        
        pdf_files = list(directory_path.glob("*.pdf"))
        
        if not pdf_files:
            self.logger.warning(f"No se encontraron archivos PDF en {directory}")
            return {"files": {}, "summary": self.get_processing_stats()}
        
        results = {}
        self.logger.info(f"Procesando {len(pdf_files)} archivos PDF...")
        
        for pdf_file in pdf_files:
            try:
                result = self.extract_text_from_pdf(str(pdf_file))
                results[pdf_file.name] = result
            except Exception as e:
                self.logger.error(f"Error procesando {pdf_file}: {e}")
                results[pdf_file.name] = {
                    'success': False,
                    'error': str(e),
                    'filename': pdf_file.name
                }
        
        return {
            "files": results,
            "summary": self.get_processing_stats()
        }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del procesamiento"""
        total_processed = self.stats['files_processed']
        success_rate = (self.stats['successful_extractions'] / total_processed * 100) if total_processed > 0 else 0
        
        return {
            'files_processed': total_processed,
            'successful_extractions': self.stats['successful_extractions'],
            'failed_extractions': self.stats['failed_extractions'],
            'success_rate': f"{success_rate:.1f}%",
            'total_pages': self.stats['total_pages'],
            'total_characters': self.stats['total_characters'],
            'average_chars_per_file': self.stats['total_characters'] // max(self.stats['successful_extractions'], 1)
        }
    
    def reset_stats(self):
        """Reinicia las estadísticas de procesamiento"""
        self.stats = {
            'files_processed': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_pages': 0,
            'total_characters': 0,
        }


def extract_text_from_pdf(pdf_path: str, method: str = "auto") -> str:
    """Función de conveniencia para extraer texto de un PDF"""
    parser = LegalPDFParser()
    result = parser.extract_text_from_pdf(pdf_path, method)
    return result['text'] if result['success'] else ""


def process_pdfs_in_directory(directory: str) -> Dict[str, str]:
    """Función de conveniencia para procesar todos los PDFs de un directorio"""
    parser = LegalPDFParser()
    results = parser.extract_all_pdfs_from_directory(directory)
    
    # Retornar solo el texto extraído por archivo
    text_results = {}
    for filename, result in results["files"].items():
        if result['success']:
            text_results[filename] = result['text']
        else:
            text_results[filename] = ""
    
    return text_results 