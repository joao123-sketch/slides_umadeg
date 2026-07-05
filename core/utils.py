import logging
import re

def setup_logger(name: str) -> logging.Logger:
    """Configura e retorna um logger padronizado."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def clean_text(text: str) -> str:
    """Remove quebras de linha excessivas e espaços duplicados."""
    if not text:
        return ""
    # Substitui quebras de linha dentro de parágrafos por espaço
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    # Remove espaços duplos
    text = re.sub(r' +', ' ', text)
    return text.strip()

def split_text_for_slides(text: str, max_chars: int = 400) -> list[str]:
    """Divide um texto longo em partes menores para caber nos slides, sem quebrar palavras."""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > max_chars and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks
