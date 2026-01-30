import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import os

st.set_page_config(page_title="Generador Premium con Logos", page_icon="📱")

st.title("📱 Generador con Encabezado de Marcas")

comision = st.sidebar.number_input("Comisión a sumar (USD)", value=50)
font_size = st.sidebar.slider("Tamaño de letra", 30, 60, 40)

input_text = st.text_area("Pega tu lista aquí:", height=300)

def procesar_universal(texto, incremento):
    patrones_corte = [r"⏰", r"📍", r"CABA", r"Condiciones de pago", r"🚨", r"⚠️", r"Consultar"]
    lineas = texto.split('\n')
    lineas_limpias = []
    for linea in lineas:
        if any(re.search(patron, linea, re.IGNORECASE) for patron in patrones_corte): break
        if "MARTES" in linea.upper() or "LISTA ACTUALIZADA" in linea.upper(): continue
        lineas_limpias.append(linea.replace('‼️', '!!').replace('🔺', '•').replace('🔻', '•'))

    resultado = []
    for linea in lineas_limpias:
        nueva_linea = re.sub(r'([=–\-]\s*\$?\s*)(\d+)', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        if nueva_linea == linea:
            nueva_linea = re.sub(r'(\$\s*)(\d+)$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        resultado.append(nueva_linea)
    return resultado

if st.button("Generar Imagen con Logos"):
    if input_text:
        lineas_finales = procesar_universal(input_text, comision)
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        
        # --- CONFIGURACIÓN DE ESPACIO PARA LOGOS ---
        logo_area_h = 250  # Espacio para los logos arriba
        font_size_encabezado = 45
        line_spacing = 20
        total_h = logo_area_h + 100 + (len(lineas_finales) * (font_size + line_spacing)) + 100
        
        img = Image.new('RGB', (1080, int(total_h)), color="#FFFFFF")
        draw = ImageDraw.Draw(img)

        # --- PEGAR LOGOS ---
        logos = ["logo_apple.png", "logo_samsung.png", "logo_motorola.png", "logo_xiaomi.png"]
        x_offset = 100
        for logo_name in logos:
            if os.path.exists(logo_name):
                logo_img = Image.open(logo_name).convert("RGBA")
                # Redimensionar logo para que quepa (ej: 150px de ancho)
                logo_img.thumbnail((150, 150))
                # Pegar logo usando su propio canal alfa para transparencia
                img.paste(logo_img, (x_offset, 50), logo_img)
                x_offset += 230 # Espacio entre logos

        # --- DIBUJAR TEXTO ---
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size_encabezado)
        except:
            font = ImageFont.load_default()
            font_fecha = ImageFont.load_default()

        # Fecha y Separador
        draw.text((80, 220), f"📅 PRECIOS ACTUALIZADOS: {fecha_hoy}", font=font_fecha, fill="#000000")
        draw.line([(80, 280), (1000, 280)], fill="#CCCCCC", width=5)

        y = 330
        for line in lineas_finales:
            draw.text((80, y), line, font=font, fill="#000000")
            y += font_size + line_spacing
            
        st.image(img)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("📥 Descargar Imagen con Logos", buf.getvalue(), "lista_marcas.png")
