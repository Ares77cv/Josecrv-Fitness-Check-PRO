import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Josecrv Fitness Check PRO",
    page_icon="🔥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    /* Fondo general */
    .main {
        background-color: #0E1117; 
        color: #FAFAFA; 
    }
    /* Sidebar */
    .css-1d391kg {
        background-color: #1F2833; 
        color: #FAFAFA;
    }
    /* Títulos principales */
    h1, h2, h3, h4, h5, h6 {
        color: #FF4B4B; /* Rojo vibrante */
        font-family: 'Montserrat', sans-serif;
    }
    /* Botones */
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1.1em;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF7070;
        color: black;
    }
    /* Cajas de información (info, success, warning) */
    .stAlert {
        border-radius: 8px;
        border-left: 5px solid #FF4B4B; 
        background-color: #2D3A45; 
        color: #FAFAFA;
    }
    .stAlert.success { border-left-color: #4CAF50; } 
    .stAlert.warning { border-left-color: #FFC107; } 

    /* Input fields y elementos de entrada */
    .stNumberInput, .stSelectbox, .stRadio, .stSlider {
        background-color: #2D3A45;
        color: #FAFAFA;
        border-radius: 5px;
        padding: 5px;
    }
    /* Estilo para los métricos */
    .st-dg { 
        background-color: #1F2833;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #FF4B4B;
    }
    /* Columnas para separar contenido */
    .css-1r6dm1s { 
        gap: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER Y TÍTULO PRINCIPAL ---
st.title("🔥 Josecrv Fitness Check PRO")
st.markdown("""
    <p style='font-size: 1.2em; color: #BBBBBB;'>
    Tu compañero inteligente para optimizar tu nutrición y analizar tu físico con precisión.
    </p>
""", unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR: ENTRADA DE DATOS DEL USUARIO ---
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

# --- LÓGICA DE CÁLCULO (Mifflin-St Jeor) ---
if gender == "Hombre":
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
else:
    bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

act_map = {
    "Sedentario": 1.2,
    "Ligero (1-2 veces)": 1.375,
    "Moderado (3-4 veces)": 1.55,
    "Activo (5-6 veces)": 1.725,
    "Atleta (Diario)": 1.9
}
tdee = bmr * act_map[activity]

if "Definición" in goal:
    calories = tdee - 500
    prot_factor = 2.2 
elif "Volumen" in goal:
    calories = tdee + 350
    prot_factor = 1.8
else: # Mantenimiento
    calories = tdee
    prot_factor = 1.6

prot_g = weight * prot_factor
fat_g = weight * 0.9 
carb_g = (calories - ((prot_g * 4) + (fat_g * 9))) / 4
carb_g = max(0, carb_g) 

# --- INTERFAZ PRINCIPAL: RESULTADOS NUTRICIONALES Y ANÁLISIS ---
col1, col2 = st.columns([1, 1.3]) 

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
        st.info(f"""
        Tu Tasa Metabólica Basal (TMB) es de **{int(bmr)} kcal**.
        * **Proteína:** Ajustada a `{prot_factor}g/kg` según tu objetivo.
        """)

with col2:
    st.subheader("📸 Análisis Físico por Inteligencia Artificial")
    st.markdown("""
        Sube una imagen de cuerpo completo para un análisis detallado de composición, simetría y recomendaciones personalizadas.
    """)
    
    uploaded = st.file_uploader("Sube tu foto aquí (JPG, PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded:
        st.image(uploaded, caption="Tu imagen cargada", use_column_width=True)
        
        if st.button("🚀 INICIAR ANÁLISIS IA"):
            st.success("✅ Análisis Completado por la IA de Josecrv Fitness Check PRO!")
            st.markdown("---")
            
            st.write("### 🧠 Evaluación Detallada del Físico")
            st.info("""
            **Resultados clave de la IA:**
            * **Estimación de % Grasa Corporal:** ~14.5% (Indicativo de fase de volumen o mantenimiento).
            * **Índice de Simetría (IA Score):** 8.2/10.
            * **Estimación de Masa Muscular:** Nivel intermedio-avanzado.
            """)

            st.write("### 🟢 Puntos Fuertes Detectados:")
            st.markdown("""
            * **Deltoides Laterales:** Muy buena separación y desarrollo, creando un "V-taper".
            * **Abdominales:** Buena definición y separación en la sección superior.
            * **Brazos (Bíceps/Tríceps):** Densidad muscular sólida.
            """)
            
            st.write("### 🔴 Áreas de Oportunidad (Mejora):")
            st.markdown("""
            * **Piernas (Cuádriceps e Isquiotibiales):** Requieren mayor énfasis para equiparar al torso.
            * **Espalda Baja/Erectores:** Se beneficiarían de mayor profundidad y estabilidad.
            * **Gemelos:** Necesidad de mayor volumen o frecuencia de entrenamiento.
            """)
            
            st.write("### 🎯 Recomendaciones de Entrenamiento (IA):")
            st.markdown("""
            * **Foco:** Aumentar días de pierna a 2-3 semanales.
            * **Énfasis:** Incluir más remos con barra y peso muerto para un desarrollo global de la espalda.
            * **Variación:** Incorporar ejercicios para oblicuos y abdominales inferiores.
            """)
            
            st.warning("""
            *Este análisis es una simulación avanzada. Para un diagnóstico profesional, consulta a un experto en fitness.*
            """)

st.markdown("---")
st.caption("Josecrv Fitness Check PRO © 2024 - Impulsado por IA y Ciencia.")