import fitz  # PyMuPDF
from pathlib import Path
from typing import Union
from io import BytesIO

from core.utils import setup_logger

logger = setup_logger(__name__)

class PDFReader:
    """Classe responsável por ler o arquivo PDF e extrair seu texto bruto."""
    
    @staticmethod
    def read_text(file_source: Union[str, Path, BytesIO]) -> str:
        """
        Lê o PDF e retorna todo o texto concatenado.
        Pode receber um caminho de arquivo ou um objeto BytesIO (Streamlit).
        """
        try:
            if isinstance(file_source, (str, Path)):
                doc = fitz.open(file_source)
            elif isinstance(file_source, BytesIO):
                doc = fitz.open(stream=file_source, filetype="pdf")
            else:
                raise ValueError("O formato do arquivo de origem não é suportado.")
                
            full_text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                full_text += page.get_text("text") + "\n"
                
            doc.close()
            return full_text
            
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo PDF: {e}")
            raise
