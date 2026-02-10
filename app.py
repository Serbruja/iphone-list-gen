import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Lista Pro WhatsApp", layout="wide")

# --- AJUSTES ---
st.sidebar.header("📏 Ajustes")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
font_size = st.sidebar.slider("Tamaño de letra", 30, 80, 50)
ancho_hoja = 600 # Ancho ideal para estados de WhatsApp

st.title("📲 Generador de Lista Oficial")

uploaded_file = st.file_uploader("Sube tu banner", type=["jpg", "png"])
if uploaded_file:
    st.session_state.img_banner = Image.open(uploaded_file)

input_text = st.text_area("Pega tu lista aquí:", height=200)

def procesar_texto_inteligente(texto, plus):
    lineas_finales = []
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas_finales.append(f"LISTA ACTUALIZADA ({fecha_hoy})")
    
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "actualizada", "———"]
    
    lineas_raw = texto.split('\n')
    for l in lineas_raw:
        limpia = l.strip()
        if not limpia or any(b in limpia.lower() for b in basura):
            continue
        
        # Lógica de unión: Solo une si empieza con guion solo o puntos, NO si es un rango 85-100
        es_detalle = (limpia.startswith("-") or limpia.startswith("•") or "Grado" in limpia or "🔋" in limpia)
        
        if es_detalle and lineas_finales:
            # Quitamos el guion inicial pero mantenemos los internos (como en 85-100)
            det = re.sub(r'^[-•]\s*', '', limpia)
            lineas_finales[-1] += f" - {det}"
            continue

        # Sumar comisión
        if "$" in limpia or "=" in limpia:
            limpia = re.sub(r'(\d{3,4})', lambda m: str(int(m.group(1)) + plus) if int(m.group(1)) > 150 else m.group(1), limpia)
        
        # Limpieza de iconos
        limpia = limpia.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "").replace("◼️", "").strip()
        lineas_finales.append(limpia)
        
    return lineas_finales

if st.button("🚀 GENERAR IMAGEN"):
    if input_text:
        datos = procesar_texto_inteligente(input_text, comision)
        
        # Procesar Banner para que ocupe todo el ancho
        if 'img_banner' in st.session_state:
            w_perc = (ancho_hoja / float(st.session_state.img_banner.size[0]))
            h_banner = int((float(st.session_state.img_banner.size[1]) * float(w_perc)))
            banner_res = st.session_state.img_banner.resize((ancho_hoja, h_banner), Image.Resampling.LANCZOS)
        else:
            h_banner = 10
            banner_res = Image.new('RGB', (ancho_hoja, h_banner), color="white")

        # ESPACIADO CERO
        alto_total = h_banner + (len(datos) * (font_size + 8)) + 40
        img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="white")
        img.paste(banner_res, (0, 0))
        
        draw = ImageDraw.Draw(img)
        try:
            # Fuente Negrita
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        y = h_banner + 15
        for i, linea in enumerate(datos):
            # Títulos en Azul, resto en Negro
            es_azul = i == 0 or any(x in linea.upper() for x in ["IPHONE", "SAMSUNG", "TESTERS", "INGRESO"])
            color = "#004a99" if es_azul else "black"
            
            draw.text((20, y), linea, font=font, fill=color)
            y += font_size + 6 # El mínimo para que no se encimen las letras

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(img)
        st.download_button("📥 DESCARGAR LISTA", buf.getvalue(), "lista_final.png")
