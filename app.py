import streamlit as st
import re
import matplotlib.pyplot as plt
from PIL import Image
import io
import gc
from datetime import datetime

st.set_page_config(page_title="Lista Matplotlib PRO", layout="wide")

st.sidebar.header("🎨 Ajustes de Tipografía")
comision = st.sidebar.number_input("Suma fija ($)", value=50)
font_size_val = st.sidebar.slider("Tamaño de Letra", 15, 60, 35)

accion_escalas = st.sidebar.radio(
    "Líneas de cantidad 💰(3x.../5x...):",
    ["Eliminar línea por completo", "Sumar $50 a cada escala"]
)

st.title("📲 Generador de Lista PRO")

uploaded_file = st.file_uploader("1. Sube tu Banner", type=["jpg", "png"])
if uploaded_file:
    with Image.open(uploaded_file) as img_temp:
        if img_temp.size[0] > 1000:
            ancho_fijo = 1000
            alto_prop = int(img_temp.size[1] * (ancho_fijo / img_temp.size[0]))
            st.session_state.banner_mpl = img_temp.resize((ancho_fijo, alto_prop), Image.Resampling.LANCZOS).convert("RGB")
        else:
            st.session_state.banner_mpl = img_temp.convert("RGB")

input_text = st.text_area("2. Pega tu lista:", height=250)

def procesar_estricto(texto, plus, modo_escalas):
    lineas_finales = []
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    lineas_finales.append(f"LISTA ACTUALIZADA ({fecha_hoy})")
    
    # Palabras basura y separadores
    basura = [
        "garantia", "11 - 18hs", "nüñez", "lunes a viernes", "lun a vier", 
        "encomiendas", "usd/pesos", "usdt", "bajamos", "caba"
    ]
    
    for l in texto.split('\n'):
        limpia = l.strip()
        
        # 1. Eliminar líneas vacías, textos basura o líneas divisorias
        if not limpia or any(b in limpia.lower() for b in basura):
            continue
        if any(c in limpia for c in ["___", "▔▔▔", "……", "....", "----", "————"]):
            continue

        # 2. Manejo de líneas de escala de cantidad (💰)
        if "💰" in limpia or ("x" in limpia and "/" in limpia and ")" in limpia):
            if modo_escalas == "Eliminar línea por completo":
                continue
            else:
                # Suma el valor a números que sigan a una 'x' dentro de la escala
                limpia = re.sub(r'(\d+x)(\d+)', lambda m: f"{m.group(1)}{int(m.group(2)) + plus}", limpia)
                lineas_finales.append(limpia)
                continue

        # 3. Formatear encabezados de categoría (ej: |🔸NUEVOS SELLADOS🔸|)
        if limpia.startswith("|") and limpia.endswith("|"):
            limpia = limpia.replace("|", "").replace("🔸", "").strip()

        # 4. Agrupar líneas secundarias de colores y batería con el producto superior
        if (limpia.startswith("-") or limpia.startswith("🔋")) and lineas_finales:
            lineas_finales[-1] += f"  {limpia}"
            continue

        # 5. Normalizar '1x' frente al precio (ej: 1x450$ -> 450$)
        limpia = re.sub(r'1x\s*(\d+)', r'\1', limpia)

        # 6. Sumar la comisión únicamente a valores con el signo '$' inmediatamente después
        limpia = re.sub(r'(\d+)\$', lambda m: f"{int(m.group(1)) + plus}$", limpia)
        
        # 7. Limpieza de caracteres de formato
        limpia = limpia.replace("*", "").replace("📌", "").replace("_", "").strip()
        
        lineas_finales.append(limpia)
        
    return lineas_finales

def generar_con_matplotlib(datos, limite_fijo=10):
    alto_pulgadas = limite_fijo * 0.8 + 1
    fig, ax = plt.subplots(figsize=(9, alto_pulgadas), dpi=120)
    fig.patch.set_facecolor('white')
    ax.axis('off')

    ax.set_ylim(0, 1)
    
    espacio_entre_lineas = 1.0 / (limite_fijo + 1)
    y_pos = 0.95 

    for linea in datos:
        es_tit = any(x in linea.upper() for x in ["IPHONE", "SAMSUNG", "ACTUALIZADA", "TESTERS", "SELLADOS", "AIRPODS", "IPAD", "CARGADOR"])
        
        ax.text(0.05, y_pos, linea, 
                fontsize=font_size_val, 
                fontweight='bold',
                color='#004a99' if es_tit else 'black',
                ha='left', va='center',
                transform=ax.transAxes,
                family='sans-serif')
        y_pos -= espacio_entre_lineas

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.4)
    
    plt.close(fig)
    plt.clf()
    gc.collect()
    
    return Image.open(buf)

if st.button("🚀 GENERAR LISTAS IDÉNTICAS"):
    if input_text:
        lineas = procesar_estricto(input_text, comision, accion_escalas)
        
        limite_corte = 10
        partes = [lineas[i:i + limite_corte] for i in range(0, len(lineas), limite_corte)]
        
        for idx, parte in enumerate(partes):
            st.write(f"### Vista Previa - Parte {idx + 1}")
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
            gc.collect()
