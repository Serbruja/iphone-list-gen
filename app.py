import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Generador Pro WhatsApp", layout="wide")

# --- INTERFAZ DE AJUSTES ---
st.sidebar.header("⚙️ Configuración")
comision = st.sidebar.number_input("Comisión a sumar ($)", value=50)
font_size = st.sidebar.slider("Tamaño de Letra", 40, 80, 55)
ancho_hoja = 750 # Ancho equilibrado para nitidez

st.title("📲 Generador de Listas para Estados")

uploaded_file = st.file_uploader("1. Sube tu Banner (se verá completo)", type=["jpg", "png"])
if uploaded_file:
    st.session_state.img_banner = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista aquí:", height=250)

def procesar_lista(texto, plus):
    lineas_finales = []
    # Condición 2: Fecha del día
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas_finales.append(f"LISTA ACTUALIZADA ({fecha_hoy})")
    
    # Condición 5: Filtros de limpieza
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "usdt", "actualizada", "———"]
    
    lineas_raw = texto.split('\n')
    for l in lineas_raw:
        limpia = l.strip()
        if not limpia or any(b in limpia.lower() for b in basura):
            continue
        
        # Condición 3 & 4: Unir colores y respetar porcentajes
        # Si la línea empieza con guion, es un color/detalle para la línea anterior
        if limpia.startswith("-") and lineas_finales:
            color = limpia.replace("-", "").strip()
            if "(" in lineas_finales[-1] and "%" in lineas_finales[-1]:
                # Si ya hay paréntesis de porcentaje, ponemos los colores en otros paréntesis
                lineas_finales[-1] += f" ({color})"
            elif "(" in lineas_finales[-1]:
                 # Si ya hay un paréntesis (de color), lo unimos con guion
                lineas_finales[-1] = lineas_finales[-1].rstrip(")") + f" - {color})"
            else:
                lineas_finales[-1] += f" ({color})"
            continue

        # Condición 1: Sumar comisión SOLO si tiene el símbolo $
        if "$" in limpia:
            # Buscamos números de 3 o 4 cifras
            limpia = re.sub(r'(\d{3,4})', lambda m: str(int(m.group(1)) + plus), limpia)
        
        # Limpieza de símbolos estéticos
        limpia = limpia.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "").strip()
        lineas_finales.append(limpia)
        
    return lineas_finales

def dibujar_imagen(datos, titulo_parte):
    # Procesar Banner
    if 'img_banner' in st.session_state:
        w_perc = (ancho_hoja / float(st.session_state.img_banner.size[0]))
        h_banner = int((float(st.session_state.img_banner.size[1]) * float(w_perc)))
        banner_res = st.session_state.img_banner.resize((ancho_hoja, h_banner), Image.Resampling.LANCZOS)
    else:
        h_banner = 20
        banner_res = Image.new('RGB', (ancho_hoja, h_banner), color="white")

    # Espaciado y dimensiones
    interlineado = 10
    alto_total = h_banner + (len(datos) * (font_size + interlineado)) + 80
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="white")
    img.paste(banner_res, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        font_min = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 30)
    except:
        font = font_min = ImageFont.load_default()

    # Dibujar indicador de parte
    draw.text((ancho_hoja - 150, 10), titulo_parte, font=font_min, fill="gray")

    y = h_banner + 30
    for i, linea in enumerate(datos):
        # Colores: Azul para secciones, Negro para el resto
        es_seccion = any(x in linea.upper() for x in ["IPHONE", "SAMSUNG", "TESTERS", "SELLADOS", "ACTUALIZADA"])
        color = "#004a99" if es_seccion else "black"
        
        draw.text((35, y), linea, font=font, fill=color)
        y += font_size + interlineado
        
    return img

if st.button("🚀 GENERAR LISTAS (CON CORTE AUTOMÁTICO)"):
    if input_text:
        todas_las_lineas = procesar_lista(input_text, comision)
        
        # Condición 7: Corte de página (Máximo 15 líneas por imagen para que la letra sea gigante)
        limite = 15
        partes = [todas_las_lineas[i:i + limite] for i in range(0, len(todas_las_lineas), limite)]
        
        for idx, parte in enumerate(partes):
            st.subheader(f"Parte {idx + 1}")
            img_resultado = dibujar_imagen(parte, f"PARTE {idx + 1}")
            
            buf = io.BytesIO()
            img_resultado.save(buf, format="PNG")
            st.image(img_resultado)
            st.download_button(f"📥 Descargar Parte {idx + 1}", buf.getvalue(), f"lista_parte_{idx+1}.png")
