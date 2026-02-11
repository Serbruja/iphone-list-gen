import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

st.set_page_config(page_title="Lista Final WhatsApp", layout="wide")

# --- AJUSTES ---
st.sidebar.header("⚙️ Control de Calidad")
comision = st.sidebar.number_input("Suma fija ($)", value=50)
# Un ancho menor (500-600) hace que el texto se vea mucho más grande en el celular
ancho_hoja = 550 
font_size = st.sidebar.slider("Tamaño de Letra", 40, 80, 60)

st.title("📲 Generador de Lista Legible")

uploaded_file = st.file_uploader("1. Sube tu Banner", type=["jpg", "png"])
if uploaded_file:
    st.session_state.img_banner = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista aquí:", height=250)

def procesar_lista_v2(texto, plus):
    lineas_finales = []
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas_finales.append(f"LISTA ACTUALIZADA ({fecha_hoy})")
    
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "usdt", "actualizada", "———"]
    
    lineas_raw = texto.split('\n')
    for l in lineas_raw:
        limpia = l.strip()
        if not limpia or any(b in limpia.lower() for b in basura):
            continue
        
        # UNIÓN DE COLORES: Si empieza con "-" se une a la anterior entre ()
        if limpia.startswith("-") and lineas_finales:
            color = limpia.replace("-", "").strip()
            if "(" in lineas_finales[-1] and "%" not in lineas_finales[-1].split('(')[-1]:
                lineas_finales[-1] = lineas_finales[-1].rstrip(")") + f" - {color})"
            else:
                lineas_finales[-1] += f" ({color})"
            continue

        # SUMA DE COMISIÓN INTELIGENTE (Solo después de = o junto a $)
        if "$" in limpia or "=" in limpia:
            # Esta regex busca números que sigan a un '=' o precedan/sigan a un '$'
            limpia = re.sub(r'(?<=[=\$])\s*(\d+)|(\d+)\s*(?=[=\$])', 
                            lambda m: str(int(m.group(0)) + plus) if m.group(0).isdigit() else m.group(0), 
                            limpia)
        
        # Limpieza de basura visual
        limpia = limpia.replace("*", "").replace("🔺", "").replace("🔻", "").replace("❕", "").strip()
        lineas_finales.append(limpia)
        
    return lineas_finales

def dibujar_parte(datos, num_parte):
    # Banner
    if 'img_banner' in st.session_state:
        w_perc = (ancho_hoja / float(st.session_state.img_banner.size[0]))
        h_banner = int((float(st.session_state.img_banner.size[1]) * float(w_perc)))
        banner_res = st.session_state.img_banner.resize((ancho_hoja, h_banner), Image.Resampling.LANCZOS)
    else:
        h_banner = 20
        banner_res = Image.new('RGB', (ancho_hoja, h_banner), color="white")

    interlineado = 12
    alto_total = h_banner + (len(datos) * (font_size + interlineado)) + 100
    img = Image.new('RGB', (ancho_hoja, int(alto_total)), color="white")
    img.paste(banner_res, (0, 0))
    
    draw = ImageDraw.Draw(img)
    try:
        # Usamos Bold para máxima legibilidad
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    y = h_banner + 40
    for i, linea in enumerate(datos):
        # Colores: Azul para secciones y fecha, Negro para el resto
        es_seccion = any(x in linea.upper() for x in ["IPHONE", "SAMSUNG", "TESTERS", "SELLADOS", "ACTUALIZADA"])
        color = "#004a99" if es_seccion else "black"
        
        draw.text((25, y), linea, font=font, fill=color)
        y += font_size + interlineado
        
    return img

if st.button("🚀 GENERAR IMÁGENES GIGANTES"):
    if input_text:
        todas_las_lineas = procesar_lista_v2(input_text, comision)
        
        # Corte de página: Máximo 12 líneas para asegurar que la letra sea ENORME
        limite = 12
        partes = [todas_las_lineas[i:i + limite] for i in range(0, len(todas_las_lineas), limite)]
        
        for idx, parte in enumerate(partes):
            st.write(f"### Vista Previa - Parte {idx + 1}")
            img_final = dibujar_parte(parte, idx + 1)
            
            buf = io.BytesIO()
            img_final.save(buf, format="PNG")
            st.image(img_final)
            st.download_button(f"📥 Descargar Parte {idx + 1}", buf.getvalue(), f"lista_vips_{idx+1}.png")
