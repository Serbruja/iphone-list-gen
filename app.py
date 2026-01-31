import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import pytz 

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador Pro Premium", page_icon="📲")

# Inicializar la memoria (session_state) si no existe
if 'imagenes_generadas' not in st.session_state:
    st.session_state.imagenes_generadas = []

# --- AJUSTES LATERALES ---
st.sidebar.header("🎨 Ajustes de Imagen")
comision = st.sidebar.number_input("Comisión (USD)", value=50)
ancho_img = st.sidebar.slider("Ancho de imagen", 1200, 1600, 1500)
font_size = st.sidebar.slider("Tamaño de letra", 25, 45, 34)
lineas_por_pag = st.sidebar.slider("Líneas por imagen", 15, 60, 35)

input_text = st.text_area("Pega tus listas aquí:", height=300)

# [Aquí van tus funciones procesar_texto y dibujar_imagen que ya tenemos]
# (Asegúrate de mantenerlas igual, solo cambiaremos la lógica del botón)

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
        lineas_limpias.append(l)

    resultado = []
    for linea in lineas_limpias:
        nueva_linea = re.sub(r'([=–\-:\$]\s*\$?\s*)(\d{2,4})', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        if nueva_linea == linea:
            nueva_linea = re.sub(r'(\s)(\d{2,4})$', lambda m: f"{m.group(1)}{int(m.group(2)) + incremento}", linea)
        resultado.append(nueva_linea)
    return resultado

def dibujar_imagen(lineas, titulo_pag, es_primera):
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
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        font_logo = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()
        font_logo = ImageFont.load_default()

    draw.rectangle([0, 0, ancho_img, 200], fill="#000000")
    marcas = [("🍎 APPLE", 60), ("🔵 SAMSUNG", 450), ("📱 MOTOROLA", 880), ("🟠 XIAOMI", 1250)]
    for texto_m, x_m in marcas:
        draw.text((x_m, 50), texto_m, font=font_logo, fill="#FFFFFF")

    info_header = f"📅 ACTUALIZADO: {fecha_hoy} | {titulo_pag}" if es_primera else f"🚀 CATÁLOGO PRODUCTOS | {titulo_pag}"
    draw.text((60, 130), info_header, font=font, fill="#AAAAAA")

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

# --- LÓGICA DE BOTONES CON MEMORIA ---
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🚀 GENERAR IMÁGENES"):
        if input_text:
            lineas_finales = procesar_texto(input_text, comision)
            paginas = [lineas_finales[i:i + lineas_por_pag] for i in range(0, len(lineas_finales), lineas_por_pag)]
            
            # Guardamos las imágenes en la memoria de la sesión
            st.session_state.imagenes_generadas = []
            for idx, pag in enumerate(paginas):
                txt_pag = f"PARTE {idx+1}"
                img_res = dibujar_imagen(pag, txt_pag, es_primera=(idx==0))
                
                # Convertir a bytes para que estén listos para descargar
                buf = io.BytesIO()
                img_res.save(buf, format="PNG")
                st.session_state.imagenes_generadas.append({
                    "titulo": txt_pag,
                    "bytes": buf.getvalue(),
                    "pil_img": img_res
                })
        else:
            st.error("Pega la lista primero.")

with col_btn2:
    if st.button("🗑️ LIMPIAR TODO"):
        st.session_state.imagenes_generadas = []
        st.rerun()

# --- MOSTRAR RESULTADOS DESDE LA MEMORIA ---
if st.session_state.imagenes_generadas:
    for idx, item in enumerate(st.session_state.imagenes_generadas):
        st.divider()
        st.subheader(f"🖼️ {item['titulo']}")
        st.image(item['pil_img'])
        st.download_button(
            label=f"📥 Descargar {item['titulo']}",
            data=item['bytes'],
            file_name=f"lista_parte_{idx+1}.png",
            mime="image/png",
            key=f"btn_dl_{idx}" # Clave única para que no se confunda
        )
