import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
import os
from datetime import datetime
import pytz 

st.set_page_config(page_title="Generador Pro Premium", page_icon="📲", layout="wide")

# --- CONFIGURACIÓN DE IMAGEN DE ENCABEZADO ---
# Cambia "encabezado.jpg" por el nombre exacto de tu archivo
IMAGEN_BANNER = "encabezado.jpg" 

if 'lista_imagenes' not in st.session_state:
    st.session_state.lista_imagenes = []

st.sidebar.header("🎨 Ajustes de Imagen")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_img = st.sidebar.slider("Ancho de imagen", 1200, 1600, 1500)
font_size = st.sidebar.slider("Tamaño de letra", 25, 45, 34)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 60, 35)

st.title("📲 Generador con Encabezado Fijo")
input_text = st.text_area("Pega tus listas aquí:", height=250)

def procesar_texto(texto, incremento):
    lineas_limpias = []
    for linea in texto.split('\n'):
        l = linea.strip()
        if not l or len(l) < 2: continue
        
        # --- FIX DE BATERÍA 100% ---
        # Solo suma si el número tiene un "$" o está solo al final de la línea.
        # Esto ignora el 100 de (85-100%) porque tiene un "%" o ")" después.
        nueva_linea = re.sub(r'(\$\s*)(\d{2,4})', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        if nueva_linea == l:
            nueva_linea = re.sub(r'([=–\-:\s]\s*)(\d{3,4})$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        
        lineas_limpias.append(nueva_linea)
    return lineas_limpias

def dibujar_imagen(lineas, titulo_pag):
    # Cargar el banner
    try:
        banner = Image.open(IMAGEN_BANNER)
        # Ajustar el banner al ancho seleccionado manteniendo proporción
        w_percent = (ancho_img / float(banner.size[0]))
        h_size = int((float(banner.size[1]) * float(w_percent)))
        banner = banner.resize((ancho_img, h_size), Image.Resampling.LANCZOS)
    except Exception as e:
        st.error(f"No se pudo cargar la imagen {IMAGEN_BANNER}. Verifica el nombre.")
        # Banner de emergencia si no encuentra la imagen
        banner = Image.new('RGB', (ancho_img, 200), color="#000000")
        h_size = 200

    espacio_linea = 22
    margen_inferior = 100
    alto_total = h_size + (len(lineas) * (font_size + espacio_linea)) + margen_inferior
    
    img = Image.new('RGB', (ancho_img, int(alto_total)), color="#FFFFFF")
    img.paste(banner, (0, 0)) # Pegamos tu imagen arriba
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    y = h_size + 50 # Empezamos a escribir debajo de tu imagen
    for line in lineas:
        color_txt = "#0056b3" if "*" in line else "#000000"
        x_pos = 60 if "*" in line else 80
        clean_line = line.replace("*", "").replace("-", "•")
        draw.text((x_pos, y), clean_line, font=font, fill=color_txt)
        y += font_size + espacio_linea
        
    return img

col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 GENERAR CON MI IMAGEN"):
        if input_text:
            if not os.path.exists(IMAGEN_BANNER):
                st.warning(f"⚠️ ¡Atención! No encontré el archivo '{IMAGEN_BANNER}'. Usaré un fondo negro por ahora.")
            
            lineas_finales = procesar_texto(input_text, comision)
            paginas = [lineas_finales[i:i + lineas_por_pag] for i in range(0, len(lineas_finales), lineas_por_pag)]
            
            st.session_state.lista_imagenes = [] 
            for idx, pag in enumerate(paginas):
                img_res = dibujar_imagen(pag, f"PARTE {idx+1}")
                buf = io.BytesIO()
                img_res.save(buf, format="PNG")
                st.session_state.lista_imagenes.append({"pil": img_res, "bytes": buf.getvalue()})
        else:
            st.error("Pega la lista.")

with col2:
    if st.button("🗑️ NUEVA"):
        st.session_state.lista_imagenes = []
        st.rerun()

if st.session_state.lista_imagenes:
    for idx, item in enumerate(st.session_state.lista_imagenes):
        st.divider()
        st.image(item['pil'], use_container_width=True)
        st.download_button(f"📥 Descargar Parte {idx+1}", item['bytes'], f"lista_{idx+1}.png", "image/png")
