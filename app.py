import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz 

st.set_page_config(page_title="Generador Premium Final", page_icon="📲", layout="wide")

if 'lista_imagenes' not in st.session_state:
    st.session_state.lista_imagenes = []

# --- BARRA LATERAL ---
st.sidebar.header("🎨 Ajustes de Imagen")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_img = st.sidebar.slider("Ancho de imagen", 1200, 1600, 1500)
font_size = st.sidebar.slider("Tamaño de letra", 25, 45, 34)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 60, 35)

input_text = st.text_area("Pega tus listas aquí:", height=250)

def procesar_texto(texto, incremento):
    palabras_prohibidas = [
        "⏰", "📍", "CABA", "Condiciones", "billetes", "dolares", "CARA CHICA",
        "No se aceptan", "CARGADOR", "cargador", "encomiendas", "Consultar",
        "MARTES", "LISTA ACTUALIZADA", "ACTUALIZO", "¡Nuevos ingresos",
        "Lunes a viernes", "USD/PESOS/USDT", "solo para completar", "mal estado", "NOKIA"
    ]
    lineas_limpias = []
    for linea in texto.split('\n'):
        upper_l = linea.upper()
        if any(p.upper() in upper_l for p in palabras_prohibidas): continue
        l = linea.strip()
        if not l or len(l) < 2: continue
        lineas_limpias.append(l)

    resultado = []
    for linea in lineas_limpias:
        nueva_linea = re.sub(r'([=–\-:\$]\s*\$?\s*)(\d{2,4})', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        if nueva_linea == linea:
            nueva_linea = re.sub(r'(\s)(\d{2,4})$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        resultado.append(nueva_linea)
    return resultado

def dibujar_imagen(lineas, titulo_pag, es_primera):
    try:
        zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
        fecha_hoy = datetime.now(zona_horaria).strftime("%d/%m/%Y")
    except:
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    margen_top = 280
    espacio_linea = 22
    alto = margen_top + (len(lineas) * (font_size + espacio_linea)) + 120
    
    img = Image.new('RGB', (ancho_img, int(alto)), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        font_logo = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 42)
        font_m = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 30)
    except:
        font = ImageFont.load_default()
        font_logo = ImageFont.load_default()
        font_m = ImageFont.load_default()

    # --- ENCABEZADO NEGRO ---
    draw.rectangle([0, 0, ancho_img, 230], fill="#000000")

    # DIBUJO MANUAL DE LOGOS (Para que salgan sí o sí)
    # 1. APPLE
    draw.ellipse([60, 45, 110, 95], fill="#FFFFFF") # Círculo blanco
    draw.text((120, 50), "APPLE", font=font_logo, fill="#FFFFFF")

    # 2. SAMSUNG
    draw.rectangle([400, 45, 460, 95], fill="#1428a0") # Rectángulo azul
    draw.text((475, 50), "SAMSUNG", font=font_logo, fill="#FFFFFF")

    # 3. MOTOROLA
    draw.ellipse([830, 45, 880, 95], outline="#00d5ff", width=5) # Círculo turquesa
    draw.text((843, 55), "M", font=font_m, fill="#00d5ff")
    draw.text((895, 50), "MOTOROLA", font=font_logo, fill="#FFFFFF")

    # 4. XIAOMI
    draw.rectangle([1230, 45, 1280, 95], fill="#ff6700") # Cuadrado naranja
    draw.text((1295, 50), "XIAOMI", font=font_logo, fill="#FFFFFF")

    # Info de fecha
    info_header = f"📅 ACTUALIZADO: {fecha_hoy} | {titulo_pag}" if es_primera else f"🚀 CATÁLOGO DE PRODUCTOS | {titulo_pag}"
    draw.text((60, 150), info_header, font=font, fill="#AAAAAA")
    draw.line([(60, 210), (ancho_img-60, 210)], fill="#333333", width=2)

    # --- LISTADO ---
    y = margen_top
    for line in lineas:
        color_txt = "#000000"
        if "*" in line:
            color_txt = "#0056b3"
            draw.text((60, y), line.replace("*", ""), font=font, fill=color_txt)
        else:
            draw.text((80, y), line.replace("-", "•"), font=font, fill=color_txt)
        y += font_size + espacio_linea
    return img

# --- LÓGICA DE INTERFAZ ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 GENERAR LISTA FINAL"):
        if input_text:
            lineas_finales = procesar_texto(input_text, comision)
            paginas = [lineas_finales[i:i + lineas_por_pag] for i in range(0, len(lineas_finales), lineas_por_pag)]
            st.session_state.lista_imagenes = []
            for idx, pag in enumerate(paginas):
                img_res = dibujar_imagen(pag, f"PARTE {idx+1}", es_primera=(idx==0))
                buf = io.BytesIO()
                img_res.save(buf, format="PNG")
                st.session_state.lista_imagenes.append({"t": f"PARTE {idx+1}", "b": buf.getvalue(), "p": img_res})
        else:
            st.error("Pega la lista.")

with col2:
    if st.button("🗑️ NUEVA LISTA"):
        st.session_state.lista_imagenes = []
        st.rerun()

if st.session_state.lista_imagenes:
    for idx, item in enumerate(st.session_state.lista_imagenes):
        st.divider()
        st.image(item['p'], use_container_width=True)
        st.download_button(f"📥 Descargar {item['t']}", item['b'], f"lista_p{idx+1}.png", "image/png", key=f"d{idx}")
