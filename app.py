import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz 

st.set_page_config(page_title="Generador Premium Final", page_icon="📲", layout="wide")

# --- MEMORIA DE SESIÓN ---
if 'lista_imagenes' not in st.session_state:
    st.session_state.lista_imagenes = []

# --- BARRA LATERAL (Tus ajustes originales) ---
st.sidebar.header("🎨 Ajustes de Imagen")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_img = st.sidebar.slider("Ancho de imagen", 1200, 1600, 1500)
font_size = st.sidebar.slider("Tamaño de letra", 25, 45, 34)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 60, 35)

st.title("📲 Generador de Listas Premium")
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
        
        # --- NUEVA LÓGICA DE PRECIO SEGURA ---
        # Solo suma si hay un "$" o si el número de 3 cifras está al final de la línea.
        # Esto ignora los (85-100%) porque terminan en "%" o ")".
        
        # 1. Buscar precio con "$" explícito
        nueva_linea = re.sub(r'(\$\s*)(\d{2,4})', 
                             lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        
        # 2. Si no cambió, buscar número al final de la línea (Ej: = 680)
        if nueva_linea == l:
            nueva_linea = re.sub(r'([=–\-:\s]\s*)(\d{3,4})$', 
                                 lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", l)
        
        lineas_limpias.append(nueva_linea)
    return lineas_limpias

def dibujar_imagen(lineas, titulo_pag, es_primera):
    try:
        zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
        fecha_hoy = datetime.now(zona_horaria).strftime("%d/%m/%Y")
    except:
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    # --- PROPORCIONES RESTAURADAS ---
    margen_top = 240
    espacio_linea = 22
    alto = margen_top + (len(lineas) * (font_size + espacio_linea)) + 120
    
    img = Image.new('RGB', (ancho_img, int(alto)), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        font_logo = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()
        font_logo = ImageFont.load_default()

    # --- DISEÑO DE ENCABEZADO ORIGINAL ---
    draw.rectangle([0, 0, ancho_img, 200], fill="#000000")
    
    # Emojis y Marcas (Volvemos a tu formato de texto directo que funcionaba)
    marcas = [("🍎 APPLE", 60), ("🔵 SAMSUNG", 400), ("📱 MOTOROLA", 800), ("🟠 XIAOMI", 1200)]
    for texto_m, x_m in marcas:
        draw.text((x_m, 50), texto_m, font=font_logo, fill="#FFFFFF")

    info_header = f"📅 ACTUALIZADO: {fecha_hoy} | {titulo_pag}" if es_primera else f"🚀 CONTINUACIÓN | {titulo_pag}"
    draw.text((60, 130), info_header, font=font, fill="#AAAAAA")

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

# --- INTERFAZ (Tu lógica de persistencia) ---
col_b1, col_b2 = st.columns(2)
with col_b1:
    if st.button("🚀 GENERAR LISTA"):
        if input_text:
            lineas_finales = procesar_texto(input_text, comision)
            paginas = [lineas_finales[i:i + lineas_por_pag] for i in range(0, len(lineas_finales), lineas_por_pag)]
            
            st.session_state.lista_imagenes = [] 
            for idx, pag in enumerate(paginas):
                txt_pag = f"PARTE {idx+1}"
                img_res = dibujar_imagen(pag, txt_pag, es_primera=(idx==0))
                buf = io.BytesIO()
                img_res.save(buf, format="PNG")
                st.session_state.lista_imagenes.append({
                    "titulo": txt_pag, "bytes": buf.getvalue(), "pil": img_res
                })
        else:
            st.error("Pega la lista primero.")

with col_b2:
    if st.button("🗑️ NUEVA"):
        st.session_state.lista_imagenes = []
        st.rerun()

if st.session_state.lista_imagenes:
    for idx, item in enumerate(st.session_state.lista_imagenes):
        st.divider()
        st.image(item['pil'], use_container_width=True)
        st.download_button(
            label=f"📥 Descargar {item['titulo']}",
            data=item['bytes'],
            file_name=f"lista_p{idx+1}.png",
            mime="image/png",
            key=f"dl_{idx}"
        )
