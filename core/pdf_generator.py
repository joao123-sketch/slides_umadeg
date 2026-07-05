import fitz
import os
from typing import List
from core.models import Slide
from core.utils import setup_logger

logger = setup_logger(__name__)

class PDFGenerator:
    """Classe responsável por transformar uma lista de Slides num arquivo PDF."""
    
    def __init__(self, slides: List[Slide]):
        self.slides = slides
        self.width = 960
        self.height = 540
        
        # Paleta de Cores mais limpa
        self.c_primary = (0.0, 138/255, 122/255)       # #008A7A
        self.c_primary_dark = (0.0, 77/255, 64/255)    # Verde ainda mais escuro
        self.c_accent = (247/255, 148/255, 29/255)     # #F7941D
        self.c_bg = (250/255, 250/255, 250/255)        # #FAFAFA (quase branco)
        self.c_text = (31/255, 31/255, 31/255)         # #1F1F1F
        
    def generate(self, output_path: str):
        logger.info("Iniciando geração de PDF...")
        doc = fitz.open()
        
        base_dir = os.path.dirname(os.path.dirname(__file__))
        font_regular = os.path.join(base_dir, "fonte", "static", "RobotoSlab-Regular.ttf")
        font_bold = os.path.join(base_dir, "fonte", "static", "RobotoSlab-Bold.ttf")
        logo_path = os.path.join(base_dir, "fonte", "logo.png")
        
        has_logo = os.path.exists(logo_path)
        
        for slide in self.slides:
            page = doc.new_page(width=self.width, height=self.height)
            
            try:
                page.insert_font(fontname="roboto", fontfile=font_regular)
                page.insert_font(fontname="robotob", fontfile=font_bold)
            except Exception as e:
                logger.warning(f"Não foi possível carregar a fonte RobotoSlab: {e}")
                page.insert_font(fontname="roboto", fontbuffer=fitz.Font("helv").buffer)
                page.insert_font(fontname="robotob", fontbuffer=fitz.Font("hebo").buffer)

            # Background Geral mais clean
            page.draw_rect(fitz.Rect(0, 0, self.width, self.height), color=self.c_bg, fill=self.c_bg)
            
            # Adicionar Logo no canto inferior direito
            if has_logo:
                # Ajuste o tamanho e a posição conforme a necessidade
                logo_w = 160
                logo_h = 55
                logo_rect = fitz.Rect(self.width - logo_w - 20, 20, self.width - 20, 20 + logo_h)
                page.insert_image(logo_rect, filename=logo_path, keep_proportion=True)
            
            if slide.is_cover or slide.is_section:
                # Estilo Centrado Clean - Títulos de Tópico centralizados
                title_rect = fitz.Rect(50, 160, self.width - 50, 300)
                page.insert_textbox(title_rect, slide.title, 
                                   fontname="robotob",
                                   fontsize=48, 
                                   color=self.c_primary_dark, 
                                   align=fitz.TEXT_ALIGN_CENTER)
                
                # Linha decorativa
                line_y = 310
                page.draw_line(fitz.Point(self.width / 2 - 100, line_y), fitz.Point(self.width / 2 + 100, line_y), color=self.c_accent, width=3)
                
                # Subtítulo ou conteúdo logo abaixo
                if slide.content:
                    content_rect = fitz.Rect(50, 330, self.width - 50, 480)
                    page.insert_textbox(content_rect, slide.content, 
                                       fontname="roboto",
                                       fontsize=32, 
                                       color=self.c_text, 
                                       align=fitz.TEXT_ALIGN_CENTER)
                
                # Data escura pequena no rodapé (se tiver espaço)
                if slide.date:
                    date_rect = fitz.Rect(50, self.height - 50, self.width - 50, self.height - 20)
                    page.insert_textbox(date_rect, slide.date, 
                                       fontname="robotob",
                                       fontsize=20, 
                                       color=(0.3, 0.3, 0.3), 
                                       align=fitz.TEXT_ALIGN_CENTER)
                                       
            else:
                # Estilo Padrão (Sem header sólido, título no topo esquerdo)
                title_rect = fitz.Rect(50, 30, self.width - 220, 110)
                page.insert_textbox(title_rect, slide.title, 
                                   fontname="robotob",
                                   fontsize=36, 
                                   color=self.c_primary_dark, 
                                   align=fitz.TEXT_ALIGN_LEFT)
                
                # Linha decorativa fina laranja
                page.draw_line(fitz.Point(50, 115), fitz.Point(self.width - 50, 115), color=self.c_accent, width=2)
                
                # Texto grande
                text_rect = fitz.Rect(50, 135, self.width - 50, self.height - 30)
                
                page.insert_textbox(text_rect, slide.content, 
                                   fontname="roboto",
                                   fontsize=28, 
                                   color=self.c_text, 
                                   align=fitz.TEXT_ALIGN_JUSTIFY)
                
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        doc.close()
        logger.info(f"PDF salvo com sucesso em: {output_path}")
        return output_path
