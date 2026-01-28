import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Pro iPhone", page_icon="📲")

# --- INTERFAZ ---
st.title("📲 Generador Blanco & Negro")
comision = st.sidebar.number_input("Comisión a sumar (USD)", value=50)
font_size = st.sidebar.slider("Tamaño de letra", 30, 70, 45)
# Invertimos los colores aquí
bg_color = "#FFFFFF" # Blanco
text_color = "#000000" # Negro

input_text = st.text_area("Pega la lista aquí:", height=300)

def procesar_lista(texto, incremento):
    # Filtro de dirección y limpieza
    patrones_corte = [r"⏰", r"📍", r"CABA", r"Lunes a viernes", r"💵", r"📦"]
    lineas = texto.split('\n')
    lineas_limpias = []
    for linea in lineas:
        if any(re.search(patron, linea, re.IGNORECASE) for patron in patrones_corte):
            break
        # Limpieza de símbolos que no se ven bien en blanco y negro
        l = linea.replace('‼️', '!!').replace('🔺', '•').replace('🔻', '•').replace('◼️', '---')
        lineas_limpias.append(l)
    
    texto_filtrado = "\n".join(lineas_limpias)

    # Sumar comisión
    def substituir(match):
        return f"{match.group(1)}{int(match.group(2)) + incremento}{match.group(3)}"
    
    pattern = r'([=:]\s*)(\d+)(\s*\$?)'
    return re.sub(pattern, substituir, texto_filtrado).strip()

if st.button("Generar Imagen Blanca"):
    if input_text:
        texto_final = procesar_lista(input_text, comision)
        
        # Crear imagen vertical (1080x1920)
        img = Image.new('RGB', (1080, 1920), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Intentar cargar fuente
        try:
            # Esta ruta suele funcionar en Streamlit Cloud
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Dibujar el texto
        y_offset = 150
        margin_left = 100
        line_spacing = 30 
        
        for line in texto_final.split('\n'):
            # Escribir directamente en negro
            draw.text((margin_left, y_offset), line, font=font, fill=text_color)
            y_offset += font_size + line_spacing
            
        st.image(img, caption="Vista previa (Blanco y Negro)")
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("📥 Descargar para WhatsApp", buf.getvalue(), "estado_blanco.png", "image/png")
