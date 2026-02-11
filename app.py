import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Generador Zoom WhatsApp", layout="wide")

# --- AJUSTES ---
st.sidebar.header("🎨 Ajustes de Visibilidad")
comision = st.sidebar.number_input("Suma fija ($)", value=50)
font_size = st.sidebar.slider("Tamaño de Letra", 40, 70, 50)
# Ancho pequeño = Letra más grande en WhatsApp
ancho_hoja = 500 

st.title("📲 Generador de Estados Legibles")

uploaded_file = st.file_uploader("1. Sube tu Banner", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_raw = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista aquí:", height=200)

def procesar_logica(texto, plus):
    lineas_finales = []
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas_finales.append(f"LISTA ACTUALIZADA ({fecha_hoy})")
    
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "usdt"]
    
    for l in texto.split('\n'):
        limpia = l.strip()
        if not limpia or any(b in limpia.lower() for b in basura) or "———" in limpia:
            continue
        
        # Unión de colores (Condición 3)
        if limpia.startswith("-") and lineas_finales:
            color = limpia.replace("-", "").strip()
            if "(" in lineas_finales[-1] and "%" not in lineas_finales[-1].split('(')[-1]:
                lineas_finales[-1] = lineas_finales[-1].rstrip(")") + f" - {color})"
            else:
                lineas_finales[-1] += f" ({color})"
            continue

        # Suma de comisión solo a precios (Condición 1 y 4)
        if "$" in limpia or "=" in limpia:
            # Busca números que sigan a = o $ exclusivamente
            limpia = re.sub(r'([=\$]\s*)(\d+)|(\d+)(\s*[=\$])', 
                            lambda m: f"{m.group(1) or ''}{int(m.group(2) or m.group(3)) + plus}{m.group(4) or ''}", 
                            limpia)
        
        limpia = limpia.replace("*", "").replace("🔺", "").replace("🔻", "").strip()
        lineas_finales.append(limpia)
    return lineas_finales

def renderizar_parte(datos):
    # Banner
    if 'banner_raw' in st.session_state:
        w_p = (ancho_hoja / float(st.session_state.banner_raw.size[0]))
        h_b = int((float(st.session_state.banner_raw.size[1]) * float(w_p)))
        banner = st.session_state.banner_raw.resize((ancho_hoja, h_b), Image.Resampling.LANCZOS)
    else:
        h_b = 20
        banner = Image.new('RGB', (ancho_hoja, h_b), color="white")

    # Espaciado apretado para que no se estire la imagen
    interlineado = 15
    alto_total = h_b + (len(datos) * (font_size + interlineado)) + 80
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="white")
    img.paste(banner, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        # Usamos la fuente Bold del sistema
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    y = h_b + 30
    for i, linea in enumerate(datos):
        es_tit = any(x in linea.upper() for x in ["IPHONE", "SAMSUNG", "ACTUALIZADA", "TESTERS"])
        color = "#004a99" if es_tit else "black"
        draw.text((20, y), linea, font=font, fill=color)
        y += font_size + interlineado
        
    return img

if st.button("🚀 GENERAR IMÁGENES DE ALTA VISIBILIDAD"):
    if input_text:
        todas = procesar_logica(input_text, comision)
        
        # CORTE DE PÁGINA (Condición 7): 10 líneas máximo para asegurar que la letra sea ENORME
        limite = 10
        partes = [todas[i:i + limite] for i in range(0, len(todas), limite)]
        
        for idx, parte in enumerate(partes):
            st.write(f"### Parte {idx + 1}")
            img_final = renderizar_parte(parte)
            
            buf = io.BytesIO()
            img_final.save(buf, format="PNG")
            st.image(img_final)
            st.download_button(f"📥 Descargar Parte {idx + 1}", buf.getvalue(), f"lista_p{idx+1}.png")
