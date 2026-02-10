import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Compacto Pro", layout="wide")

if 'banner_pro' not in st.session_state:
    st.session_state.banner_pro = None

# --- AJUSTES LATERALES ---
st.sidebar.header("🎨 Ajustes de Diseño")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_hoja = st.sidebar.slider("Ancho de imagen", 600, 950, 850)
font_size_main = st.sidebar.slider("Tamaño de letra", 30, 60, 45)

st.title("📲 Generador de Lista Compacta")

uploaded_file = st.file_uploader("1. Sube el banner de los celulares", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_pro = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista aquí:", height=250)

def procesar_lista_compacta(texto, plus):
    lineas_finales = []
    # Palabras para limpiar datos innecesarios
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "actualizada"]
    
    raw_lines = texto.split('\n')
    
    for i in range(len(raw_lines)):
        l = raw_lines[i].strip()
        if not l or any(b in l.lower() for b in basura) or "———" in l:
            continue
        
        # 1. Si es un COLOR (empieza con -), lo pegamos a la línea anterior
        if (l.startswith("-") or l.startswith("⁠-")) and lineas_finales:
            color_limpio = l.replace("-", "").strip()
            # Si el modelo anterior ya tiene colores, sumamos con coma, si no, con guion
            if " - " in lineas_finales[-1]:
                lineas_finales[-1] += f", {color_limpio}"
            else:
                lineas_finales[-1] += f" - {color_limpio}"
            continue

        # 2. SUMAR COMISIÓN A LOS MODELOS
        nueva = l
        if "$" in l or "=" in l:
            # Suma la comisión a números de 3 o 4 cifras (evita porcentajes de batería)
            nueva = re.sub(r'(\d{3,4})', lambda m: str(int(m.group(1)) + plus) if int(m.group(1)) > 150 else m.group(1), l)
        
        # Limpieza estética
        nueva = nueva.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "").strip()
        lineas_finales.append(nueva)
            
    return lineas_finales

def dibujar(lineas):
    # Banner con altura fija (estilo franja)
    if st.session_state.banner_pro:
        banner = st.session_state.banner_pro.copy()
        w_percent = (ancho_hoja / float(banner.size[0]))
        h_size = int(220) # Altura fija para que no sea gigante
        banner = banner.resize((ancho_hoja, int(banner.size[1] * w_percent)), Image.Resampling.LANCZOS)
        banner = banner.crop((0, 0, ancho_hoja, h_size))
    else:
        h_size = 120
        banner = Image.new('RGB', (ancho_hoja, h_size), color="#000000")

    interlineado = 22
    alto_total = h_size + (len(lineas) * (font_size_main + interlineado)) + 100
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="#FFFFFF")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size_main)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", int(font_size_main*0.75))
    except:
        font_bold = font_small = ImageFont.load_default()

    y = h_size + 40
    for line in lineas:
        # Colores por tipo de línea
        if "◼️" in line or "INGRESO" in line or "TESTERS" in line:
            color = "#004a99" # Azul Títulos
            fnt = font_bold
            txt = line.replace("◼️", "").upper()
        elif "🔋" in line or "Grado" in line:
            color = "#555555" # Gris para batería/grado
            fnt = font_small
            txt = "   " + line
        else:
            color = "#000000" # Negro para Modelos + Colores
            fnt = font_bold
            txt = line
            
        draw.text((40, y), txt, font=fnt, fill=color)
        y += (font_size_main if fnt == font_bold else int(font_size_main*0.75)) + interlineado
        
    return img

if st.button("🚀 GENERAR LISTA COMPACTA"):
    if input_text:
        lineas = procesar_lista_compacta(input_text, comision)
        resultado = dibujar(lineas)
        buf = io.BytesIO()
        resultado.save(buf, format="PNG")
        st.image(resultado, use_container_width=True)
        st.download_button("📥 Descargar Imagen", buf.getvalue(), "lista_compacta.png")
