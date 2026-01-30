import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Generador Pro Final", page_icon="📲")

# --- CONFIGURACIÓN ---
st.sidebar.header("Ajustes de Diseño")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
font_size = st.sidebar.slider("Tamaño de letra", 25, 50, 36)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 45, 28)

st.title("📲 Generador de Listas Premium")

input_text = st.text_area("Pega tus listas aquí:", height=300)

def procesar_universal(texto, incremento):
    # Filtros de exclusión (Lo que NO querés que salga)
    palabras_prohibidas = [
        "⏰", "📍", "CABA", "Condiciones", "billetes", "dolares", 
        "CARGADOR", "cargador", "Consultar", "encomiendas", "CARA CHICA", "No se aceptan"
    ]
    
    lineas = texto.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        # 1. Filtro: Si la línea tiene algo prohibido, se ignora
        if any(palabra in linea for palabra in palabras_prohibidas):
            continue
        
        # 2. Ignorar fechas viejas o títulos de ingresos del proveedor
        if "MARTES" in linea.upper() or "NUEVOS INGRESOS" in linea.upper():
            continue
            
        # 3. Limpieza de caracteres raros (cuadraditos)
        l = linea.strip()
        if not l: continue
        
        # Reemplazar emojis rebeldes por puntos elegantes
        l = re.sub(r'[^\x00-\x7F]+', '• ', l) 
        lineas_limpias.append(l)

    # 4. Sumar comisión
    resultado = []
    for linea in lineas_limpias:
        nueva_linea = re.sub(r'([=–\-:\$]\s*\$?\s*)(\d{2,4})', 
                             lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        # Si la línea termina en el precio solo (ej: Nokia 106 21)
        if nueva_linea == linea:
            nueva_linea = re.sub(r'(\s)(\d{2,4})$', 
                                 lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        resultado.append(nueva_linea)
        
    return resultado

def dibujar_imagen(lineas, titulo_pag):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    ancho = 1400  # Más ancho para evitar cortes
    margen_top = 280
    espacio_linea = 22
    alto = margen_top + (len(lineas) * (font_size + espacio_linea)) + 120
    
    img = Image.new('RGB', (ancho, int(alto)), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        font_logo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
    except:
        font = ImageFont.load_default()
        font_logo = ImageFont.load_default()

    # --- ENCABEZADO DE MARCAS (Dibujado) ---
    draw.rectangle([0, 0, ancho, 240], fill="#1a1a1a") # Fondo oscuro para el logo
    
    # Dibujamos los nombres de las marcas con círculos de colores
    colores = {"APPLE": "#FFFFFF", "SAMSUNG": "#1428a0", "MOTOROLA": "#00d5ff", "XIAOMI": "#ff6700"}
    x_pos = 70
    for marca, color in colores.items():
        draw.ellipse([x_pos-10, 60, x_pos+40, 110], fill=color)
        draw.text((x_pos+50, 60), marca, font=font_logo, fill="#FFFFFF")
        x_pos += 320

    # Subtítulo con fecha
    draw.text((70, 160), f"📅 PRECIOS ACTUALIZADOS: {fecha_hoy} | {titulo_pag}", font=font, fill="#aaaaaa")

    # --- DIBUJAR LISTADO ---
    y = margen_top
    for line in lineas:
        # Si la línea es un título (tiene asteriscos)
        color_txt = "#000000"
        if "*" in line:
            color_txt = "#0056b3" # Títulos en Azul
            draw.text((70, y), line, font=font, fill=color_txt)
        else:
            draw.text((80, y), line, font=font, fill=color_txt)
        
        y += font_size + espacio_linea
            
    return img

if st.button("🚀 GENERAR IMAGEN FINAL"):
    if input_text:
        lineas_finales = procesar_universal(input_text, comision)
        
        # Partición en páginas
        paginas = [lineas_finales[i:i + lineas_por_pag] for i in range(0, len(lineas_finales), lineas_por_pag)]
        
        for idx, pag in enumerate(paginas):
            txt_pag = f"PARTE {idx+1}"
            img_res = dibujar_imagen(pag, txt_pag)
            st.image(img_res)
            
            buf = io.BytesIO()
            img_res.save(buf, format="PNG")
            st.download_button(f"📥 Descargar {txt_pag}", buf.getvalue(), f"lista_p{idx+1}.png")
    else:
        st.warning("Pega la lista antes de empezar.")
