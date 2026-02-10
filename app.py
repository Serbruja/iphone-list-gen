import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Premium", layout="wide")

if 'lista_imagenes' not in st.session_state:
    st.session_state.lista_imagenes = []
if 'banner_pro' not in st.session_state:
    st.session_state.banner_pro = None

# --- BARRA LATERAL (Valores optimizados) ---
st.sidebar.header("🎨 Ajustes de Diseño")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
# Bajamos el ancho máximo a 900 para que la letra "llene" más la imagen
ancho_hoja = st.sidebar.slider("Ancho de imagen", 700, 1000, 850)
# Subimos el tamaño base de letra
font_size = st.sidebar.slider("Tamaño de letra", 40, 80, 55)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 10, 40, 25)

st.title("📲 Generador de Listas Pro")

# 1. SUBIDA DE IMAGEN
uploaded_banner = st.file_uploader("Sube tu encabezado", type=["jpg", "png"])
if uploaded_banner:
    st.session_state.banner_pro = Image.open(uploaded_banner)

# 2. ENTRADA DE TEXTO
input_text = st.text_area("Pega tu lista aquí:", height=200)

def procesar_texto(texto, incremento):
    resultado = []
    for linea in texto.split('\n'):
        l = linea.strip()
        if not l or len(l) < 2: continue
        
        # Filtro de precio seguro
        nueva = re.sub(r'(\$\s*)(\d{2,4})', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        if nueva == l:
            nueva = re.sub(r'([=–\-:\s]\s*)(\d{3,4})$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        resultado.append(nueva)
    return resultado

def dibujar_imagen(lineas):
    # Reducimos el espacio entre líneas para que no se vea tan "estirado"
    interlineado = 15 
    alto_texto = len(lineas) * (font_size + interlineado)
    
    # Manejo del Banner (Lo limitamos para que no coma toda la pantalla)
    if st.session_state.banner_pro:
        banner = st.session_state.banner_pro.copy()
        w_percent = (ancho_hoja / float(banner.size[0]))
        h_size = int((float(banner.size[1]) * float(w_percent)))
        # Si la imagen es muy alta, la cortamos o limitamos
        if h_size > 400: h_size = 400 
        banner = banner.resize((ancho_hoja, h_size), Image.Resampling.LANCZOS)
    else:
        h_size = 120
        banner = Image.new('RGB', (ancho_hoja, h_size), color="#000000")

    alto_total = h_size + alto_texto + 80
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="#FFFFFF")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    y = h_size + 30
    for line in lineas:
        # Colores según tipo de línea
        color_txt = "#0056b3" if "*" in line or "#" in line else "#000000"
        clean_line = line.replace("*", "").replace("#", "").replace("-", "•")
        
        # Margen izquierdo pequeño para aprovechar el ancho
        draw.text((40, y), clean_line, font=font, fill=color_txt)
        y += font_size + interlineado
        
    return img

# --- BOTONES ---
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
        st.error("Pega el texto.")

# --- RESULTADOS ---
if st.session_state.lista_imagenes:
    for idx, item in enumerate(st.session_state.lista_imagenes):
        st.divider()
        st.image(item['pil'], use_container_width=True)
        st.download_button(f"📥 Descargar Parte {idx+1}", item['bytes'], f"lista_{idx+1}.png")
