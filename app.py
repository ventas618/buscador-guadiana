import streamlit as st
import pandas as pd
import urllib.parse

# Configuración de la página
st.set_page_config(
    page_title="Cotizador - Materiales y Perfiles del Guadiana",
    page_icon="🏗️",
    layout="wide"
)

# Inicializar el carrito de cotización en la sesión si no existe
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# Encabezado principal
st.title("🏗️ Materiales y Perfiles del Guadiana")
st.subheader("Buscador de Productos y Generador de Cotizaciones")
st.write("Busca tus materiales, agrégalos a tu lista y envía tu pedido por WhatsApp para recibir tu presupuesto de inmediato.")

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
        
        # --- SECCIÓN 1: BUSCADOR Y SELECCIÓN ---
        st.markdown("### 🔍 1. Busca y Selecciona tus Materiales")
        
        # Barra de búsqueda reactiva
        busqueda = st.text_input(
            "Escribe el producto, medida o clave:",
            placeholder="Ejemplo: PTR, Viga, Tubo, 4x4...",
            key="campo_busqueda"
        )
        
        # Filtrado de datos
        if busqueda:
            termino = busqueda.lower()
            df_filtrado = df[
                df['CLAVE'].str.lower().str.contains(termino) |
                df['PRODUCTO'].str.lower().str.contains(termino) |
                df['MEDIDA'].str.lower().str.contains(termino)
            ]
        else:
            df_filtrado = df.head(10) # Mostrar 10 productos sugeridos al inicio
            
        if not df_filtrado.empty:
            # Creamos una lista de textos amigables para el selector desplegable
            opciones_productos = []
            mapa_productos = {}
            
            for idx, row in df_filtrado.iterrows():
                texto_mostrar = f"[{row['CLAVE']}] {row['PRODUCTO']} - {row['MEDIDA']}"
                opciones_productos.append(texto_mostrar)
                mapa_productos[texto_mostrar] = row
            
            # Selector interactivo que se actualiza según lo que escribe el cliente
            producto_seleccionado = st.selectbox(
                "Selecciona el material exacto de la lista desplegable:",
                options=opciones_productos,
                index=0 if busqueda else None,
                placeholder="Haz clic aquí para elegir..."
            )
            
            # Controles para agregar cantidad
            if producto_seleccionado:
                prod_data = mapa_productos[producto_seleccionado]
                
                col_cant, col_btn = st.columns([1, 2])
                with col_cant:
                    cantidad = st.number_input("Cantidad (Pzas/Tramos):", min_value=1, value=1, step=1)
                with col_btn:
                    st.write("") # Espacio estético
                    st.write("")
                    if st.button("➕ Agregar a mi Lista", use_container_width=True):
                        # Revisar si el producto ya estaba en el carrito para sumar la cantidad
                        existe = False
                        for item in st.session_state.carrito:
                            if item['CLAVE'] == prod_data['CLAVE']:
                                item['CANTIDAD'] += cantidad
                                existe = True
                                break
                        
                        if not existe:
                            st.session_state.carrito.append({
                                'CLAVE': prod_data['CLAVE'],
                                'PRODUCTO': prod_data['PRODUCTO'],
                                'MEDIDA': prod_data['MEDIDA'],
                                'CANTIDAD': cantidad
                            })
                        st.toast(f"¡Agregado: {cantidad} pza(s) de {prod_data['PRODUCTO']}!", icon="✅")
        else:
            st.warning("No se encontraron productos con ese criterio de búsqueda.")

        # --- SECCIÓN 2: EL CARRITO DE COTIZACIÓN ---
        st.divider()
        st.markdown("### 📋 2. Tu Lista de Cotización")
        
        if st.session_state.carrito:
            # Convertir el carrito actual en un DataFrame para mostrarlo estético
            df_carrito = pd.DataFrame(st.session_state.carrito)
            
            # Reordenar columnas para el cliente
            df_carrito = df_carrito[['CANTIDAD', 'PRODUCTO', 'MEDIDA', 'CLAVE']]
            
            # Mostrar la tabla del pedido actual
            st.dataframe(df_carrito, use_container_width=True, hide_index=True)
            
            # Botón para vaciar la lista si se equivocan
            if st.button("🗑️ Vaciar Lista"):
                st.session_state.carrito = []
                st.rerun()
            
            # --- SECCIÓN 3: ENVÍO A WHATSAPP ---
            st.markdown("### 📲 3. Enviar Pedido")
            
            # Construir el mensaje de texto para WhatsApp
            mensaje_wa = "*SOLICITUD DE COTIZACIÓN - MATERIALES DEL GUADIANA*\n"
            mensaje_wa += "Hola, me gustaría cotizar la siguiente lista de materiales:\n\n"
            
            for item in st.session_state.carrito:
                mensaje_wa += f"• *{item['CANTIDAD']} pza(s)* - {item['PRODUCTO']} ({item['MEDIDA']}) - [Ref: {item['CLAVE']}]\n"
            
            mensaje_wa += "\nQuedo atento a los precios y existencias. ¡Gracias!"
            
            # Codificar el texto para que sea compatible con un enlace web (caracteres especiales, espacios, etc.)
            mensaje_codificado = urllib.parse.quote(mensaje_wa)
            
            # REEMPLAZA ESTE NÚMERO POR EL DE TU NEGOCIO (con código de país, ej: 52 para México)
            numero_whatsapp = "526184421022" 
            
            url_final = f"https://wa.me/{numero_whatsapp}?text={mensaje_codificado}"
            
            st.write("Una vez que revises que tu lista está completa, haz clic abajo:")
            st.link_button("🟢 ENVIAR MI PEDIDO POR WHATSAPP", url_final, use_container_width=True)
            
      
