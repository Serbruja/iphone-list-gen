import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz 

st.set_page_config(page_title="Generador Premium", layout="wide")

# --- AJUSTES DE DISEÑO FIJOS (Los que funcionaban) ---
ANCHO_IMG = 1400
FONT_SIZE_LISTA = 40
FONT_SIZE_LOGOS = 50

# --- BARRA LATERAL ---
st.sidebar.header("🎨 Ajustes")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 50, 30)

st.title("📱 Generador de Listas Premium")
input_text = st.text_area("Pega tus listas aquí:", height=250)

def procesar_texto(texto, incremento):
    # Filtros que pediste
    prohibidas = ["NOKIA", "LUNES A VIERNES", "USD/PESOS/USDT", "BILLETES", "CARGADOR", "CABA", "MAL ESTADO"]
    lineas_limpias = []
    for linea in texto.split('\n'):
        if not linea.strip() or any(p in linea.upper() for p in prohibidas):
            continue
        # Sumar comisión
        l = re.sub(r'([=–\-:\$]\s*\$?\s*)(\d{2,4})', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        if l == linea:
            l = re.sub(r'(\s)(\d{2,4})$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        lineas_limpias.append(l.strip())
    return lineas_limpias

def dibujar_imagen(lineas, titulo_pag, es_primera):
    # Fecha Argentina
    try:
        zona = pytz.timezone('America/Argentina/Buenos_Aires')
        fecha = datetime.now(zona).strftime("%d/%m/%Y")
    except:
        fecha = datetime.now().strftime("%d/%m/%Y")
    
    # Espaciado dinámico
    margen_top = 250
    alto_total = margen_top + (len(lineas) * (FONT_SIZE_LISTA + 25)) + 80
    
    img = Image.new('RGB', (ANCHO_IMG, int(alto_total)), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    # Cargar fuentes (Sistema Linux de Streamlit)
    try:
        f_bold = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", FONT_SIZE_LISTA)
        f_logos = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", FONT_SIZE_LOGOS)
    except:
        f_bold = ImageFont.load_default()
        f_logos = ImageFont.load_default()

    # ENCABEZADO NEGRO (Diseño que te gustaba)
    draw.rectangle([0, 0, ANCHO_IMG, 200], fill="#000000")
    
    # Logos dibujados para que no fallen
    # Apple
    draw.ellipse([60, 50, 110, 100], fill="#FFFFFF")
    draw.text((125, 50), "APPLE", font=f_logos, fill="#FFFFFF")
    # Samsung
    draw.rectangle([400, 50, 460, 100], fill="#1428a0")
    draw.text((475, 50), "SAMSUNG", font=f_logos, fill="#FFFFFF")
    # Motorola
    draw.ellipse([820, 50, 870, 100], outline="#00d5ff", width=6)
    draw.text((885, 50), "MOTOROLA", font=f_logos, fill="#FFFFFF")
    # Xiaomi
    draw.rectangle([1180, 50, 1230, 100], fill="#ff6700")
    draw.text((1245, 50), "XIAOMI", font=f_logos, fill="#FFFFFF")

    # Texto de fecha/actualización (Solo 1era hoja)
    if es_primera:
        info = f"📅 ACTUALIZADO: {fecha} | {titulo_pag}"
    else:
        info = f"🚀 CATÁLOGO DE PRODUCTOS | {titulo_pag}"
    draw.text((65, 135), info, font=f_bold, fill="#AAAAAA")

    # LISTADO
    y = margen_top
    for line in lineas:
        color = "#0056b3" if "*" in line else "#000000"
        txt = line.replace("*", "").replace("-", "•")
        draw.text((70, y), txt, font=f_bold, fill=color)
        y += FONT_SIZE_LISTA + 25
        
    return img

# --- GENERACIÓN ---
if st.button("🚀 GENERAR LISTA"):
    if input_text:
        lineas = procesar_texto(input_text, comision)
        pags = [lineas[i:i + lineas_por_pag] for i in range(0, len(lineas), lineas_por_pag)]
        
        for i, p in enumerate(pags):
            img = dibujar_imagen(p, f"PARTE {i+1}", i==0)
            st.image(img)
            
            # Descarga
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button(f"📥 Descargar PARTE {i+1}", buf.getvalue(), f"lista_p{i+1}.png", "image/png", key=f"d{i}")
