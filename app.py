import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz 

st.set_page_config(page_title="Generador Pro Premium", page_icon="📲", layout="wide")

# --- MEMORIA DE SESIÓN ---
if 'lista_imagenes' not in st.session_state:
    st.session_state.lista_imagenes = []
if 'banner_pro' not in st.session_state:
    st.session_state.banner_pro = None

st.sidebar.header("🎨 Ajustes de Imagen")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_img = st.sidebar.slider("Ancho de imagen", 1200, 1600, 1500)
font_size = st.sidebar.slider("Tamaño de letra", 25, 45, 34)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 60, 35)

st.title("📲 Generador Premium con Banner Personalizado")

# --- SECCIÓN PARA SUBIR TU IMAGEN ---
st.subheader("1️⃣ Sube tu imagen de encabezado")
uploaded_banner = st.file_uploader("Sube la foto de los celulares aquí (JPG o PNG)", type=["jpg", "jpeg", "png"])

if uploaded_banner:
    st.session_state.banner_pro = Image.open(uploaded_banner)
    st.success("✅ Imagen cargada correctamente")

st.subheader("2️⃣ Pega tu lista")
input_text = st.text_area("Lista de productos:", height=200)

def procesar_texto(texto, incremento):
    lineas_limpias = []
    for linea in texto.split('\n'):
        l = linea.strip()
        if not l or len(l) < 2: continue
        
        # Filtro de batería: solo suma si hay $ o si el número está al final de la línea solo.
        nueva_linea = re.sub(r'(\$\s*)(\d{2,4})', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        if nueva_linea == l:
            nueva_linea = re.sub(r'([=–\-:\s]\s*)(\d{3,4})$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        lineas_limpias.append(nueva_linea)
    return lineas_limpias

def dibujar_imagen(lineas):
    # Usar el banner subido o crear uno negro si no hay nada
    if st.session_state.banner_pro:
        banner = st.session_state.banner_pro.copy()
        w_percent = (ancho_img / float(banner.size[0]))
        h_size = int((float(banner.size[1]) * float(w_percent)))
        banner = banner.resize((ancho_img, h_size), Image.Resampling.LANCZOS)
    else:
        h_size = 200
        banner = Image.new('RGB', (ancho_img, h_size), color="#000000")

    espacio_linea = 25
    alto_total = h_size + (len(lineas) * (font_size + espacio_linea)) + 120
    
    img = Image.new('RGB', (ancho_img, int(alto_total)), color="#FFFFFF")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    y = h_size + 60
    for line in lineas:
        color_txt = "#0056b3" if "*" in line else "#000000"
        # Quitamos los asteriscos estéticos y reemplazamos guiones por puntos
        clean_line = line.replace("*", "").replace("-", "•")
        draw.text((80, y), clean_line, font=font, fill=color_txt)
        y += font_size + espacio_linea
        
    return img

# --- BOTONES ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 GENERAR LISTA"):
        if input_text:
            lineas_finales = procesar_texto(input_text, comision)
            paginas = [lineas_finales[i:i + lineas_por_pag] for i in range(0, len(lineas_finales), lineas_por_pag)]
            
            st.session_state.lista_imagenes = [] 
            for pag in paginas:
                img_res = dibujar_imagen(pag)
                buf = io.BytesIO()
                img_res.save(buf, format="PNG")
                st.session_state.lista_imagenes.append({"pil": img_res, "bytes": buf.getvalue()})
        else:
            st.error("Pega la lista primero.")

with col2:
    if st.button("🗑️ NUEVA"):
        st.session_state.lista_imagenes = []
        st.rerun()

# --- MOSTRAR RESULTADOS ---
if st.session_state.lista_imagenes:
    for idx, item in enumerate(st.session_state.lista_imagenes):
        st.divider()
        st.image(item['pil'], use_container_width=True)
        st.download_button(f"📥 Descargar Parte {idx+1}", item['bytes'], f"lista_{idx+1}.png", "image/png")
