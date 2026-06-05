import streamlit as st
import pandas as pd

# Configuración de la página (Título e icono en la pestaña del navegador)
st.set_page_config(
    page_title="Inventario - Materiales y Perfiles del Guadiana",
    page_icon="🏗️",
    layout="wide"
)

# Estilos visuales personalizados (Colores oscuros/acero y diseño limpio)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTextInput font { size: 18px; }
    div.stButton > button:first-child {
        background-color: #25D366;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado principal
st.title("🏗️ Materiales y Perfiles del Guadiana")
st.subheader("Buscador de Productos e Inventario en Tiempo Real")
st.write("Escribe lo que necesitas para verificar si lo tenemos disponible.")

# Función para cargar los datos de Excel de forma eficiente
@st.cache_data
def cargar_datos():
    try:
        # Lee el archivo Excel. Asegúrate de que se llame así en tu repositorio.
        df = pd.read_excel("inventario.xlsx")
        # Limpieza básica: quitar espacios en blanco en los nombres de las columnas
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error("Error al cargar el archivo 'inventario.xlsx'. Verifica que el nombre sea correcto.")
        return None

df = cargar_datos()

if df is not None:
    # Asegurar que las columnas requeridas existan en el Excel
    columnas_requeridas = ['CLAVE', 'PRODUCTO', 'MEDIDA']
    if all(col in df.columns for col in columnas_requeridas):
        
        # Barra de búsqueda centralizada
        busqueda = st.text_input(
            "🔍 Busca por producto, medida (ej. 2x2, 1/4) o clave:",
            placeholder="Ejemplo: PTR, Viga, Tubo, 4x4..."
        )
        
        # Filtrado inteligente
        if busqueda:
            # Convertimos todo a texto y minúsculas para que la búsqueda sea flexible
            termino = busqueda.lower()
            resultado = df[
                df['CLAVE'].astype(str).str.lower().str.contains(termino) |
                df['PRODUCTO'].astype(str).str.lower().str.contains(termino) |
                df['MEDIDA'].astype(str).str.lower().str.contains(termino)
            ]
            
            # Mostrar resultados
            st.write(f"📋 Se encontraron **{len(resultado)}** productos coincidentes:")
            st.dataframe(resultado[['CLAVE', 'PRODUCTO', 'MEDIDA']], use_container_width=True, hide_index=True)
            
        else:
            # Vista inicial cuando el buscador está vacío
            st.write("💡 Mostrando una lista general de materiales disponibles:")
            st.dataframe(df[['CLAVE', 'PRODUCTO', 'MEDIDA']].head(15), use_container_width=True, hide_index=True)
            
    else:
        st.error(f"El archivo Excel debe contener exactamente las columnas: {', '.join(columnas_requeridas)}")



# Sección de contacto fija abajo
st.divider()
col1, col2 = st.columns([2, 1])
with col1:
    st.write("¿Encontraste lo que buscabas o necesitas una medida especial?")
with col2:
    # Enlace directo a tu WhatsApp (Cambia el número por el tuyo)
    st.link_button("📲 Cotizar Material por WhatsApp", "https://wa.me/526184421022?text=Hola,%20quiero%20cotizar%20unos%20materiales")
