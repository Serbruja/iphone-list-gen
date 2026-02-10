import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Generador Letra Gigante", layout="wide")

# --- PANEL LATERAL ---
st.sidebar.header("📏 Ajuste de Tamaño")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
# Reducimos el ancho para que la letra parezca más grande al estirarse en el celu
ancho_hoja = 600 
font_size_main = st.sidebar.slider("Tamaño de letra", 50, 90, 70)

st.title("📲 Generador de Estados (Visibilidad Máxima)")

uploaded_file = st.file_uploader("1. Sube tu banner", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_pro = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista:", height=200)

def procesar_lista_compacta(texto, plus):
    lineas_finales = []
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "actualizada", "———"]
    
    raw_lines = texto.split('\n')
    for i in range(len(raw_lines)):
        l = raw_lines[i].strip()
        if not l or any(b in l.lower() for b in basura):
            continue
        
        # Unir colores y grados a la línea del modelo para ahorrar espacio
        if (l.startswith("-") or l.startswith("⁠-") or "Grado" in l or "🔋" in l) and lineas_finales:
            limpio = l.replace("-", "").replace("🔋", "").strip()
            # Si es grado o batería, lo ponemos entre paréntesis al final
            lineas_finales[-1] += f" ({limpio})"
            continue

        nueva = l
        if "$" in l or "=" in l:
            nueva = re.sub(r'(\d{3,4})', lambda m: str(int(m.group(1)) + plus) if int(m.group(1)) > 150 else m.group(1), l)
        
        nueva = nueva.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "").strip()
        lineas_finales.append(nueva)
            
    return lineas_finales

def dibujar_gigante(lineas):
    # Banner súper finito (solo como detalle arriba)
    h_banner = 120 
    if 'banner_pro' in st.session_state and st.session_state.banner_pro:
        banner = st.session_state.banner_pro.copy()
        w_percent = (ancho_hoja / float(banner.size[0]))
        banner = banner.resize((ancho_hoja, int(banner.size[1] * w_percent)), Image.Resampling.LANCZOS)
        banner = banner.crop((0, 0, ancho_hoja, h_banner))
    else:
        banner = Image.new('RGB', (ancho_hoja, h_banner), color="#111111")

    # INTERLINEADO CASI CERO
    interlineado = 4 
    alto_total = h_banner + (len(lineas) * (font_size_main + interlineado)) + 40
    
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="#000000")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        # Usamos Bold para TODO
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size_main)
        font_fecha = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 30)
    except:
        font = font_fecha = ImageFont.load_default()

    # Fecha en una esquina del banner para no ocupar espacio
    fecha_hoy = datetime.now().strftime("%d/%m")
    draw.text((ancho_hoja - 120, 10), f"MOD: {fecha_hoy}", font=font_fecha, fill="#FFD700")

    y = h_banner + 15
    for line in lineas:
        if "INGRESO" in line or "TESTERS" in line or "IPHONE" in line.upper():
            color = "#00D4FF" # Celeste
        else:
            color = "#FFFFFF" # Blanco
            
        draw.text((15, y), line, font=font, fill=color)
        y += font_size_main + interlineado
        
    return img

if st.button("🚀 GENERAR LISTA GIGANTE"):
    if input_text:
        lineas = procesar_lista_compacta(input_text, comision)
        resultado = dibujar_gigante(lineas)
        buf = io.BytesIO()
        resultado.save(buf, format="PNG")
        st.divider()
        st.image(resultado)
        st.download_button("📥 DESCARGAR PARA WHATSAPP", buf.getvalue(), "lista_gigante.png")
