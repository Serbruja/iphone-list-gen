import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Generador de Lista", layout="wide")

# --- AJUSTES ---
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_final = 800 # Un ancho estándar para que no se estire
font_size = st.sidebar.slider("Tamaño de letra", 30, 70, 45)

st.title("📲 Generador de Lista para WhatsApp")

# 1. CARGA DE BANNER
uploaded_file = st.file_uploader("Sube tu banner (se verá completo)", type=["jpg", "png"])
if uploaded_file:
    st.session_state.img_banner = Image.open(uploaded_file)

# 2. ENTRADA DE TEXTO
input_text = st.text_area("Pega tu lista aquí:", height=200)

def procesar_texto(texto, plus):
    lineas = []
    # Fecha arriba de todo
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas.append(f"LISTA ACTUALIZADA ({fecha_hoy})")
    lineas.append("") # Un solo espacio de aire tras la fecha
    
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "actualizada", "———"]
    
    for l in texto.split('\n'):
        limpia = l.strip()
        if not limpia or any(b in limpia.lower() for b in basura):
            continue
        
        # Sumar comisión
        if "$" in limpia or "=" in limpia:
            limpia = re.sub(r'(\d{3,4})', lambda m: str(int(m.group(1)) + plus) if int(m.group(1)) > 150 else m.group(1), limpia)
        
        # Limpiar emojis y asteriscos
        limpia = limpia.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "").replace("◼️", "").strip()
        lineas.append(limpia)
    return lineas

if st.button("🚀 GENERAR IMAGEN"):
    if input_text:
        lineas = procesar_texto(input_text, comision)
        
        # Preparar Banner
        if 'img_banner' in st.session_state:
            base_w = ancho_final
            w_perc = (base_w / float(st.session_state.img_banner.size[0]))
            h_size = int((float(st.session_state.img_banner.size[1]) * float(w_perc)))
            banner = st.session_state.img_banner.resize((base_w, h_size), Image.Resampling.LANCZOS)
        else:
            h_size = 50
            banner = Image.new('RGB', (ancho_final, h_size), color="white")

        # CALCULO DE ALTURA (Sin espacios extra)
        # Altura = Banner + (Cantidad de lineas * Tamaño de letra)
        alto_total = h_size + (len(lineas) * (font_size + 10)) + 50
        img = Image.new('RGB', (ancho_final, int(alto_total)), color="white")
        img.paste(banner, (0, 0))
        
        draw = ImageDraw.Draw(img)
        try:
            # Fuente estándar similar a Calibri/Arial
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        y = h_size + 20
        for i, line in enumerate(lineas):
            # Color: Azul para fecha y secciones, Negro para modelos
            color = "#004a99" if (i == 0 or "IPHONE" in line.upper() or "SAMSUNG" in line.upper() or "INGRESO" in line.upper()) else "black"
            
            draw.text((40, y), line, font=font, fill=color)
            y += font_size + 5 # Espaciado mínimo entre renglones

        # Mostrar y Descargar
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(img)
        st.download_button("📥 Descargar para WhatsApp", buf.getvalue(), "lista_final.png")
