from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Subtopic:
    number: int
    title: str
    content: str

@dataclass
class Topic:
    number_roman: str
    title: str
    subtopics: List[Subtopic] = field(default_factory=list)

@dataclass
class Lesson:
    title: str = ""
    subtitle: str = ""
    date: str = ""
    
    main_text: str = ""
    main_text_reference: str = ""
    
    summary: str = ""
    
    biblical_text: str = ""
    introduction: str = ""
    
    topics: List[Topic] = field(default_factory=list)
    
    conclusion: str = ""
    
    def is_valid(self) -> bool:
        """Verifica se a lição tem o mínimo necessário para gerar slides."""
        return bool(self.title and self.topics)

    def generate_slides(self) -> List['Slide']:
        """Converte a estrutura da lição em uma lista de slides para visualização e exportação."""
        from core.utils import split_text_for_slides
        slides = []
        
        # 1. Slide de Capa
        full_title = f"{self.title}: {self.subtitle}" if self.subtitle else self.title
        slides.append(Slide(
            title=full_title,
            content="",
            date=self.date,
            is_cover=True
        ))

        # 2. Texto Principal
        if self.main_text:
            self._add_multipage_to_list(slides, "Texto Principal", self.main_text)

        # 3. Resumo
        if self.summary:
            self._add_multipage_to_list(slides, "Resumo da Lição", self.summary)

        # 4. Tópicos
        for topic in self.topics:
            # Slide de Seção
            slides.append(Slide(
                title=f"Tópico {topic.number_roman}",
                content=topic.title,
                is_section=True
            ))
            
            # Subtópicos
            for sub in topic.subtopics:
                title_str = f"{sub.number}. {sub.title}"
                self._add_multipage_to_list(slides, title_str, sub.content)

        # 5. Conclusão
        if self.conclusion:
            self._add_multipage_to_list(slides, "Conclusão", self.conclusion)

        return slides

    def _add_multipage_to_list(self, slides: List['Slide'], title: str, text: str, max_chars: int = 480):
        if not text.strip():
            return
            
        from core.utils import split_text_for_slides
        chunks = split_text_for_slides(text, max_chars=max_chars)
        
        for chunk in chunks:
            if chunk.strip():
                # O nome do ponto se repete igual, sem (Cont.)
                slides.append(Slide(title=title, content=chunk.strip()))

@dataclass
class Slide:
    title: str
    content: str
    date: str = ""
    is_cover: bool = False
    is_section: bool = False
    is_bullet: bool = False
