import re
from core.models import Lesson, Topic, Subtopic
from core.utils import clean_text, setup_logger

logger = setup_logger(__name__)

class Parser:
    """Classe responsável por analisar o texto do PDF e extrair os dados da lição."""
    
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.lesson = Lesson()
        
    def _extract_section(self, start_marker: str, end_marker: str = None) -> str:
        """Extrai o texto bruto entre dois marcadores (sem limpar quebras de linha ainda)."""
        start_pattern = re.escape(start_marker)
        
        if end_marker:
            end_pattern = re.escape(end_marker)
            pattern = re.compile(rf"{start_pattern}(.*?)(?={end_pattern})", re.IGNORECASE | re.DOTALL)
        else:
            pattern = re.compile(rf"{start_pattern}(.*)", re.IGNORECASE | re.DOTALL)
            
        match = pattern.search(self.raw_text)
        if match:
            return match.group(1).strip()
        
        return ""
        
    def _extract_header(self):
        title_match = re.search(r"Lição\s+\d+:\s*(.*?)(?=\nData:)", self.raw_text, re.IGNORECASE | re.DOTALL)
        if title_match:
            full_title = clean_text(title_match.group(1))
            parts = full_title.split(":")
            if len(parts) > 1:
                self.lesson.title = parts[0].strip()
                self.lesson.subtitle = ":".join(parts[1:]).strip()
            else:
                self.lesson.title = full_title
                
        date_match = re.search(r"Data:\s*(.*?)\n", self.raw_text, re.IGNORECASE)
        if date_match:
            self.lesson.date = clean_text(date_match.group(1))

    def _extract_basic_sections(self):
        texto_principal = self._extract_section("T E X T O P R I N C I P A L", "R E S U M O D A L I Ç Ã O")
        self.lesson.main_text = clean_text(texto_principal)
        
        resumo_raw = self._extract_section("R E S U M O D A L I Ç Ã O", "L E I T U R A S E M A N A L")
        # Remove lixos do rodapé do PDF no resumo
        resumo_limpo = resumo_raw.split("Lições CPAD")[0]
        self.lesson.summary = clean_text(resumo_limpo)

    def _extract_biblical_text_and_intro(self):
        biblical_raw = self._extract_section("T E X T O B Í B L I C O", "C O M E N T Á R I O D A L I Ç Ã O")
        self.lesson.biblical_text = clean_text(biblical_raw)
        
        comentario_raw = self._extract_section("C O M E N T Á R I O D A L I Ç Ã O", "CONCLUSÃO")
        
        intro_match = re.search(r"INTRODUÇÃO(.*?)I\.", comentario_raw, re.IGNORECASE | re.DOTALL)
        if intro_match:
            self.lesson.introduction = clean_text(intro_match.group(1))

    def _extract_topics(self):
        comentario_raw = self._extract_section("C O M E N T Á R I O D A L I Ç Ã O", "CONCLUSÃO")
        
        topic_pattern = re.compile(r"\n\s*([IVX]+)\.\s+([A-ZÇÃÕÁÉÍÓÚÊÂÔ\s]+?)(?=\n)", re.MULTILINE)
        
        matches = list(topic_pattern.finditer(comentario_raw))
        
        for i, match in enumerate(matches):
            roman = match.group(1).strip()
            title = clean_text(match.group(2))
            
            topic = Topic(number_roman=roman, title=title)
            
            start_pos = match.end()
            if i + 1 < len(matches):
                end_pos = matches[i+1].start()
            else:
                end_pos = len(comentario_raw)
                
            topic_content = comentario_raw[start_pos:end_pos]
            
            topic_content = re.sub(r"S U B S Í D I O.*?(?=\n\s*\d+\.\s+|$)", "", topic_content, flags=re.DOTALL)
            
            subtopic_pattern = re.compile(r"\n\s*(\d+)\.\s+(.*?)\.(.*?)(?=\n\s*\d+\.\s+|$)", re.DOTALL)
            for sub_match in subtopic_pattern.finditer(topic_content):
                num = int(sub_match.group(1).strip())
                sub_title = clean_text(sub_match.group(2))
                sub_content = clean_text(sub_match.group(3))
                topic.subtopics.append(Subtopic(number=num, title=sub_title, content=sub_content))
                
            self.lesson.topics.append(topic)

    def _extract_conclusion(self):
        conc_raw = self._extract_section("CONCLUSÃO", "H O R A D A R E V I S Ã O")
        if not conc_raw:
            # Caso não tenha Hora da Revisão no final, pegar até o EOF
            conc_raw = self._extract_section("CONCLUSÃO")
            
        self.lesson.conclusion = clean_text(conc_raw.split("H O R A D A R E V I S Ã O")[0])

    def parse(self) -> Lesson:
        logger.info("Iniciando parser do texto...")
        try:
            self._extract_header()
            self._extract_basic_sections()
            self._extract_biblical_text_and_intro()
            self._extract_topics()
            self._extract_conclusion()
            logger.info("Parser finalizado com sucesso.")
        except Exception as e:
            logger.error(f"Erro durante o parser: {e}")
            
        return self.lesson
