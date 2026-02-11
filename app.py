import streamlit as st
import re
import matplotlib.pyplot as plt
from PIL import Image
import io
from datetime import datetime

st.set_page_config(page_title="Lista Matplotlib PRO", layout="wide")

st.sidebar.header("🎨 Ajustes de Tipografía")
comision = st.sidebar.number_input("Suma fija ($)", value=50)
font_size_val = st.sidebar.slider("Tamaño de Letra", 15, 60, 35)

st.title("📲 Generador de Lista PRO")

uploaded_file = st.file_uploader("1. Sube tu Banner", type=["jpg", "png"])
if uploaded_file:
    st.session_state.banner_mpl = Image.open(uploaded_file)

input_text = st.text_area("2. Pega tu lista:", height=250)

def procesar_estricto(texto, plus):
    lineas_finales = []
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas_finales.append(f"LISTA ACTUALIZADA ({fecha_hoy})")
    
    basura = ["garantía", "11 - 18hs", "nüñez", "lunes a viernes", "encomiendas", "usd/pesos", "usdt"]
    
    for l in texto.split('\n'):
        limpia = l.strip()
        if not limpia or any(b in limpia.lower() for b in basura) or "———" in limpia:
            continue
        
        if limpia.startswith("-") and lineas_finales:
            color = limpia.replace("-", "").strip()
            if "(" in lineas_finales[-1] and "%" in lineas_finales[-1]:
                lineas_finales[-1] += f" ({color})"
            elif "(" in lineas_finales[-1]:
                lineas_finales[-1] = lineas_finales[-1].rstrip(")") + f" - {color})"
            else:
                lineas_finales[-1] += f" ({color})"
            continue

        # Solo suma si tiene el $ al lado
        limpia = re.sub(r'(\d+)\$', lambda m: f"{int(m.group(1)) + plus}$", limpia)
        limpia = limpia.replace("*", "").replace("🔺", "").replace("🔻", "").strip()
        lineas_finales.append(limpia)
        
    return lineas_finales

def generar_con_matplotlib(datos, limite_fijo=10):
    # Forzamos que la altura siempre sea para 'limite_fijo' líneas
    alto_pulgadas = limite_fijo * 0.8 + 1
    fig, ax = plt.subplots(figsize=(9, alto_pulgadas), dpi=120)
    fig.patch.set_facecolor('white')
    ax.axis('off')

    # EL TRUCO: Fijamos el eje Y de 0 a 1 siempre
    ax.set_ylim(0, 1)
    
    # Calculamos el espacio para cada línea basado en el LÍMITE, no en los datos
    espacio_entre_lineas = 1.0 / (limite_fijo + 1)
    y_pos = 0.95 

    for linea in datos:
        es_tit = any(x in linea.upper() for x in ["IPHONE", "SAMSUNG", "ACTUALIZADA", "TESTERS", "SELLADOS"])
        
        ax.text(0.05, y_pos, linea, 
                fontsize=font_size_val, 
                fontweight='bold', # Todo en negrita para máxima visibilidad
                color='#004a99' if es_tit else 'black',
                ha='left', va='center',
                transform=ax.transAxes,
                family='sans-serif')
        y_pos -= espacio_entre_lineas

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.4)
    plt.close(fig)
    return Image.open(buf)

if st.button("🚀 GENERAR LISTAS IDÉNTICAS"):
    if input_text:
        lineas = procesar_estricto(input_text, comision)
        
        # Mantenemos el corte en 10 para que la letra sea gigante
        limite_corte = 10
        partes = [lineas[i:i + limite_corte] for i in range(0, len(lineas), limite_corte)]
        
        for idx, parte in enumerate(partes):
            st.write(f"### Vista Previa - Parte {idx + 1}")
            # Le pasamos el límite al generador para que la escala sea constante
            img_texto = generar_con_matplotlib(parte, limite_fijo=limite_corte)
            
            if 'banner_mpl' in st.session_state:
                ban = st.session_state.banner_mpl
                w_t, h_t = img_texto.size
                new_h_b = int(ban.size[1] * (w_t / ban.size[0]))
                ban_res = ban.resize((w_t, new_h_b), Image.Resampling.LANCZOS)
                
                final_img = Image.new('RGB', (w_t, h_t + new_h_b), 'white')
                final_img.paste(ban_res, (0, 0))
                final_img.paste(img_texto, (0, new_h_b))
            else:
                final_img = img_texto

            buf_final = io.BytesIO()
            final_img.save(buf_final, format="PNG")
            st.image(final_img)
            st.download_button(f"📥 Descargar Parte {idx + 1}", buf_final.getvalue(), f"lista_hoja_{idx+1}.png")
