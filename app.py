import streamlit as st
import pandas as pd
from PIL import Image
import io
import google.genai # Librería de Gemini

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(
    page_title="Josecrv Fitness Check PRO",
    page_icon="🔥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* Estilos para el modo oscuro elegante */
    .main { background-color: #0E1117; color: #FAFAFA; }
    .css-1d391kg { background-color: #1F2833; color: #FAFAFA; }
    h1, h2, h3, h4, h5, h6 { color: #FF4B4B; font-family: 'Montserrat', sans-serif; }
    .stButton>button { background-color: #FF4B4B; color: white; border-radius: 8px; font-size: 1.1em; }
    .stButton>button:hover { background-color: #FF7070; color: black; }
    .stAlert { border-radius: 8px; border-left: 5px solid #FF4B4B; background-color: #2D3A45; color: #FAFAFA; }
    .stAlert.success { border-left-color: #4CAF50; } 
    .stAlert.warning { border-left-color: #FFC107; } 
    .st-dg { background-color: #1F2833; border-radius: 8px; padding: 15px; margin-bottom: 10px; border: 1px solid #FF4B4B; }
    .css-1r6dm1s { gap: 2rem; }
    </style>
""", unsafe_allow_html=True)


# --- FUNCIÓN DE ANÁLISIS REAL CON GEMINI ---

def analyze_physique_with_gemini(uploaded_file):
    """Llama a la API de Gemini para analizar la imagen."""
    
    try:
        # Intenta obtener la clave de Streamlit Secrets
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        return "❌ ERROR: Clave GEMINI_API_KEY no encontrada. Configúrala en 'Edit Secrets' de Streamlit Cloud."

    try:
        client = google.genai.Client(api_key=api_key)
        model = "gemini-2.5-flash"
    except Exception as e:
        return f"❌ ERROR al inicializar cliente Gemini: {e}"

    try:
        image = Image.open(uploaded_file)
    except Exception as e:
        return f"❌ ERROR al cargar la imagen: {e}"

    # Prompt Detallado para obtener un análisis de fitness
    prompt = """
    Eres un entrenador personal y analista de físico experto. Analiza la imagen deportiva. Genera una respuesta SÓLO en formato Markdown, con los siguientes encabezados, siendo muy específico:

    ### 🧠 Evaluación Detallada del Físico
    - Estimación de % Grasa Corporal (Ej: ~15%):
    - Índice de Simetría (Ej: 8.5/10):
    - Estimación de Masa Muscular (Ej: Nivel intermedio-avanzado):

    ### 🟢 Puntos Fuertes Detectados
    - Menciona al menos 3 grupos musculares o aspectos estéticos fuertes.

    ### 🔴 Áreas de Oportunidad (Mejora)
    - Menciona al menos 3 grupos musculares que necesiten mayor volumen o desarrollo.

    ### 🎯 Recomendaciones de Entrenamiento
    - Ofrece 3 sugerencias específicas de entrenamiento basadas en las áreas de oportunidad.
    """

    with st.spinner("🧠 Analizando el físico con Gemini Pro Vision..."):
        try:
            response = client.models.generate_content(
                model=model,
                contents=[image, prompt]
            )
            return response.text
        except Exception as e:
            return f"❌ ERROR de la API de Gemini: {e}. Revisa tu clave y cuota."


# --- HEADER Y CÁLCULOS (Código Robusto) ---

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
    activity = st.select_slider(
        "Nivel de Actividad Semanal", 
        options=["Sedentario", "Ligero (1-2 veces)", "Moderado (3-4 veces)", "Activo (5-6 veces)", "Atleta (Diario)"]
    )
    
    goal = st.radio(
        "¿Cuál es tu Objetivo Principal?",
        ["Definición (Perder Grasa)", "Mantenimiento Corporal", "Volumen (Ganar Músculo)"]
    )

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


# Columna 2: Análisis de IA
with col2:
    st.subheader("📸 Análisis Físico por Inteligencia Artificial")
    st.info("⚠️ **¡REAL!** Este análisis usa la API de Gemini para ver y evaluar la foto.")
    st.markdown("Sube una imagen de cuerpo completo para la evaluación.")
    
    uploaded = st.file_uploader("Sube tu foto aquí (JPG, PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded:
        st.image(uploaded, caption="Tu imagen cargada", use_column_width=True)
        
        if st.button("🚀 INICIAR ANÁLISIS REAL DE IA"):
            st.session_state['ai_result'] = None
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
    Si te gusta la aplicación y el análisis de la IA te ha sido útil,
    considera una pequeña donación para ayudar a cubrir los costos de la API y el desarrollo.
    </p>
""", unsafe_allow_html=True)

# Código HTML del botón de PayPal
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


st.caption("Josecrv90 Fitness Check PRO © 2025 - Impulsado por IA y Ciencia. Gracias por tu apoyo.")

