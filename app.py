import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime  # <-- Nueva librería para la fecha

st.set_page_config(page_title="Generador Pro Premium", layout="wide")

if 'banner_pro' not in st.session_state:
    st.session_state.banner_pro = None

# --- PANEL DE CONTROL ---
st.sidebar.header("🎨 Ajustes de Diseño")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_hoja = st.sidebar.slider("Ancho de imagen", 600, 900, 750)
font_size_main = st.sidebar.slider("Tamaño de letra", 40, 80, 55)

st.title("📲 Generador de Lista Oficial")

uploaded_file = st.file_uploader("1. Sube tu banner", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_pro = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista aquí:", height=250)

def procesar_lista_estilo_nuevo(texto, plus):
    lineas_finales = []
    # Agregamos la fecha automática al principio
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas_finales.append(f"LISTA ACTUALIZADA ({fecha_hoy})")
    
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "actualizada"]
    raw_lines = texto.split('\n')
    
    for i in range(len(raw_lines)):
        l = raw_lines[i].strip()
        if not l or any(b in l.lower() for b in basura) or "———" in l:
            continue
        
        if (l.startswith("-") or l.startswith("⁠-") or l.startswith("•")) and lineas_finales:
            det_limpio = l.replace("-", "").replace("•", "").strip()
            if " - " in lineas_finales[-1]:
                lineas_finales[-1] += f", {det_limpio}"
            else:
                lineas_finales[-1] += f" - {det_limpio}"
            continue

        nueva = l
        if "$" in l or "=" in l:
            nueva = re.sub(r'(\d{3,4})', lambda m: str(int(m.group(1)) + plus) if int(m.group(1)) > 150 else m.group(1), l)
        
        nueva = nueva.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "").strip()
        lineas_finales.append(nueva)
            
    return lineas_finales

def dibujar_compacto(lineas):
    if st.session_state.banner_pro:
        banner = st.session_state.banner_pro.copy()
        w_percent = (ancho_hoja / float(banner.size[0]))
        h_size = 220 
        banner = banner.resize((ancho_hoja, int(banner.size[1] * w_percent)), Image.Resampling.LANCZOS)
        banner = banner.crop((0, 0, ancho_hoja, h_size))
    else:
        h_size = 120
        banner = Image.new('RGB', (ancho_hoja, h_size), color="#000000")

    interlineado = 8 
    alto_total = h_size + (len(lineas) * (font_size_main + interlineado)) + 60
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="#FFFFFF")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size_main)
        font_info = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf", int(font_size_main*0.75))
    except:
        font_bold = font_info = ImageFont.load_default()

    y = h_size + 25
    for i, line in enumerate(lineas):
        # La primera línea (Fecha) va en un gris profesional o azul
        if i == 0:
            color = "#777777"
            fnt = font_info
            txt = line
        elif "INGRESO" in line or "TESTERS" in line or "IPHONE" in line.upper():
            color = "#004a99"
            fnt = font_bold
            txt = line.upper()
        elif "🔋" in line or "Grado" in line:
            color = "#555555"
            fnt = font_info
            txt = "   " + line
        else:
            color = "#000000"
            fnt = font_bold
            txt = line
            
        draw.text((30, y), txt, font=fnt, fill=color)
        y += (font_size_main if fnt == font_bold else int(font_size_main*0.75)) + interlineado
        
    return img

if st.button("🚀 GENERAR LISTA COMPACTA"):
    if input_text:
        lineas = procesar_lista_estilo_nuevo(input_text, comision)
        resultado = dibujar_compacto(lineas)
        buf = io.BytesIO()
        resultado.save(buf, format="PNG")
        st.divider()
        st.image(resultado, use_container_width=True)
        st.download_button("📥 Descargar Imagen", buf.getvalue(), "lista_compacta.png")
