import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz 

st.set_page_config(page_title="Generador Premium Pro", page_icon="📲")

# --- AJUSTES ---
st.sidebar.header("🎨 Ajustes de Imagen")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_img = st.sidebar.slider("Ancho de imagen", 1200, 1600, 1500)
font_size = st.sidebar.slider("Tamaño de letra", 25, 45, 34)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 60, 35)

input_text = st.text_area("Pega tus listas aquí:", height=300)

def procesar_texto(texto, incremento):
    # LISTA NEGRA: Agregamos NOKIA para que se ignore por completo
    palabras_prohibidas = [
        "⏰", "📍", "CABA", "Condiciones", "billetes", "dolares", "CARA CHICA",
        "No se aceptan", "CARGADOR", "cargador", "encomiendas", "Consultar",
        "MARTES", "LISTA ACTUALIZADA", "ACTUALIZO", "¡Nuevos ingresos",
        "Lunes a viernes", "USD/PESOS/USDT", "solo para completar", "mal estado",
        "NOKIA" # <--- Filtro para omitir Nokia
    ]
    
    lineas = texto.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        upper_l = linea.upper()
        # Si la línea contiene "NOKIA" o cualquier palabra prohibida, la salteamos
        if any(p.upper() in upper_l for p in palabras_prohibidas):
            continue
        
        l = linea.strip()
        if not l or len(l) < 2: continue
        lineas_limpias.append(l)

    resultado = []
    for linea in lineas_limpias:
        # Sumar comisión
        nueva_linea = re.sub(r'([=–\-:\$]\s*\$?\s*)(\d{2,4})', 
                             lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        if nueva_linea == linea:
            nueva_linea = re.sub(r'(\s)(\d{2,4})$', 
                                 lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        resultado.append(nueva_linea)
        
    return resultado

def dibujar_imagen(lineas, titulo_pag, es_primera):
    # Sincronización horaria Argentina
    try:
        zona_horaria = pytz.timezone('America/Argentina/Buenos_Aires')
        fecha_hoy = datetime.now(zona_horaria).strftime("%d/%m/%Y")
    except:
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    margen_top = 240
    espacio_linea = 22
    alto = margen_top + (len(lineas) * (font_size + espacio_linea)) + 120
    
    img = Image.new('RGB', (ancho_img, int(alto)), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    # Fuentes con soporte para acentos
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        font_logo = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 48)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            font_logo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            font = ImageFont.load_default()
            font_logo = ImageFont.load_default()

    # --- ENCABEZADO NEGRO ---
    draw.rectangle([0, 0, ancho_img, 200], fill="#000000")
    
    # Logos de marcas (Ahora sin Nokia)
    marcas = [("🍎 APPLE", 60), ("🔵 SAMSUNG", 450), ("📱 MOTOROLA", 880), ("🟠 XIAOMI", 1250)]
    for texto_m, x_m in marcas:
        draw.text((x_m, 50), texto_m, font=font_logo, fill="#FFFFFF")

    if es_primera:
        info_header = f"📅 ACTUALIZADO: {fecha_hoy} | {titulo_pag}"
    else:
        info_header = f"🚀 CATÁLOGO DE PRODUCTOS | {titulo_pag}"
        
    draw.text((60, 130), info_header, font=font, fill="#AAAAAA")

    # --- LISTADO ---
    y = margen_top
    for line in lineas:
        color_txt = "#000000"
        if "*" in line:
            color_txt = "#0056b3"
            draw.text((60, y), line.replace("*", ""), font=font, fill=color_txt)
        else:
            clean_line = line.replace("-", "•")
            draw.text((80, y), clean_line, font=font, fill=color_txt)
        y += font_size + espacio_linea
            
    return img

if st.button("🚀 GENERAR LISTA SIN NOKIA"):
    if input_text:
        lineas_finales = procesar_texto(input_text, comision)
        paginas = [lineas_finales[i:i + lineas_por_pag] for i in range(0, len(lineas_finales), lineas_por_pag)]
        
        for idx, pag in enumerate(paginas):
            txt_pag = f"PARTE {idx+1}"
            img_res = dibujar_imagen(pag, txt_pag, es_primera=(idx==0))
            st.subheader(f"🖼️ {txt_pag}")
            st.image(img_res)
            
            buf = io.BytesIO()
            img_res.save(buf, format="PNG")
            st.download_button(f"📥 Descargar {txt_pag}", buf.getvalue(), f"lista_p{idx+1}.png")
    else:
        st.error("Pega las listas primero.")
