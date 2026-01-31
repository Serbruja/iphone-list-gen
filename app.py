import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Generador Premium Final", page_icon="📲")

# --- AJUSTES LATERALES ---
st.sidebar.header("🎨 Ajustes de Imagen")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_img = st.sidebar.slider("Ancho de imagen", 1200, 1600, 1500)
font_size = st.sidebar.slider("Tamaño de letra", 25, 45, 34)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 60, 35)

st.title("📲 Generador de Listas Premium")

input_text = st.text_area("Pega tus listas aquí:", height=300)

def procesar_texto(texto, incremento):
    # Lista negra estricta
    palabras_prohibidas = [
        "⏰", "📍", "CABA", "Condiciones", "billetes", "dolares", "CARA CHICA",
        "No se aceptan", "CARGADOR", "cargador", "encomiendas", "Consultar",
        "MARTES", "LISTA ACTUALIZADA", "ACTUALIZO", "¡Nuevos ingresos",
        "Lunes a viernes", "USD/PESOS/USDT", "solo para completar", "mal estado"
    ]
    
    lineas = texto.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        upper_l = linea.upper()
        # Filtro: si tiene una palabra prohibida, se descarta la línea completa
        if any(p.upper() in upper_l for p in palabras_prohibidas):
            continue
        
        l = linea.strip()
        if not l or len(l) < 2: continue # Ignorar líneas vacías o de un solo carácter
        
        # Reemplazar emojis rebeldes que fallan en la fuente
        l = re.sub(r'[^\x00-\x7F]+', '• ', l) 
        lineas_limpias.append(l)

    # Lógica de precios
    resultado = []
    for linea in lineas_limpias:
        # Sumar a formatos: "= 800", "- $800", ": 800"
        nueva_linea = re.sub(r'([=–\-:\$]\s*\$?\s*)(\d{2,4})', 
                             lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        # Sumar a precios al final de línea
        if nueva_linea == linea:
            nueva_linea = re.sub(r'(\s)(\d{2,4})$', 
                                 lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        resultado.append(nueva_linea)
        
    return resultado

def dibujar_imagen(lineas, titulo_pag, es_primera):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    margen_top = 240
    espacio_linea = 22
    alto = margen_top + (len(lineas) * (font_size + espacio_linea)) + 120
    
    img = Image.new('RGB', (ancho_img, int(alto)), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        font_logo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
    except:
        font = ImageFont.load_default()
        font_logo = ImageFont.load_default()

    # --- ENCABEZADO NEGRO ---
    draw.rectangle([0, 0, ancho_img, 200], fill="#000000")
    
    # Marcas con espaciado amplio para evitar cortes
    # Formato: (Emoji + Nombre, Posicion X)
    marcas = [("🍎 APPLE", 60), ("🔵 SAMSUNG", 420), ("📱 MOTOROLA", 840), ("🟠 XIAOMI", 1230)]
    for texto_m, x_m in marcas:
        draw.text((x_m, 45), texto_m, font=font_logo, fill="#FFFFFF")

    # Fecha solo en la primera página
    if es_primera:
        info_header = f"📅 PRECIOS ACTUALIZADOS: {fecha_hoy} | {titulo_pag}"
    else:
        info_header = f"🚀 CATÁLOGO PRODUCTOS | {titulo_pag}"
        
    draw.text((60, 130), info_header, font=font, fill="#AAAAAA")

    # --- DIBUJAR LISTADO ---
    y = margen_top
    for line in lineas:
        color_txt = "#000000"
        # Títulos en azul
        if "*" in line:
            color_txt = "#0056b3"
            draw.text((60, y), line, font=font, fill=color_txt)
        else:
            draw.text((80, y), line, font=font, fill=color_txt)
        y += font_size + espacio_linea
            
    return img

if st.button("🚀 GENERAR LISTA LIMPIA"):
    if input_text:
        lineas_finales = procesar_texto(input_text, comision)
        
        # Dividir en páginas
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
