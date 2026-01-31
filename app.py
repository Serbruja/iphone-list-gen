import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz 

st.set_page_config(page_title="Generador Premium Final", layout="wide")

# --- MEMORIA DE SESIÓN ---
if 'lista_imagenes' not in st.session_state:
    st.session_state.lista_imagenes = []

# --- BARRA LATERAL ---
st.sidebar.header("🎨 Ajustes de Imagen")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_fijo = 1200 # Ancho estándar para evitar desconfiguraciones
font_size_global = st.sidebar.slider("Tamaño de letra", 30, 50, 40)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 60, 30)

st.title("📱 Generador Pro: Diseño Corregido")
input_text = st.text_area("Pega tus listas aquí:", height=250)

def procesar_texto(texto, incremento):
    prohibidas = ["⏰", "📍", "CABA", "CONDICIONES", "BILLETES", "DOLARES", "CARA CHICA", 
                  "NO SE ACEPTAN", "CARGADOR", "ENCOMIENDAS", "CONSULTAR", "MARTES", 
                  "LUNES A VIERNES", "USD/PESOS/USDT", "MAL ESTADO", "NOKIA"]
    lineas_limpias = []
    for linea in texto.split('\n'):
        if not linea.strip() or any(p in linea.upper() for p in prohibidas): continue
        # Sumar comisión
        l = re.sub(r'([=–\-:\$]\s*\$?\s*)(\d{2,4})', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        if l == linea: l = re.sub(r'(\s)(\d{2,4})$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        lineas_limpias.append(l.strip())
    return lineas_limpias

def dibujar_imagen(lineas, titulo_pag, es_primera):
    # Zona Horaria
    try: zona = pytz.timezone('America/Argentina/Buenos_Aires'); fecha = datetime.now(zona).strftime("%d/%m/%Y")
    except: fecha = datetime.now().strftime("%d/%m/%Y")
    
    # --- CÁLCULO DE ESPACIOS ---
    h_header = 250
    h_linea = font_size_global + 25
    alto_total = h_header + (len(lineas) * h_linea) + 100
    
    img = Image.new('RGB', (ancho_fijo, int(alto_total)), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    # --- FUENTES ---
    try:
        f_bold = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size_global)
        f_logo = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 45)
    except:
        f_bold = ImageFont.load_default(); f_logo = ImageFont.load_default()

    # --- ENCABEZADO NEGRO ---
    draw.rectangle([0, 0, ancho_fijo, h_header], fill="#000000")
    
    # Dibujo de Logos (Posiciones fijas para que no se muevan)
    # Apple
    draw.ellipse([50, 40, 100, 90], fill="#FFFFFF")
    draw.text((110, 45), "APPLE", font=f_logo, fill="#FFFFFF")
    # Samsung
    draw.rectangle([320, 40, 380, 90], fill="#1428a0")
    draw.text((390, 45), "SAMSUNG", font=f_logo, fill="#FFFFFF")
    # Motorola
    draw.ellipse([650, 40, 700, 90], outline="#00d5ff", width=5)
    draw.text((710, 45), "MOTOROLA", font=f_logo, fill="#FFFFFF")
    # Xiaomi
    draw.rectangle([1000, 40, 1050, 90], fill="#ff6700")
    draw.text((1060, 45), "XIAOMI", font=f_logo, fill="#FFFFFF")

    # Subtítulo (Fecha o Continuación)
    sub = f"📅 ACTUALIZADO: {fecha} | {titulo_pag}" if es_primera else f"🚀 CATÁLOGO DE PRODUCTOS | {titulo_pag}"
    draw.text((50, 140), sub, font=f_bold, fill="#AAAAAA")
    draw.line([(50, 200), (ancho_fijo-50, 200)], fill="#333333", width=3)

    # --- LISTADO ---
    y = h_header + 40
    for line in lineas:
        color = "#0056b3" if "*" in line else "#000000"
        draw.text((60, y), line.replace("*", "").replace("-", "•"), font=f_bold, fill=color)
        y += h_linea
    return img

# --- INTERFAZ ---
c1, c2 = st.columns(2)
with c1:
    if st.button("🚀 GENERAR"):
        if input_text:
            lineas = procesar_texto(input_text, comision)
            pags = [lineas[i:i + lineas_por_pag] for i in range(0, len(lineas), lineas_por_pag)]
            st.session_state.lista_imagenes = []
            for i, p in enumerate(pags):
                img = dibujar_imagen(p, f"PARTE {i+1}", i==0)
                b = io.BytesIO(); img.save(b, format="PNG")
                st.session_state.lista_imagenes.append({"t": f"PARTE {i+1}", "b": b.getvalue(), "p": img})
        else: st.error("Pega la lista.")

with c2:
    if st.button("🗑️ NUEVA"):
        st.session_state.lista_imagenes = []
        st.rerun()

if st.session_state.lista_imagenes:
    for i, item in enumerate(st.session_state.lista_imagenes):
        st.divider()
        st.image(item['p'], use_container_width=True)
        st.download_button(f"📥 Descargar {item['t']}", item['b'], f"lista_p{i+1}.png", "image/png", key=f"d{i}")
