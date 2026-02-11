import streamlit as st
import re
import matplotlib.pyplot as plt
from PIL import Image
import io
from datetime import datetime

st.set_page_config(page_title="Lista Premium Matplotlib", layout="wide")

# --- AJUSTES ---
st.sidebar.header("🎨 Estética de la Lista")
comision = st.sidebar.number_input("Suma fija ($)", value=50)
font_size = st.sidebar.slider("Tamaño de Letra", 10, 40, 22) # Matplotlib usa escalas distintas

st.title("📲 Generador de Lista Oficial (Alta Definición)")

uploaded_file = st.file_uploader("1. Sube tu Banner", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_img = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista:", height=200)

def limpiar_y_procesar(texto, plus):
    lineas_finales = []
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas_finales.append(f"LISTA ACTUALIZADA ({fecha_hoy})")
    
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "usdt"]
    
    lineas_raw = texto.split('\n')
    for l in lineas_raw:
        limpia = l.strip()
        if not limpia or any(b in limpia.lower() for b in basura) or "———" in limpia:
            continue
        
        # Lógica de unión de colores y protección de batería (%)
        if limpia.startswith("-") and lineas_finales:
            color = limpia.replace("-", "").strip()
            if "(" in lineas_finales[-1] and "%" not in lineas_finales[-1].split('(')[-1]:
                lineas_finales[-1] = lineas_finales[-1].rstrip(")") + f" - {color})"
            else:
                lineas_finales[-1] += f" ({color})"
            continue

        # SUMA DE COMISIÓN SOLO A PRECIOS (Detecta el $ o el =)
        if "$" in limpia or "=" in limpia:
            # Busca números que estén después de = o al lado de $
            limpia = re.sub(r'(?<=[=\$])\s*(\d+)|(\d+)\s*(?=[=\$])', 
                            lambda m: str(int(m.group(0)) + plus) if m.group(0).isdigit() else m.group(0), 
                            limpia)
        
        limpia = limpia.replace("*", "").replace("🔺", "").replace("🔻", "").strip()
        lineas_finales.append(limpia)
    return lineas_finales

def crear_imagen_matplotlib(datos, num_parte):
    # Configuramos la figura
    # Un "ancho" de 8 y alto dinámico
    alto_dinamico = len(datos) * 0.6 + 2 
    fig, ax = plt.subplots(figsize=(8, alto_dinamico), dpi=100)
    fig.patch.set_facecolor('white')
    ax.axis('off')

    # Si hay banner, lo ponemos arriba (usando una técnica de subplots o simplemente texto)
    # Por simplicidad y para que la letra sea la prioridad, manejaremos el banner como imagen aparte
    # o lo pegamos al final. Aquí nos enfocamos en el texto:
    
    y_pos = 1.0
    for i, linea in enumerate(datos):
        # Estilo de letra
        es_titulo = any(x in linea.upper() for x in ["ACTUALIZADA", "IPHONE", "SAMSUNG", "TESTERS"])
        peso = 'bold' if es_titulo or "=" in linea else 'normal'
        color = '#004a99' if es_titulo else 'black'
        
        ax.text(0.05, y_pos, linea, 
                fontsize=font_size, 
                fontweight=peso, 
                color=color,
                ha='left', va='center',
                transform=ax.transAxes,
                family='sans-serif')
        y_pos -= (1.0 / (len(datos) + 1))

    # Guardar a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.2, facecolor='white')
    plt.close(fig)
    return Image.open(buf)

if st.button("🚀 GENERAR IMÁGENES DE ALTA LECTURA"):
    if input_text:
        todas = limpiar_y_procesar(input_text, comision)
        
        # Corte de página: 12 líneas máximo para que en el celu se vea GIGANTE
        limite = 12
        partes = [todas[i:i + limite] for i in range(0, len(todas), limite)]
        
        for idx, parte in enumerate(partes):
            st.write(f"### Parte {idx + 1}")
            img_texto = crear_imagen_matplotlib(parte, idx + 1)
            
            # Pegar Banner arriba si existe
            if 'banner_img' in st.session_state:
                ban = st.session_state.banner_img
                # Redimensionar banner al ancho de la imagen de texto
                w_t, h_t = img_texto.size
                w_b, h_b = ban.size
                new_h_b = int(h_b * (w_t / w_b))
                ban_res = ban.resize((w_t, new_h_b), Image.Resampling.LANCZOS)
                
                final_img = Image.new('RGB', (w_t, h_t + new_h_b), 'white')
                final_img.paste(ban_res, (0, 0))
                final_img.paste(img_texto, (0, new_h_b))
            else:
                final_img = img_texto

            buf_final = io.BytesIO()
            final_img.save(buf_final, format="PNG")
            st.image(final_img)
            st.download_button(f"📥 Descargar Parte {idx + 1}", buf_final.getvalue(), f"lista_v{idx+1}.png")
