import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Generador Ultra Visible", layout="wide")

if 'banner_pro' not in st.session_state:
    st.session_state.banner_pro = None

# --- PANEL LATERAL ---
st.sidebar.header("🚀 Ajustes de Visibilidad")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
# Forzamos un ancho menor para que la letra "crezca" proporcionalmente
ancho_hoja = 650 
font_size_main = st.sidebar.slider("Tamaño de letra", 45, 85, 60)

st.title("📲 Generador Especial para Estados")

uploaded_file = st.file_uploader("1. Sube tu banner", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_pro = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista:", height=200)

def procesar_lista_ultra(texto, plus):
    lineas_finales = []
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas_finales.append(f"🔥 LISTA ACTUALIZADA: {fecha_hoy} 🔥")
    
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "actualizada"]
    raw_lines = texto.split('\n')
    
    for i in range(len(raw_lines)):
        l = raw_lines[i].strip()
        if not l or any(b in l.lower() for b in basura) or "———" in l:
            continue
        
        # Unir colores para ahorrar espacio vertical
        if (l.startswith("-") or l.startswith("⁠-") or l.startswith("•")) and lineas_finales:
            det_limpio = l.replace("-", "").replace("•", "").strip()
            lineas_finales[-1] += f" ({det_limpio})"
            continue

        nueva = l
        if "$" in l or "=" in l:
            nueva = re.sub(r'(\d{3,4})', lambda m: str(int(m.group(1)) + plus) if int(m.group(1)) > 150 else m.group(1), l)
        
        nueva = nueva.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "").strip()
        lineas_finales.append(nueva)
            
    return lineas_finales

def dibujar_ultra(lineas):
    # Banner
    if st.session_state.banner_pro:
        banner = st.session_state.banner_pro.copy()
        w_percent = (ancho_hoja / float(banner.size[0]))
        h_size = 180 
        banner = banner.resize((ancho_hoja, int(banner.size[1] * w_percent)), Image.Resampling.LANCZOS)
        banner = banner.crop((0, 0, ancho_ho_ja, h_size))
    else:
        h_size = 100
        banner = Image.new('RGB', (ancho_hoja, h_size), color="#111111")

    # Espaciado apretado
    interlineado = 6 
    alto_total = h_size + (len(lineas) * (font_size_main + interlineado)) + 60
    
    # FONDO NEGRO para resaltar más
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="#000000")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size_main)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", int(font_size_main*0.7))
    except:
        font_bold = font_small = ImageFont.load_default()

    y = h_size + 20
    for i, line in enumerate(lineas):
        if i == 0: # Fecha
            color = "#FFD700" # Dorado
            fnt = font_small
            draw.text((20, y), line, font=fnt, fill=color)
            y += int(font_size_main*0.7) + 15
        elif "INGRESO" in line or "TESTERS" in line or "IPHONE" in line.upper():
            color = "#00D4FF" # Celeste Neón
            draw.text((20, y), line.upper(), font=font_bold, fill=color)
            y += font_size_main + interlineado + 5
        else:
            color = "#FFFFFF" # Blanco puro
            draw.text((20, y), line, font=font_bold, fill=color)
            y += font_size_main + interlineado
            
    return img

if st.button("🚀 GENERAR LISTA ULTRA VISIBLE"):
    if input_text:
        lineas = procesar_lista_ultra(input_text, comision)
        resultado = dibujar_ultra(lineas)
        buf = io.BytesIO()
        resultado.save(buf, format="PNG")
        st.divider()
        st.image(resultado)
        st.download_button("📥 Descargar", buf.getvalue(), "lista_estado.png")
