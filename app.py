import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Pro iPhone", page_icon="📲")

# --- INTERFAZ ---
st.title("📲 Generador de Estados Premium")
comision = st.sidebar.number_input("Comisión a sumar (USD)", value=50)
font_size = st.sidebar.slider("Tamaño de letra", 40, 80, 55) # Subí el rango
bg_color = "#121212" # Fondo oscuro elegante

input_text = st.text_area("Pega la lista aquí:", height=300)

def procesar_lista(texto, incremento):
    # Filtro de dirección y limpieza
    patrones_corte = [r"⏰", r"📍", r"CABA", r"Lunes a viernes", r"💵", r"📦"]
    lineas = texto.split('\n')
    lineas_limpias = []
    for linea in lineas:
        if any(re.search(patron, linea, re.IGNORECASE) for patron in patrones_corte):
            break
        # Limpiar caracteres raros que rompen la fuente básica
        l = linea.replace('‼️', '!!').replace('🔺', '>').replace('🔻', '>').replace('◼️', '---')
        lineas_limpias.append(l)
    
    texto_filtrado = "\n".join(lineas_limpias)

    # Sumar comisión
    def substituir(match):
        return f"{match.group(1)}{int(match.group(2)) + incremento}{match.group(3)}"
    
    pattern = r'([=:]\s*)(\d+)(\s*\$?)'
    return re.sub(pattern, substituir, texto_filtrado).strip()

if st.button("Generar Imagen"):
    if input_text:
        texto_final = procesar_lista(input_text, comision)
        
        # Crear imagen vertical (1080x1920)
        img = Image.new('RGB', (1080, 1920), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Intentar cargar fuente del sistema
        try:
            # En servidores Linux/Streamlit suele estar DejaVuSans
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Dibujar el texto con mejor espaciado
        y_offset = 150
        margin_left = 80
        line_spacing = 25 # Espacio extra entre líneas
        
        for line in texto_final.split('\n'):
            # Dibujar sombra para que resalte
            draw.text((margin_left+2, y_offset+2), line, font=font, fill="#000000")
            # Dibujar texto blanco
            draw.text((margin_left, y_offset), line, font=font, fill="#FFFFFF")
            y_offset += font_size + line_spacing
            
        st.image(img, caption="Imagen Optimizada")
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("📥 Descargar para WhatsApp", buf.getvalue(), "estado.png", "image/png")
