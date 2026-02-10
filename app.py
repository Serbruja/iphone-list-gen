import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Pro Premium", layout="wide")

if 'banner_pro' not in st.session_state:
    st.session_state.banner_pro = None

# --- AJUSTES LATERALES ---
st.sidebar.header("🎨 Ajustes de Diseño")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_hoja = st.sidebar.slider("Ancho de imagen", 600, 900, 700) # 700 es ideal para WhatsApp
font_size = st.sidebar.slider("Tamaño de letra", 40, 80, 55)

st.title("📲 Generador de Lista de Precios")

# 1. CARGA DE ENCABEZADO
uploaded_file = st.file_uploader("Sube la imagen de los celulares", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_pro = Image.open(uploaded_file)

# 2. ENTRADA DE TEXTO
input_text = st.text_area("Pega tu lista original aquí:", height=250)

def procesar_texto_estricto(texto, incremento):
    lineas_finales = []
    for linea in texto.split('\n'):
        l = linea.strip()
        if not l or len(l) < 3: continue
        
        # --- FILTRO: ¿Es una línea de producto o título? ---
        # Solo aceptamos si tiene un "$" o si empieza con "*" (título)
        # Esto elimina automáticamente direcciones, horarios y encomiendas.
        if "$" in l or l.startswith("*"):
            # Si tiene precio, sumamos la comisión
            nueva = re.sub(r'(\$\s*)(\d{2,4})', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
            if nueva == l: # Intento extra por si el $ está al final
                nueva = re.sub(r'([=–\-:\s]\s*)(\d{3,4})$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
            
            # Limpieza de caracteres extra
            nueva = nueva.replace("*", "").replace("-", "•")
            lineas_finales.append(nueva)
            
    return lineas_finales

def dibujar_imagen(lineas):
    # Ajuste de Banner (Recorte tipo franja)
    if st.session_state.banner_pro:
        banner = st.session_state.banner_pro.copy()
        w_percent = (ancho_hoja / float(banner.size[0]))
        h_size = int((float(banner.size[1]) * float(w_percent)))
        banner = banner.resize((ancho_hoja, h_size), Image.Resampling.LANCZOS)
        
        # Cortamos para que no sea muy alta (máximo 220px)
        limite_h = 220
        if h_size > limite_h:
            banner = banner.crop((0, 0, ancho_hoja, limite_h))
            h_size = limite_h
    else:
        h_size = 100
        banner = Image.new('RGB', (ancho_hoja, h_size), color="#1E1E1E")

    # Diseño del texto
    interlineado = 15
    alto_texto = len(lineas) * (font_size + interlineado)
    alto_total = h_size + alto_texto + 80
    
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="#FFFFFF")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    y = h_size + 40
    for line in lineas:
        # Si la línea parece un título (ej: MOTOROLA), la ponemos en azul
        # Detectamos títulos porque suelen no tener "$"
        es_titulo = "$" not in line
        color_txt = "#004a99" if es_titulo else "#000000"
        
        draw.text((40, y), line, font=font, fill=color_txt)
        y += font_size + interlineado
        
    return img

if st.button("🚀 GENERAR LISTA LIMPIA"):
    if input_text:
        lineas_validas = procesar_texto_estricto(input_text, comision)
        if lineas_validas:
            img_res = dibujar_imagen(lineas_validas)
            buf = io.BytesIO()
            img_res.save(buf, format="PNG")
            
            st.divider()
            st.image(img_res, use_container_width=True)
            st.download_button("📥 Descargar Imagen", buf.getvalue(), "lista_final.png", "image/png")
        else:
            st.warning("No encontré productos con '$' en el texto.")
    else:
        st.error("Pega la lista primero.")
