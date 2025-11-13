import streamlit as st
import pandas as pd
from PIL import Image
import io
import json
import google.genai 
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(
    page_title="Josecrv Fitness Check PRO",
    page_icon="🔥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS para el modo oscuro (con fix para métricas)
st.markdown("""
    <style>
    /* Fondo general */
    .main { background-color: #0E1117; color: #FAFAFA; }
    /* Sidebar */
    .css-1d391kg { background-color: #1F2833; color: #FAFAFA; }
    /* Títulos principales */
    h1, h2, h3, h4, h5, h6 { color: #FF4B4B; font-family: 'Montserrat', sans-serif; }
    /* Botones y Alerts */
    .stButton>button { background-color: #FF4B4B; color: white; border-radius: 8px; font-size: 1.1em; }
    .stButton>button:hover { background-color: #FF7070; color: black; }
    .stAlert { border-radius: 8px; border-left: 5px solid #FF4B4B; background-color: #2D3A45; color: #FAFAFA; }

    /* FIX: Estilo para métricos y tablas */
    .st-dg { 
        background-color: #1F2833;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #FF4B4B;
        color: #FAFAFA !important;
    }
    .st-emotion-cache-12t9kbi > div > div:nth-child(2) > div,
    .st-emotion-cache-12t9kbi p,
    .st-emotion-cache-1100w0f p,
    .stTable {
        color: #FAFAFA !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- FUNCIONES DE CLOUD ---

def analyze_physique_with_gemini(uploaded_file):
    """Llama a la API de Gemini para analizar la imagen."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        return "❌ ERROR: Clave GEMINI_API_KEY no encontrada."

    try:
        client = google.genai.Client(api_key=api_key)
        model = "gemini-2.5-flash"
    except Exception as e:
        return f"❌ ERROR al inicializar cliente Gemini: {e}"

    try:
        # Asegúrate de que el puntero esté al inicio para Gemini
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
    except Exception as e:
        return f"❌ ERROR al cargar la imagen: {e}"

    # Prompt Detallado
    prompt = "Eres un entrenador personal y analista de físico experto. Analiza la imagen deportiva. Genera una respuesta SÓLO en formato Markdown, con los siguientes encabezados: ### 🧠 Evaluación Detallada del Físico, ### 🟢 Puntos Fuertes Detectados, ### 🔴 Áreas de Oportunidad (Mejora), ### 🎯 Recomendaciones de Entrenamiento. Sé muy específico en el análisis."
    
    with st.spinner("🧠 Analizando el físico con Gemini Pro Vision..."):
        try:
            response = client.models.generate_content(
                model=model,
                contents=[image, prompt]
            )
            return response.text
        except Exception as e:
            return f"❌ ERROR de la API de Gemini: {e}. Revisa tu clave y cuota."


def upload_file_to_drive(uploaded_file, user_weight):
    """Sube el archivo cargado a la carpeta especificada en Google Drive."""
    try:
        folder_id = st.secrets["GDRIVE_FOLDER_ID"]
        service_account_info = json.loads(st.secrets["GDRIVE_SERVICE_ACCOUNT"])
        
        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=creds)
    except KeyError:
        return "❌ Error: Las claves de Google Drive no están en Streamlit Secrets."
    except Exception as e:
        return f"❌ Error de Autenticación de Drive: {e}"

    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"Foto_Progreso_{timestamp}_{int(user_weight)}kg_{uploaded_file.name}"
    
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    
    # Reinicia el puntero del archivo para que la API pueda leerlo
    uploaded_file.seek(0)
    media = MediaIoBaseUpload(
        io.BytesIO(uploaded_file.read()),
        mimetype=uploaded_file.type
    )

    try:
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return "✅ Foto guardada exitosamente" # Mensaje de éxito interno
    except Exception as e:
        return f"❌ Error al subir a Drive: {e}. Revisa los permisos de la Cuenta de Servicio."


# --- HEADER Y CÁLCULOS (Lógica de Macros) ---

st.title("🔥 Josecrv Fitness Check PRO")
st.markdown("<p style='font-size: 1.2em; color: #BBBBBB;'>Tu compañero inteligente para optimizar tu nutrición y analizar tu físico con precisión.</p>", unsafe_allow_html=True)
st.markdown("---")

# SIDEBAR: ENTRADA DE DATOS DEL USUARIO
with st.sidebar:
    st.header("👤 Tus Datos Biométricos")
    gender = st.selectbox("Género", ["Hombre", "Mujer"])
    age = st.number_input("Edad (años)", min_value=15, max_value=90, value=25)
    height = st.number_input("Altura (cm)", min_value=120, max_value=230, value=175)
    weight = st.number_input("Peso (kg)", min_value=40, max_value=180, value=75)
    
    st.subheader("🏋️ Nivel de Actividad y Objetivo")
    activity = st.select_slider("Nivel de Actividad Semanal", options=["Sedentario", "Ligero (1-2 veces)", "Moderado (3-4 veces)", "Activo (5-6 veces)", "Atleta (Diario)"])
    
    goal = st.radio("¿Cuál es tu Objetivo Principal?", ["Definición (Perder Grasa)", "Mantenimiento Corporal", "Volumen (Ganar Músculo)"])

# LÓGICA DE CÁLCULO (Mifflin-St Jeor)
if gender == "Hombre": bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
else: bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
act_map = { "Sedentario": 1.2, "Ligero (1-2 veces)": 1.375, "Moderado (3-4 veces)": 1.55, "Activo (5-6 veces)": 1.725, "Atleta (Diario)": 1.9 }
tdee = bmr * act_map[activity]
if "Definición" in goal: calories = tdee - 500; prot_factor = 2.2 
elif "Volumen" in goal: calories = tdee + 350; prot_factor = 1.8
else: calories = tdee; prot_factor = 1.6
prot_g = weight * prot_factor
fat_g = weight * 0.9 
carb_g = (calories - ((prot_g * 4) + (fat_g * 9))) / 4
carb_g = max(0, carb_g) 


# --- INTERFAZ PRINCIPAL ---

col1, col2 = st.columns([1, 1.3]) 

# Columna 1: Resultados Nutricionales
with col1:
    st.subheader("📊 Tu Plan Nutricional Personalizado")
    st.metric(label="Calorías Diarias Recomendadas", value=f"{int(calories)} kcal", delta=goal)
    df_macros = pd.DataFrame({
        "Macronutriente": ["Proteína 🥩", "Grasas 🥑", "Carbohidratos 🍚"],
        "Gramos / Día": [f"{int(prot_g)}g", f"{int(fat_g)}g", f"{int(carb_g)}g"],
        "Calorías Aportadas": [f"{int(prot_g*4)}", f"{int(fat_g*9)}", f"{int(carb_g*4)}"]
    })
    st.table(df_macros)
    with st.expander("📚 Detalles Científicos y Recomendaciones"):
        st.info(f"Tu Tasa Metabólica Basal (TMB) es de **{int(bmr)} kcal**.")


# Columna 2: Análisis de IA y Subida (DISCRETO)
with col2:
    st.subheader("📸 Análisis Físico por Inteligencia Artificial")
    
    # Mensaje SUTIL, sin mencionar Google Drive
    st.info("⚠️ **Análisis REAL:** La imagen será procesada por IA para seguimiento y evaluación.")
    
    uploaded = st.file_uploader("Sube tu foto aquí (JPG, PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded:
        st.image(uploaded, caption="Tu imagen cargada", use_column_width=True)
        
        if st.button("🚀 INICIAR ANÁLISIS DE FÍSICO Y SEGUIMIENTO"):
            
            # 1. Subir a Google Drive (Función ejecutándose en el backend)
            upload_status = upload_file_to_drive(uploaded, weight)
            
            # Mensaje de éxito discreto basado en el estado de la subida
            if "✅ Foto guardada exitosamente" in upload_status:
                 st.success("✅ Imagen registrada para tu seguimiento de progreso. Iniciando análisis de IA...")
            else:
                 st.warning("⚠️ Hubo un problema al registrar la foto para seguimiento, pero el análisis de IA continuará.")
            
            # 2. Ejecutar la IA
            st.session_state['ai_result'] = None
            # Tienes que reiniciar el puntero del archivo ANTES de pasarlo a Gemini, ya que Drive lo leyó
            uploaded.seek(0) 
            ai_output = analyze_physique_with_gemini(uploaded)
            st.session_state['ai_result'] = ai_output
    
    if 'ai_result' in st.session_state and st.session_state['ai_result'] is not None:
        st.markdown("---")
        st.write("### Resultados de la IA:")
        st.markdown(st.session_state['ai_result'])
        st.markdown("---")
        st.caption("Respuesta generada por Google Gemini Pro Vision.")


# --- SECCIÓN DE DONACIONES (BOTÓN DE PAYPAL) ---

st.markdown("---")
st.markdown("## 🎉 Apoya el Desarrollo de la App")
st.markdown("""
    <p style='font-size: 1.1em; color: #BBBBBB;'>
    Si te gusta la aplicación, considera una pequeña donación para cubrir los costos de la API y el desarrollo.
    </p>
""", unsafe_allow_html=True)

paypal_button_html = """
<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
    <input type="hidden" name="cmd" value="_donations" />
    <input type="hidden" name="business" value="josecrv90@gmail.com" />
    <input type="hidden" name="currency_code" value="EUR" />
    <input type="image" src="https://www.paypalobjects.com/es_ES/ES/i/btn/btn_donate_LG.gif" border="0" 
           name="submit" title="PayPal - The safer, easier way to pay online!" 
           alt="Donar con el botón PayPal" style="width: 150px; height: auto;" />
</form>
"""
st.markdown(paypal_button_html, unsafe_allow_html=True)


st.caption("Josecrv Fitness Check PRO © 2024 - Impulsado por IA y Ciencia. Gracias por tu apoyo.")