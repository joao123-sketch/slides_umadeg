import streamlit as st
import os
import fitz
from io import BytesIO
import time

from core.pdf_reader import PDFReader
from core.parser import Parser
from core.slide_generator import SlideGenerator
from core.pdf_generator import PDFGenerator

def render_preview(pdf_path: str):
    """Gera imagens do PDF para preview"""
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        images.append(img_bytes)
    doc.close()
    return images

def inject_custom_css():
    st.markdown("""
    <style>
        /* Variables from the user's color palette */
        :root {
            --primary: #008A7A;
            --primary-dark: #006D66;
            --primary-light: #00A596;
            --accent: #F7941D;
            --accent-dark: #F26A21;
            --bg: #F5F5F5;
            --surface: #FFFFFF;
            --text: #1F1F1F;
            --border: #D9D9D9;
        }

        /* Set App Background */
        .stApp {
            background-color: var(--bg);
            color: var(--text);
        }

        /* Buttons Styling */
        div.stButton > button:first-child {
            background-color: var(--primary) !important;
            color: var(--surface) !important;
            border: 1px solid var(--primary-dark) !important;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: var(--primary-dark) !important;
            color: var(--accent) !important;
            border-color: var(--accent) !important;
        }

        /* Progress Bar */
        .stProgress > div > div > div > div {
            background-color: var(--accent) !important;
        }

        /* Text headers */
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-dark) !important;
            font-family: 'Roboto Slab', serif;
        }
        
        /* Container boxes (Surface) */
        .css-1r6slb0, .st-emotion-cache-1r6slb0 {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="UMADEG Slides", page_icon="📖", layout="centered")
    inject_custom_css()
    
    if "preview_images" not in st.session_state:
        st.session_state.preview_images = []
    if "current_slide" not in st.session_state:
        st.session_state.current_slide = 0
    if "lesson_title" not in st.session_state:
        st.session_state.lesson_title = ""
    if "output_pptx" not in st.session_state:
        st.session_state.output_pptx = None
    if "output_pdf" not in st.session_state:
        st.session_state.output_pdf = None
    
    st.title("📖 UMADEG Slides")
    st.write("Gerador automático de slides com Design Moderno (RobotoSlab)")
    
    uploaded_file = st.file_uploader("Faça upload do PDF da lição", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Gerar Slides"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("Lendo arquivo PDF...")
                progress_bar.progress(20)
                file_stream = BytesIO(uploaded_file.getvalue())
                raw_text = PDFReader.read_text(file_stream)
                
                status_text.text("Analisando estrutura da lição...")
                progress_bar.progress(40)
                parser = Parser(raw_text)
                lesson = parser.parse()
                
                if not lesson.is_valid():
                    st.error("Não foi possível identificar a estrutura da lição neste PDF.")
                    progress_bar.empty()
                    status_text.empty()
                    return
                    
                slides = lesson.generate_slides()
                
                status_text.text("Gerando arquivo PowerPoint...")
                progress_bar.progress(60)
                output_dir = "output"
                os.makedirs(output_dir, exist_ok=True)
                safe_title = "".join([c for c in lesson.title if c.isalnum() or c in (' ', '-', '_')]).rstrip()
                
                output_pptx = os.path.join(output_dir, f"{safe_title}.pptx")
                pptx_gen = SlideGenerator(slides)
                pptx_gen.generate(output_pptx)
                
                status_text.text("Gerando versão em PDF...")
                progress_bar.progress(80)
                output_pdf = os.path.join(output_dir, f"{safe_title}.pdf")
                pdf_gen = PDFGenerator(slides)
                pdf_gen.generate(output_pdf)
                
                status_text.text("Preparando visualização...")
                progress_bar.progress(95)
                st.session_state.preview_images = render_preview(output_pdf)
                st.session_state.current_slide = 0
                st.session_state.lesson_title = lesson.title
                st.session_state.output_pptx = output_pptx
                st.session_state.output_pdf = output_pdf
                
                progress_bar.progress(100)
                status_text.text("Concluído!")
                time.sleep(1)
                status_text.empty()
                progress_bar.empty()
                
            except Exception as e:
                st.error(f"Ocorreu um erro durante a geração: {e}")
                progress_bar.empty()
                status_text.empty()

    if st.session_state.preview_images:
        st.divider()
        st.subheader("👀 Preview dos Slides")
        
        img_container = st.container()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Anterior", use_container_width=True):
                if st.session_state.current_slide > 0:
                    st.session_state.current_slide -= 1
                    
        with col2:
            st.markdown(f"<h4 style='text-align: center;'>Slide {st.session_state.current_slide + 1} de {len(st.session_state.preview_images)}</h4>", unsafe_allow_html=True)
            
        with col3:
            if st.button("Próximo ➡️", use_container_width=True):
                if st.session_state.current_slide < len(st.session_state.preview_images) - 1:
                    st.session_state.current_slide += 1
        
        with img_container:
            st.image(st.session_state.preview_images[st.session_state.current_slide], use_column_width=True)
            
        st.divider()
        
        st.subheader("📥 Exportar")
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            if os.path.exists(st.session_state.output_pptx):
                with open(st.session_state.output_pptx, "rb") as f:
                    st.download_button(
                        label="📄 Baixar PowerPoint (.pptx)",
                        data=f,
                        file_name=os.path.basename(st.session_state.output_pptx),
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )
                    
        with col_down2:
            if os.path.exists(st.session_state.output_pdf):
                with open(st.session_state.output_pdf, "rb") as f:
                    st.download_button(
                        label="📑 Baixar PDF (.pdf)",
                        data=f,
                        file_name=os.path.basename(st.session_state.output_pdf),
                        mime="application/pdf",
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()
