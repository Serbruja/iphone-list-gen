import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador Pro iPhone", page_icon="📲")

st.title("📲 Creador de Estados para WhatsApp")
st.markdown("Filtra automáticamente la dirección y suma tu comisión.")

# Configuración lateral
comision = st.sidebar.number_input("Comisión a sumar (USD)", value=50)
font_size = st.sidebar.slider("Tamaño de letra", 25, 50, 35)

input_text = st.text_area("Pega la lista completa del proveedor:", height=300)

def procesar_lista(texto, incremento):
    # 1. CORTE DE SEGURIDAD: Eliminamos dirección, horarios y métodos de pago
    # Busca palabras clave que indican el final de la lista de productos
    patrones_corte = [r"⏰", r"📍", r"CABA", r"Lunes a viernes", r"💵", r"📦"]
    lineas = texto.split('\n')
    lineas_limpias = []
    
    for linea in lineas:
        # Si la línea contiene alguna palabra de corte, dejamos de procesar el resto
        if any(re.search(patron, linea, re.IGNORECASE) for patron in patrones_corte):
            break
        lineas_limpias.append(linea)
    
    texto_filtrado = "\n".join(lineas_limpias)

    # 2. INCREMENTO DE PRECIO
    # Detecta precios como: = 640$, =740, : 940, 1280$
    def substituir(match):
        separador = match.group(1) if match.group(1) else ""
        precio = int(match.group(2))
        simbolo = match.group(3) if match.group(3) else ""
        
        nuevo_precio = precio + incremento
        return f"{separador}{nuevo_precio}{simbolo}"

    # Regex: (opcional: = o : o espacio) (números) (opcional: $)
    pattern = r'([=:]\s*)(\d+)(\s*\$?)'
    return re.sub(pattern, substituir, texto_filtrado).strip()

if st.button("Generar Imagen"):
    if input_text:
        texto_final = procesar_lista(input_text, comision)
        
        # Crear imagen (Fondo oscuro estilo iPhone)
        img = Image.new('RGB', (1080, 1920), color='#121212')
        draw = ImageDraw.Draw(img)
        
        try:
            # Puedes usar 'DejaVuSans' o 'LiberationSans' si estás en Linux/Streamlit Cloud
            font = ImageFont.load_default() 
        except:
            font = ImageFont.load_default()

        # Dibujar el texto
        y_offset = 100
        for line in texto_final.split('\n'):
            # Dibujar la línea (con un margen a la izquierda de 60px)
            draw.text((60, y_offset), line, font=font, fill="#FFFFFF")
            y_offset += font_size + 15
            
        st.image(img, caption="Vista previa de tu estado")
        
        # Preparar descarga
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("Descargar Imagen", buf.getvalue(), "estado_iphone.png", "image/png")
    else:
        st.warning("Pega el texto para comenzar.")
