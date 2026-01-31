import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz 

st.set_page_config(page_title="Generador Premium Final", layout="wide")

if 'lista_imagenes' not in st.session_state:
    st.session_state.lista_imagenes = []

# --- CONFIGURACIÓN DE VISIBILIDAD ---
ANCHO_LIENZO = 1200 
TAMANO_FUENTE_MARCAS = 65  # Mucho más grande
TAMANO_FUENTE_LISTA = 48   # Mucho más grande

# --- BARRA LATERAL ---
st.sidebar.header("🎨 Ajustes de Imagen")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 60, 25)

st.title("📱 Generador Pro: Alta Visibilidad")
input_text = st.text_area("Pega tus listas aquí:", height=250)

def procesar_texto(texto, incremento):
    prohibidas = ["⏰", "📍", "CABA", "CONDICIONES", "BILLETES", "DOLARES", "CARA CHICA", 
                  "NO SE ACEPTAN", "CARGADOR", "ENCOMIENDAS", "CONSULTAR", "MARTES", 
                  "LUNES A VIERNES", "USD/PESOS/USDT", "MAL ESTADO", "NOKIA"]
    lineas_limpias = []
    for linea in texto.split('\n'):
        if not linea.strip() or any(p in linea.upper() for p in prohibidas): continue
        l = re.sub(r'([=–\-:\$]\s*\$?\s*)(\d{2,4})', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        if l == linea: l = re.sub(r'(\s)(\d{2,4})$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        lineas_limpias.append(l.strip())
    return lineas_limpias

def dibujar_imagen(lineas, titulo_pag, es_primera):
    zona = pytz.timezone('America/Argentina/Buenos_Aires')
    fecha = datetime.now(zona).strftime("%d/%m/%Y")
    
    h_header = 320 # Más espacio para logos grandes
    h_linea = TAMANO_FUENTE_LISTA + 35
    alto_total = h_header + (len(lineas) * h_linea) + 100
    
    img = Image.new('RGB', (ANCHO_LIENZO, int(alto_total)), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        f_lista = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", TAMANO_FUENTE_LISTA)
        f_logo_txt = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", TAMANO_FUENTE_MARCAS)
        f_fecha = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 45)
    except:
        f_lista = ImageFont.load_default(); f_logo_txt = ImageFont.load_default(); f_fecha = ImageFont.load_default()

    # --- ENCABEZADO NEGRO ---
    draw.rectangle([0, 0, ANCHO_LIENZO, h_header], fill="#000000")
    
    # Logos e íconos más grandes
    y_logo = 60
    radio = 35 # Radio de los círculos/cuadrados
    
    # Apple
    draw.ellipse([50-radio, y_logo-radio+40, 50+radio, y_logo+radio+40], fill="#FFFFFF")
    draw.text((100, y_logo+10), "APPLE", font=f_logo_txt, fill="#FFFFFF")
    # Samsung
    draw.rectangle([340-radio, y_logo-radio+40, 340+radio, y_logo+radio+40], fill="#1428a0")
    draw.text((390, y_logo+10), "SAMSUNG", font=f_logo_txt, fill="#FFFFFF")
    # Motorola
    draw.ellipse([680-radio, y_logo-radio+40, 680+radio, y_logo+radio+40], outline="#00d5ff", width=8)
    draw.text((730, y_logo+10), "MOTOROLA", font=f_logo_txt, fill="#FFFFFF")
    # Xiaomi
    draw.rectangle([1020-radio, y_logo-radio+40, 1020+radio, y_logo+radio+40], fill="#ff6700")
    draw.text((1070, y_logo+10), "XIAOMI", font=f_logo_txt, fill="#FFFFFF")

    # Subtítulo (Fecha o Continuación)
    sub = f"📅 ACTUALIZADO: {fecha} | {titulo_pag}" if es_primera else f"🚀 CATÁLOGO DE PRODUCTOS | {titulo_pag}"
    draw.text((50, 210), sub, font=f_fecha, fill="#AAAAAA")
    draw.line([(50, 280), (ANCHO_LIENZO-50, 280)], fill="#333333", width=4)

    # --- LISTADO ---
    y = h_header + 50
    for line in lineas:
        color = "#0056b3" if "*" in line else "#000000"
        # Usamos un punto grande para los productos
        txt = line.replace("*", "").replace("-", "•")
        draw.text((60, y), txt, font=f_lista, fill=color)
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
