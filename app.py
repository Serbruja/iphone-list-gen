import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Pro", layout="wide")

# --- ESTADO DE SESIÓN ---
if 'banner_pro' not in st.session_state:
    st.session_state.banner_pro = None

# --- BARRA LATERAL (Simplificada y potente) ---
st.sidebar.header("🎨 Ajustes de Lista")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
# Un ancho de 700-800 es el secreto para que en WhatsApp se vea gigante
ancho_hoja = st.sidebar.slider("Ancho de imagen", 600, 900, 750)
font_size = st.sidebar.slider("Tamaño de letra", 40, 70, 50)

st.title("📲 Generador de Lista Optimizado")

# 1. CARGA DE IMAGEN
uploaded_file = st.file_uploader("Sube tu encabezado aquí", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_pro = Image.open(uploaded_file)

# 2. ENTRADA DE TEXTO
input_text = st.text_area("Pega tu lista aquí:", height=200)

def procesar_texto(texto, incremento):
    resultado = []
    for linea in texto.split('\n'):
        l = linea.strip()
        if not l or len(l) < 2: continue
        # Lógica de precio: suma si tiene $ o si es un número solo al final
        nueva = re.sub(r'(\$\s*)(\d{2,4})', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        if nueva == l:
            nueva = re.sub(r'([=–\-:\s]\s*)(\d{3,4})$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        resultado.append(nueva)
    return resultado

def dibujar_imagen(lineas):
    # AJUSTE DE BANNER: Lo hacemos una franja delgada
    if st.session_state.banner_pro:
        banner = st.session_state.banner_pro.copy()
        w_percent = (ancho_hoja / float(banner.size[0]))
        h_size = int((float(banner.size[1]) * float(w_percent)))
        banner = banner.resize((ancho_hoja, h_size), Image.Resampling.LANCZOS)
        
        # CORTAMOS la imagen para que solo use los primeros 250px de alto
        # Así no "empuja" el texto hacia abajo
        if h_size > 280:
            banner = banner.crop((0, 0, ancho_hoja, 280))
            h_size = 280
    else:
        h_size = 100
        banner = Image.new('RGB', (ancho_hoja, h_size), color="#1E1E1E")

    # Espaciado apretado para que no se vea "roto"
    interlineado = 12 
    alto_texto = len(lineas) * (font_size + interlineado)
    alto_total = h_size + alto_texto + 60
    
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="#FFFFFF")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    y = h_size + 30
    for line in lineas:
        # Colores: Azul para títulos con asterisco, negro para el resto
        color_txt = "#004a99" if "*" in line else "#000000"
        clean_line = line.replace("*", "").replace("-", "•")
        
        draw.text((35, y), clean_line, font=font, fill=color_txt)
        y += font_size + interlineado
        
    return img

if st.button("🚀 GENERAR LISTA"):
    if input_text:
        lineas_finales = procesar_texto(input_text, comision)
        # Generamos una sola imagen larga para que no se corte el diseño
        img_res = dibujar_imagen(lineas_finales)
        
        buf = io.BytesIO()
        img_res.save(buf, format="PNG")
        
        st.divider()
        st.image(img_res, use_container_width=True)
        st.download_button("📥 Descargar Lista Completa", buf.getvalue(), "lista_pro.png", "image/png")
    else:
        st.error("Pega la lista.")
