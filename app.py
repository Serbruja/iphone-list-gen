import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Generador Pro Dúo", page_icon="📲")

# --- BARRA LATERAL ---
st.sidebar.header("Configuración")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
font_size = st.sidebar.slider("Tamaño de letra", 25, 55, 38)
lineas_por_pagina = st.sidebar.slider("Líneas por imagen", 20, 50, 30)

st.title("📲 Generador de Listas Unificadas")
st.markdown("Pega ambas listas juntas. El sistema las procesará y dividirá en páginas si es necesario.")

input_text = st.text_area("Pega tus listas aquí:", height=300, placeholder="Pega lista de iPhone y Android aquí...")

def procesar_universal(texto, incremento):
    # Patrones para limpiar basura logística
    patrones_corte = [r"⏰", r"📍", r"CABA", r"Condiciones de pago", r"🚨", r"⚠️", r"Lunes a viernes", r"💵", r"📦", r"encomiendas"]
    lineas = texto.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        if any(re.search(patron, linea, re.IGNORECASE) for patron in patrones_corte):
            continue # Saltamos líneas de logística pero seguimos procesando el resto
        
        # Limpiar fechas viejas del proveedor
        if "MARTES" in linea.upper() or "LISTA ACTUALIZADA" in linea.upper():
            continue
            
        # Reemplazos estéticos
        l = linea.replace('‼️', '!!').replace('🔺', '•').replace('🔻', '•').replace('📲', '•')
        lineas_limpias.append(l.strip())

    # Lógica de precios
    resultado = []
    for linea in lineas_limpias:
        # Detecta formatos: "= 800", "- $800", ": 800", " 800$"
        nueva_linea = re.sub(r'([=–\-:\$]\s*\$?\s*)(\d{2,4})', 
                             lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        
        # Si la línea termina en número sin símbolo (ej: Nokia 106 25)
        if nueva_linea == linea:
            nueva_linea = re.sub(r'(\s)(\d{2,4})$', 
                                 lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        
        resultado.append(nueva_linea)
    return [l for l in resultado if l] # Quitar líneas vacías

def dibujar_pagina(lineas, titulo_pag):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    # Configuración de tamaño (Ancho 1200 para que no se corte)
    ancho = 1200
    margen_superior = 250
    espaciado = 25
    alto_dinamico = margen_superior + (len(lineas) * (font_size + espaciado)) + 150
    
    img = Image.new('RGB', (ancho, int(alto_dinamico)), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        font_logo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
    except:
        font = ImageFont.load_default()
        font_logo = ImageFont.load_default()

    # --- ENCABEZADO ESTILO MARCAS ---
    draw.rectangle([0, 0, ancho, 220], fill="#f8f9fa")
    marcas_texto = "🍎 APPLE  |  📱 SAMSUNG  |  🔘 MOTOROLA  |  🟠 XIAOMI"
    draw.text((60, 50), marcas_texto, font=font_logo, fill="#333333")
    draw.text((60, 140), f"📅 PRECIOS ACTUALIZADOS: {fecha_hoy} ({titulo_pag})", font=font, fill="#555555")
    draw.line([(60, 210), (ancho-60, 210)], fill="#000000", width=3)

    y = margen_superior
    for line in lineas:
        # Si la línea es un título (tiene asteriscos), la ponemos en azul
        color_texto = "#000000"
        if "*" in line: color_texto = "#0056b3"
        
        draw.text((80, y), line, font=font, fill=color_texto)
        y += font_size + espaciado
        
    return img

if st.button("🚀 Generar Todo"):
    if input_text:
        todas_las_lineas = procesar_universal(input_text, comision)
        
        # Dividir en páginas según la configuración
        paginas = [todas_las_lineas[i:i + lineas_por_pagina] for i in range(0, len(todas_las_lineas), lineas_por_pagina)]
        
        for idx, lineas_pag in enumerate(paginas):
            nombre_pag = f"PARTE {idx + 1}"
            img_final = dibujar_pagina(lineas_pag, nombre_pag)
            
            st.subheader(f"🖼️ {nombre_pag}")
            st.image(img_final)
            
            buf = io.BytesIO()
            img_final.save(buf, format="PNG")
            st.download_button(f"📥 Descargar {nombre_pag}", buf.getvalue(), f"lista_p{idx+1}.png")
    else:
        st.warning("Pega las listas para comenzar.")
