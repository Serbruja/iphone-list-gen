import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Lista Oficial WhatsApp", layout="wide")

# --- AJUSTES LATERALES ---
st.sidebar.header("📏 Ajustes Finales")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
font_size = st.sidebar.slider("Tamaño de letra", 30, 80, 55)
ancho_hoja = 850 

st.title("📲 Generador de Lista Oficial")

# 1. GESTIÓN DEL BANNER
uploaded_file = st.file_uploader("Sube tu banner aquí", type=["jpg", "png"])
if uploaded_file:
    st.session_state.img_banner = Image.open(uploaded_file)

# 2. ENTRADA DE TEXTO
input_text = st.text_area("Pega tu lista:", height=200)

def procesar_lista_final(texto, plus):
    lineas_finales = []
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas_finales.append(f"LISTA ACTUALIZADA ({fecha_hoy})")
    
    # Palabras para limpiar basura
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "actualizada", "———"]
    
    bloques = texto.split('\n')
    for l in bloques:
        limpia = l.strip()
        if not limpia or any(b in limpia.lower() for b in basura):
            continue
        
        # EL SECRETO: Si la línea es un detalle (- color o batería), se pega a la anterior
        if (limpia.startswith("-") or limpia.startswith("🔋") or "Grado" in limpia) and lineas_finales:
            detalle = limpia.replace("-", "").strip()
            # Unimos a la línea anterior con un guion
            lineas_finales[-1] += f" - {detalle}"
            continue

        # Procesar precio y limpiar símbolos
        if "$" in limpia or "=" in limpia:
            limpia = re.sub(r'(\d{3,4})', lambda m: str(int(m.group(1)) + plus) if int(m.group(1)) > 150 else m.group(1), limpia)
        
        limpia = limpia.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "").replace("◼️", "").strip()
        lineas_finales.append(limpia)
        
    return lineas_finales

if st.button("🚀 GENERAR IMAGEN FINAL"):
    if input_text:
        datos = procesar_lista_final(input_text, comision)
        
        # Altura del Banner
        if 'img_banner' in st.session_state:
            w_perc = (ancho_hoja / float(st.session_state.img_banner.size[0]))
            h_banner = int((float(st.session_state.img_banner.size[1]) * float(w_perc)))
            banner_res = st.session_state.img_banner.resize((ancho_hoja, h_banner), Image.Resampling.LANCZOS)
        else:
            h_banner = 10
            banner_res = Image.new('RGB', (ancho_hoja, h_banner), color="white")

        # ESPACIADO TOTALMENTE APRETADO
        interlineado = 1 
        alto_total = h_banner + (len(datos) * (font_size + interlineado)) + 60
        
        img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="white")
        img.paste(banner_res, (0, 0))
        
        draw = ImageDraw.Draw(img)
        try:
            # Forzamos Negrita estilo Arial/Calibri
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        y = h_banner + 20
        for i, linea in enumerate(datos):
            # Color: Azul para fecha y títulos, Negro para modelos
            es_titulo = any(x in linea.upper() for x in ["ACTUALIZADA", "IPHONE", "SAMSUNG", "INGRESO", "TESTERS"])
            color = "#004a99" if es_titulo else "black"
            
            draw.text((40, y), linea, font=font, fill=color)
            y += font_size + interlineado

        # Resultado
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(img)
        st.download_button("📥 DESCARGAR AHORA", buf.getvalue(), "lista_perfecta.png")
