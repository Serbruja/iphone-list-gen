import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Pro Final", layout="wide")

if 'banner_pro' not in st.session_state:
    st.session_state.banner_pro = None

# --- PANEL DE CONTROL ---
st.sidebar.header("🎨 Estética Final")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_hoja = st.sidebar.slider("Ancho de imagen", 700, 1000, 850)
font_size_main = st.sidebar.slider("Tamaño de letra", 40, 75, 55)

st.title("📲 Generador Pro: Diseño Compacto")

uploaded_file = st.file_uploader("1. Sube tu banner de celulares", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_pro = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista:", height=250)

def procesar_lista_compacta(texto, plus):
    lineas_finales = []
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "actualizada"]
    raw_lines = texto.split('\n')
    
    for i in range(len(raw_lines)):
        l = raw_lines[i].strip()
        if not l or any(b in l.lower() for b in basura) or "———" in l:
            continue
        
        # Unir colores a la línea del modelo
        if (l.startswith("-") or l.startswith("⁠-")) and lineas_finales:
            color_limpio = l.replace("-", "").strip()
            # Usamos un guion medio con espacios para separar
            if " - " in lineas_finales[-1]:
                lineas_finales[-1] += f", {color_limpio}"
            else:
                lineas_finales[-1] += f" - {color_limpio}"
            continue

        # Sumar comisión
        nueva = l
        if "$" in l or "=" in l:
            nueva = re.sub(r'(\d{3,4})', lambda m: str(int(m.group(1)) + plus) if int(m.group(1)) > 150 else m.group(1), l)
        
        nueva = nueva.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "").strip()
        lineas_finales.append(nueva)
            
    return lineas_finales

def dibujar(lineas):
    # Banner ajustado
    if st.session_state.banner_pro:
        banner = st.session_state.banner_pro.copy()
        w_percent = (ancho_hoja / float(banner.size[0]))
        h_size = 230 # Altura fija para el encabezado
        banner = banner.resize((ancho_hoja, int(banner.size[1] * w_percent)), Image.Resampling.LANCZOS)
        banner = banner.crop((0, 0, ancho_hoja, h_size))
    else:
        h_size = 120
        banner = Image.new('RGB', (ancho_hoja, h_size), color="#000000")

    # REDUCCIÓN DE ESPACIOS: Interlineado corto
    interlineado = 12 
    alto_total = h_size + (len(lineas) * (font_size_main + interlineado)) + 80
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="#FFFFFF")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        # Cargamos fuente Bold para todo el modelo
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size_main)
        font_info = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf", int(font_size_main*0.7))
    except:
        font_bold = font_info = ImageFont.load_default()

    y = h_size + 30
    for line in lineas:
        if "INGRESO" in line or "TESTERS" in line:
            color = "#0056b3"
            txt = line.upper()
            draw.text((40, y), txt, font=font_bold, fill=color)
            y += font_size_main + interlineado + 10 # Un pelín de aire solo en títulos
        elif "🔋" in line or "Grado" in line:
            color = "#666666"
            draw.text((45, y), line, font=font_info, fill=color)
            y += int(font_size_main*0.7) + interlineado
        else:
            # Modelo normal en NEGRITA
            color = "#000000"
            draw.text((40, y), line, font=font_bold, fill=color)
            y += font_size_main + interlineado
            
    return img

if st.button("🚀 GENERAR LISTA FINAL"):
    if input_text:
        lineas = procesar_lista_compacta(input_text, comision)
        resultado = dibujar(lineas)
        buf = io.BytesIO()
        resultado.save(buf, format="PNG")
        st.divider()
        st.image(resultado, use_container_width=True)
        st.download_button("📥 DESCARGAR LISTA", buf.getvalue(), "lista_premium.png")
