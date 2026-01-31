import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Generador Pro Final", page_icon="📲")

# --- AJUSTES EN BARRA LATERAL ---
st.sidebar.header("🎨 Ajustes de Imagen")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_img = st.sidebar.slider("Ancho de imagen", 1000, 1600, 1450) # Más ancho para evitar cortes
font_size = st.sidebar.slider("Tamaño de letra", 25, 45, 34)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 50, 32)

st.title("📲 Generador de Listas Premium")

input_text = st.text_area("Pega tus listas aquí:", height=300)

def procesar_texto(texto, incremento):
    # 1. Filtro estricto: Lo que NO debe aparecer bajo ninguna circunstancia
    palabras_prohibidas = [
        "⏰", "📍", "CABA", "Condiciones", "billetes", "dolares", "CARA CHICA",
        "No se aceptan", "CARGADOR", "cargador", "encomiendas", "Consultar",
        "MARTES", "LISTA ACTUALIZADA", "ACTUALIZO", "¡Nuevos ingresos"
    ]
    
    lineas = texto.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        upper_l = linea.upper()
        # Filtro de seguridad: borrar líneas con términos prohibidos
        if any(p.upper() in upper_l for p in palabras_prohibidas):
            continue
        
        l = linea.strip()
        if not l: continue
        
        # Limpieza de emojis rebeldes que salen como cuadraditos
        l = re.sub(r'[^\x00-\x7F]+', '• ', l) 
        lineas_limpias.append(l)

    # 2. Sumar comisión (Detector universal de precios)
    resultado = []
    for linea in lineas_limpias:
        # Detectar patrones como "= 800", "- $800", ": 800"
        nueva_linea = re.sub(r'([=–\-:\$]\s*\$?\s*)(\d{2,4})', 
                             lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        
        # Detectar precios al final sin símbolos (ej: Nokia 106 21)
        if nueva_linea == linea:
            nueva_linea = re.sub(r'(\s)(\d{2,4})$', 
                                 lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        resultado.append(nueva_linea)
        
    return resultado

def dibujar_imagen(lineas, titulo_pag, es_primera):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    margen_top = 260
    espacio_linea = 20
    alto = margen_top + (len(lineas) * (font_size + espacio_linea)) + 100
    
    img = Image.new('RGB', (ancho_img, int(alto)), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        font_logo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
    except:
        font = ImageFont.load_default()
        font_logo = ImageFont.load_default()

    # --- ENCABEZADO NEGRO PREMIUM ---
    draw.rectangle([0, 0, ancho_img, 220], fill="#000000")
    
    # Logos dibujados con símbolos universales para que salgan SIEMPRE
    marcas = [("🍎 APPLE", 70), ("💙 SAMSUNG", 380), ("🩵 MOTOROLA", 750), ("🧡 XIAOMI", 1150)]
    for texto_m, x_m in marcas:
        draw.text((x_m, 50), texto_m, font=font_logo, fill="#FFFFFF")

    # Fecha solo en la primera página, en las demás solo el número de parte
    if es_primera:
        info_header = f"📅 PRECIOS ACTUALIZADOS: {fecha_hoy} | {titulo_pag}"
    else:
        info_header = f"🚀 CONTINUACIÓN | {titulo_pag}"
        
    draw.text((70, 140), info_header, font=font, fill="#888888")

    # --- LISTADO DE PRODUCTOS ---
    y = margen_top
    for line in lineas:
        color_txt = "#000000"
        # Resaltar títulos que tengan asteriscos
        if "*" in line:
            color_txt = "#0056b3"
            draw.text((70, y), line, font=font, fill=color_txt)
        else:
            draw.text((90, y), line, font=font, fill=color_txt)
        y += font_size + espacio_linea
            
    return img

if st.button("🚀 GENERAR LISTA SIN ERRORES"):
    if input_text:
        lineas_finales = procesar_texto(input_text, comision)
        
        # Partición en páginas
        paginas = [lineas_finales[i:i + lineas_por_pag] for i in range(0, len(lineas_finales), lineas_por_pag)]
        
        for idx, pag in enumerate(paginas):
            txt_pag = f"PÁGINA {idx+1}"
            img_res = dibujar_imagen(pag, txt_pag, es_primera=(idx==0))
            
            st.subheader(f"🖼️ {txt_pag}")
            st.image(img_res)
            
            buf = io.BytesIO()
            img_res.save(buf, format="PNG")
            st.download_button(f"📥 Descargar {txt_pag}", buf.getvalue(), f"lista_p{idx+1}.png")
    else:
        st.error("Por favor, pega el texto de las listas primero.")
