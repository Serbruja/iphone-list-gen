import streamlit as st
import re
import matplotlib.pyplot as plt
from PIL import Image
import io
from datetime import datetime

st.set_page_config(page_title="Lista Matplotlib PRO", layout="wide")

# --- INTERFAZ ---
st.sidebar.header("🎨 Ajustes de Tipografía")
comision = st.sidebar.number_input("Suma fija ($)", value=50)
# En Matplotlib, un font_size de 25-30 ya es muy grande
font_size_val = st.sidebar.slider("Tamaño de Letra", 15, 45, 28)

st.title("📲 Generador de Lista (Motor Matplotlib)")

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
        
        # Unión de colores/detalles (Condición 3)
        if limpia.startswith("-") and lineas_finales:
            color = limpia.replace("-", "").strip()
            # Si la línea anterior ya tiene paréntesis (ej. porcentaje), agregamos los colores aparte
            if "(" in lineas_finales[-1] and "%" in lineas_finales[-1]:
                lineas_finales[-1] += f" ({color})"
            elif "(" in lineas_finales[-1]:
                lineas_finales[-1] = lineas_finales[-1].rstrip(")") + f" - {color})"
            else:
                lineas_finales[-1] += f" ({color})"
            continue

        # CONDICIÓN 1: Sumar SOLO si el número tiene un $ pegado al final
        # Ejemplo: "128 = 600$" -> El 128 no cambia, el 600 pasa a 650.
        limpia = re.sub(r'(\d+)\$', lambda m: f"{int(m.group(1)) + plus}$", limpia)
        
        # Limpieza de iconos
        limpia = limpia.replace("*", "").replace("🔺", "").replace("🔻", "").strip()
        lineas_finales.append(limpia)
        
    return lineas_finales

def generar_con_matplotlib(datos, parte_num):
    # Definimos el alto basado en la cantidad de líneas para que no se estire
    # 0.8 pulgadas por línea es una buena proporción para letra grande
    alto_pulgadas = len(datos) * 0.8 + 2
    
    # Creamos la figura (8 pulgadas de ancho es ideal para celulares)
    fig, ax = plt.subplots(figsize=(8, alto_pulgadas), dpi=120)
    fig.patch.set_facecolor('white')
    ax.axis('off')

    # Posicionamiento vertical (de arriba hacia abajo)
    y_pos = 0.95
    salto = 1.0 / (len(datos) + 1)

    for i, linea in enumerate(datos):
        # Estilo de títulos
        es_tit = any(x in linea.upper() for x in ["IPHONE", "SAMSUNG", "ACTUALIZADA", "TESTERS", "SELLADOS"])
        
        ax.text(0.05, y_pos, linea, 
                fontsize=font_size_val, 
                fontweight='bold' if es_tit or "$" in linea else 'medium',
                color='#004a99' if es_tit else 'black',
                ha='left', va='center',
                transform=ax.transAxes,
                family='sans-serif')
        y_pos -= salto

    # Guardar a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.3)
    plt.close(fig)
    return Image.open(buf)

if st.button("🚀 GENERAR CON MATPLOTLIB"):
    if input_text:
        lineas = procesar_estricto(input_text, comision)
        
        # CORTE DE PÁGINA: 10 líneas para asegurar que la letra sea GIGANTE
        limite = 10
        partes = [lineas[i:i + limite] for i in range(0, len(lineas), limite)]
        
        for idx, parte in enumerate(partes):
            st.write(f"### Vista Previa - Parte {idx + 1}")
            img_texto = generar_con_matplotlib(parte, idx + 1)
            
            # Pegar Banner
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
            st.download_button(f"📥 Descargar Parte {idx + 1}", buf_final.getvalue(), f"lista_mpl_{idx+1}.png")
