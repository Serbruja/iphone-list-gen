import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Pro Premium", layout="wide")

if 'banner_pro' not in st.session_state:
    st.session_state.banner_pro = None

# --- AJUSTES ---
st.sidebar.header("🎨 Ajustes de Diseño")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_hoja = st.sidebar.slider("Ancho de imagen", 600, 900, 750)
font_size_main = st.sidebar.slider("Tamaño Modelos", 30, 60, 48)

st.title("📲 Generador de Lista Oficial")

uploaded_file = st.file_uploader("1. Sube el banner de los celulares", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_pro = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista (cualquier formato):", height=250)

def procesar_lista(texto, plus):
    lineas_limpias = []
    # Palabras prohibidas para limpiar la basura
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "actualizada"]
    
    for linea in texto.split('\n'):
        l = linea.strip()
        if not l or any(b in l.lower() for b in basura) or "———" in l:
            continue
        
        # SUMAR COMISIÓN (Solo a precios, no a baterías)
        # Busca números de 3 o 4 cifras que tengan un $ cerca o estén al final
        nueva = l
        if "$" in l or re.search(r'=\s*\d{3,4}', l):
            nueva = re.sub(r'(\d{3,4})', lambda m: str(int(m.group(1)) + plus) if int(m.group(1)) > 150 else m.group(1), l)
        
        # Limpieza de asteriscos y emojis de flechas
        nueva = nueva.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "")
        lineas_limpias.append(nueva)
    return lineas_limpias

def dibujar(lineas):
    # Proporción del Banner
    if st.session_state.banner_pro:
        banner = st.session_state.banner_pro.copy()
        w_percent = (ancho_hoja / float(banner.size[0]))
        h_size = int((float(banner.size[1]) * float(w_percent)))
        # Limitamos altura para que no sea gigante
        if h_size > 250:
            banner = banner.crop((0, 0, banner.size[0], int(250/w_percent)))
            h_size = 250
        banner = banner.resize((ancho_hoja, h_size), Image.Resampling.LANCZOS)
    else:
        h_size = 120
        banner = Image.new('RGB', (ancho_hoja, h_size), color="#000000")

    # Espaciado
    interlineado = 18
    alto_total = h_size + (len(lineas) * (font_size_main + interlineado)) + 100
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="#FFFFFF")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size_main)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", int(font_size_main*0.7))
    except:
        font_bold = font_small = ImageFont.load_default()

    y = h_size + 40
    for line in lineas:
        # LÓGICA DE COLORES
        if "◼️" in line or "INGRESO" in line or "TESTERS" in line:
            color = "#004a99" # Azul para títulos
            fnt = font_bold
            txt = line.replace("◼️", "").strip().upper()
        elif line.startswith("-") or "🔋" in line or "Grado" in line:
            color = "#666666" # Gris para detalles
            fnt = font_small
            txt = "   " + line # Sangría
        else:
            color = "#000000" # Negro para modelos
            fnt = font_bold
            txt = line
            
        draw.text((40, y), txt, font=fnt, fill=color)
        y += (font_size_main if fnt == font_bold else int(font_size_main*0.7)) + interlineado
        
    return img

if st.button("🚀 GENERAR LISTA PROFESIONAL"):
    if input_text:
        lineas = procesar_lista(input_text, comision)
        resultado = dibujar(lineas)
        buf = io.BytesIO()
        resultado.save(buf, format="PNG")
        st.image(resultado, use_container_width=True)
        st.download_button("📥 Descargar Imagen", buf.getvalue(), "lista.png")
