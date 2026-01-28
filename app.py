import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Pro iPhone", page_icon="📲")

# --- INTERFAZ ---
st.title("📲 Generador Pro (Sin Cortes)")
comision = st.sidebar.number_input("Comisión a sumar (USD)", value=50)
font_size = st.sidebar.slider("Tamaño de letra", 30, 60, 42)
line_spacing = st.sidebar.slider("Espaciado entre líneas", 10, 50, 25)

input_text = st.text_area("Pega la lista aquí:", height=300)

def procesar_lista(texto, incremento):
    patrones_corte = [r"⏰", r"📍", r"CABA", r"Lunes a viernes", r"💵", r"📦"]
    lineas = texto.split('\n')
    lineas_limpias = []
    for linea in lineas:
        if any(re.search(patron, linea, re.IGNORECASE) for patron in patrones_corte):
            break
        # Limpieza para evitar cuadraditos
        l = linea.replace('‼️', '!!').replace('🔺', '•').replace('🔻', '•').replace('◼️', '---')
        lineas_limpias.append(l)
    
    texto_filtrado = "\n".join(lineas_limpias)

    def substituir(match):
        return f"{match.group(1)}{int(match.group(2)) + incremento}{match.group(3)}"
    
    pattern = r'([=:]\s*)(\d+)(\s*\$?)'
    return re.sub(pattern, substituir, texto_filtrado).strip()

if st.button("Generar Imagen Completa"):
    if input_text:
        texto_final = procesar_lista(input_text, comision)
        lineas_finales = texto_final.split('\n')
        
        # --- CÁLCULO DINÁMICO DEL ALTO ---
        # Calculamos cuánto espacio ocupa el texto realmente
        margin_top = 100
        margin_bottom = 100
        total_line_height = font_size + line_spacing
        # El alto de la imagen se adapta a la cantidad de líneas
        dynamic_height = margin_top + (len(lineas_finales) * total_line_height) + margin_bottom
        
        # Mantenemos el ancho estándar de 1080 (HD)
        img = Image.new('RGB', (1080, int(dynamic_height)), color="#FFFFFF")
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Dibujar el texto
        y_offset = margin_top
        for line in lineas_finales:
            draw.text((80, y_offset), line, font=font, fill="#000000")
            y_offset += total_line_height
            
        st.image(img, caption="Imagen generada (Largo ajustable)")
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("📥 Descargar Imagen Larga", buf.getvalue(), "lista_completa.png", "image/png")
    else:
        st.warning("Pega la lista primero.")
