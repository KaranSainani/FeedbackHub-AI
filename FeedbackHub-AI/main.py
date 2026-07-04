"""
FeedbackHub AI - Orquestador de Interfaz
----------------------------------------------------------
Este archivo sirve como el punto de entrada de la aplicación Streamlit. 
Su función principal es renderizar e interactuar con la interfaz de usuario (UI).

Responsabilidades principales:
1. Orquestación del Dashboard B2B (Business-to-Business) y gestión de pestañas (Métricas y Análisis Manual).
2. Manejo reactivo de los filtros de búsqueda por texto y valoración (estrellas).
3. Control del estado de la sesión (st.session_state) para el almacenamiento temporal de datos.
4. Gestión de entradas/salidas de datos: Carga Masiva (CSV), Inserción Manual (Formulario) y Eliminación.
5. Renderizado de componentes visuales avanzados (Tarjetas KPI y Gráficos Estadísticos con Pandas).

© Karan Sainani 2026
"""
# ------- IMPORTACIONES NECESARIAS --------

# Módulo nativo de Python para interacción con el sistema
import os
# Framework principal
import streamlit as st
import json
from datetime import datetime
# Libreria estandar para datos
import pandas as pd
import csv
from io import StringIO
from src.ai_handler import analizar_resena_con_gemini

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="FeedbackHub AI", page_icon="📊", layout="wide")

# 2. GESTIÓN DEL ESTADO DE LOS DATOS (Memoria intermedia de la app)

# Comprobamos si la clave (datos_resenas) no existe aún en la memoria persistente de la aplicación (st.session_state)
if "datos_resenas" not in st.session_state:

    # Construimos  la ruta hacia el archivo de datos, uniendo la carpeta "src" con el nombre del archivo "mock_data.json"
    ruta_archivo = os.path.join("src", "mock_data.json")

    # Abrimos el JSON en modo lectura
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        # Toma el JSON, lo convierte en una lista  de diccionarios y lo almacena permanentemente dentro de la memoria de la sesión
        st.session_state.datos_resenas = json.load(archivo)

# 3. BARRA LATERAL (SIDEBAR) - FILTROS AVANZADOS
st.sidebar.header("🎯 Filtros de Búsqueda")

busqueda_texto = st.sidebar.text_input("🔍 Buscar por palabra clave:", placeholder="Ej: comida, lento...")
opciones_estrellas = ["Todas", "5 ⭐", "4 ⭐", "3 ⭐", "2 ⭐", "1 ⭐"]
filtro_estrellas = st.sidebar.selectbox("⭐ Filtrar por Valoración:", opciones_estrellas)

# --- SECCIÓN A: CARGA MASIVA DE ARCHIVOS ---
st.sidebar.markdown("---")
st.sidebar.header("📂 Carga Masiva de Reseñas")
st.sidebar.write("Sube un archivo CSV para cargar el historial de golpe:")

archivo_subido = st.sidebar.file_uploader("Arrastra tu archivo CSV aquí:", type=["csv"])

# Si el usuario subió un archivo
if archivo_subido is not None:
    # Bloque de control de excepciones (try-except)
    try:
        # Lee el fichero CSV y lo transforma en un DataFrame (Tabla indexada con filas y columnas)
        df_subido = pd.read_csv(archivo_subido)

        # Conjunto (set) con los nombres exactos de las 4 columnas del modelo de datos
        columnas_requeridas = {"fecha", "cliente", "valoracion", "comentario"}
        
        # Comprobamos si todas columnas requeridas existen dentro del archivo subido
        if columnas_requeridas.issubset(df_subido.columns):

            # Convertimos el DataFrame en una lista de diccionarios:
            # {"fecha": "...", "cliente": "...", ...}
            nuevos_datos = df_subido.to_dict(orient="records")

            # Recorremos una a una todas las nuevas reseñas extraídas del fichero
            for fila in nuevos_datos:

                # ID númerico único para cada reseña manteniendo la integridad referencial de los datos
                fila["id"] = len(st.session_state.datos_resenas) + 1

                # Vemos si la columna fecha viene vacia, no existe o contiene un valor nulo (NaN) en esa fila específica
                if "fecha" not in fila or pd.isna(fila["fecha"]):

                    # El sistema rescata el día de hoy y lo inyecta formateado en texto plano (ej: 2026-06-30)
                    fila["fecha"] = datetime.today().strftime('%Y-%m-%d')
                

                # Para controlar que no se suban reseñas repetidas
                # Creamos una variable para controlar si la reseña ya existe
                # Empezamos asumiendo que la reseña SÍ es nueva
                es_nueva = True
                
                # Revisamos una a una las reseñas que ya tenemos guardadas
                for resena_actual in st.session_state.datos_resenas:
                    if resena_actual["comentario"] == fila["comentario"]:
                        # Si la encontramos repetida, ya NO es nueva
                        es_nueva = False
                        break # Paramos de buscar
                
                # SI ES NUEVA, LA INSERTAMOS
                if es_nueva:
                    # Insertamos arriba del todo de la tabla (posición, elemento)
                    st.session_state.datos_resenas.insert(0, fila)

                
                # OTRA FORMA MAS PRO PARA EL FUTURO
                #if not any(r["comentario"] == fila["comentario"] for r in st.session_state.datos_resenas):
                    #st.session_state.datos_resenas.insert(0, fila)
                
            st.toast("📂 ¡Historial masivo cargado con éxito!", icon="🚀")
        else:
            st.sidebar.error("⚠️ El CSV debe tener las columnas: fecha, cliente, valoracion, comentario")
    except Exception as e:
        st.sidebar.error(f"❌ Error al procesar el archivo: {e}")

# --- SECCIÓN B: FORMULARIO DE INSERCIÓN MANUAL ---
st.sidebar.markdown("---")
st.sidebar.header("✍️ Registrar Nueva Reseña")
st.sidebar.write("Añade una reseña de forma individual:")

# Contenedor de formulario especial en la barra lateral usando un gestor de contexto (with)
with st.sidebar.form(key="formulario_resena", clear_on_submit=True):

    # Caja de entrada
    nuevo_cliente = st.text_input("Nombre del Cliente:", placeholder="Ej: María García")

    # Barra de deslizamiento interactiva
    nueva_valoracion = st.slider("Valoración:", min_value=1, max_value=5, value=5, step=1)

    # Cuadro de texto grande de varias lineas
    nuevo_comentario = st.text_area("Comentario de la reseña:", placeholder="Escribe aquí lo que dijo el cliente...")
    
    # Botón de envío del formulario
    boton_guardar = st.form_submit_button(label="➕ Guardar en el Dashboard")

# Vemos si el usuario ha hecho clic en el botón de enviar el formulario
if boton_guardar:

    # Verificamos que tanto el nombre como el comentario contengan texto real y no estén vacíos. 

    # .strip() -> Elimina los espacios en blanco al principio y al final de un texto, como el .trim() de java.
    if nuevo_cliente.strip() != "" and nuevo_comentario.strip() != "":

        # Diccionario (Objeto clave-valor)
        nueva_fila = {

            # ID único
            "id": len(st.session_state.datos_resenas) + 1,
            # Fecha
            "fecha": datetime.today().strftime('%Y-%m-%d'),
            # Texto que el usuario escribió en las cajas del formulario
            "cliente": nuevo_cliente,
            # Número entero (del 1 al 5)
            "valoracion": nueva_valoracion,
            # Texto
            "comentario": nuevo_comentario
        }

        # Introducimos este diccionario en la primera posición
        st.session_state.datos_resenas.insert(0, nueva_fila)
        st.toast("✅ ¡Reseña añadida con éxito!", icon="🎉")
    else:
        st.sidebar.error("⚠️ Por favor, rellena el nombre y el comentario.")


# --- SECCIÓN C: BORRAR RESEÑA ---
st.sidebar.markdown("---")
st.sidebar.header("🗑️ Eliminar Reseña")

# Evaluamos con una condición de control si hay almenos una reseña guardada en la memoria del sistema
if len(st.session_state.datos_resenas) > 0:

    # Creamos una lista con los IDs disponibles para borrar
    # Creamos una lista vacía para guardar solo los IDs
    lista_ids = []
    
    # 2. Recorremos todas las reseñas que tenemos en memoria
    for resena in st.session_state.datos_resenas:
        # 3. Sacamos el ID de cada reseña y lo metemos en nuestra lista
        lista_ids.append(resena["id"])

    # ----------------------------------
    # OTRA FORMA MAS PRO PARA EL FUTURO
    # lista_ids = [r["id"] for r in st.session_state.datos_resenas]
    # ----------------------------------
    
    # El usuario selecciona qué ID quiere borrar
    id_a_borrar = st.sidebar.selectbox("Selecciona el ID de la reseña a eliminar:", lista_ids)
    
    boton_borrar = st.sidebar.button("🗑️ Eliminar Reseña Seleccionada", type="secondary")
    
    # Vemos si hay pulsado el botón de Borrar
    if boton_borrar:

        # Buscamos la reseña por ID y la eliminamos de la sesión
        # Recorremos todas las reseñas en memoria una por una
        for resena in st.session_state.datos_resenas:
            # Si encontramos la reseña que tiene el ID que queremos borrar...
            if resena["id"] == id_a_borrar:
                # La borramos directamente de la lista
                st.session_state.datos_resenas.remove(resena)
                # Ponemos un break para detener el bucle, porque ya la encontramos
                break

        # ---- OTRA FORMA MAS PRO PARA EL FUTURO --------
        # st.session_state.datos_resenas = [r for r in st.session_state. datos_resenas if r["id"] != id_a_borrar]
        # ------------------------------------------------

        # Notificación
        st.toast(f"🗑️ Reseña con ID {id_a_borrar} eliminada correctamente.", icon="👍")

        # Forzamos a Streamlit a reiniciar y reejecutar todo el fichero main.py
        st.rerun()

# No hay reseñas
else:
    st.sidebar.write("No hay reseñas disponibles para eliminar.")



#  ----- APLICAMOS LOS FILTROS EN TIEMPO REAL -----

# Variable auxiliar que contiene una copia de reseñas de la sesión
resenas_filtradas = st.session_state.datos_resenas


# --- FILTRO 1: BUSCADOR DE TEXTO ---
# Vemos si hay algún texto escrito por el usuario en la barra de búsqueda
if busqueda_texto:

    # Contenedor temporal
    lista_temporal_texto = []
    # Convertimos a minúsculas
    texto_buscado = busqueda_texto.lower()
    
    # Examinamos una a una todas las reseñas
    for r in resenas_filtradas:
        # Pasamos a minúsculas para que coincida siempre
        comentario_minuscula = r["comentario"].lower()
        cliente_minuscula = r["cliente"].lower()
        
        # Si la palabra está en el comentario o en el nombre del cliente...
        if texto_buscado in comentario_minuscula or texto_buscado in cliente_minuscula:

            # Tomamos la reseña entera r y la añadimos al final de nuestra lista temporal
            lista_temporal_texto.append(r)
    
    # Hemos revisado todas las reseñas del sistema, reemplazamos el contenido de la variable original por la temporal
    resenas_filtradas = lista_temporal_texto


# --- FILTRO 2: DESPLEGABLE DE ESTRELLAS ---
# Vemos si es diferente a Todas las estrellas
if filtro_estrellas != "Todas":
    # Lista temporal
    lista_temporal_estrellas = []
    
    # Cortamos el texto "5 estrellas" -> ["5", "estrellas"] y cogemos el "5"
    partes_texto = filtro_estrellas.split()
    estrellas_numero = int(partes_texto[0])
    
    # Recorremos uno a uno los diccionarios
    for r in resenas_filtradas:
        # Si la valoración de la reseña coincide con el número...
        if r["valoracion"] == estrellas_numero:

            # Añadimos esa reseña al final de nuestra lista temporal
            lista_temporal_estrellas.append(r)

    # Hemos revisado todas las reseñas del sistema, reemplazamos el contenido de la variable original por la temporal       
    resenas_filtradas = lista_temporal_estrellas


#  ------- CUERPO PRINCIPAL DE LA APLICACIÓN --------
st.title("FeedbackHub AI")
st.subheader("Plataforma B2B de Análisis de Sentimiento e Insights Automatizados")

tab1, tab2 = st.tabs(["📊 Dashboard General", "🔍 Analizar Reseña Manual"])

# PESTAÑA 1: DASHBOARD GENERAL
with tab1:
    st.write("### 📈 Indicadores Clave de Rendimiento (KPIs)")

    # 1º KPI, cantidad total de reseñas disponibles
    total_resenas = len(resenas_filtradas)
    
    # Vemos si almenos hay una reseña para hacer los cálculos matemáticos
    if total_resenas > 0:
        # Acumulador y Contador 
        suma_total_estrellas = 0
        alertas_criticas = 0
        
        # Recorremos cada reseña para extraer sus datos
        for r in resenas_filtradas:
            # Acumulamos las estrellas de todas las reseñas
            suma_total_estrellas = suma_total_estrellas + r["valoracion"]
            
            # Si la reseña es de 1 o 2 estrellas, sumamos una alerta crítica
            if r["valoracion"] <= 2:
                alertas_criticas = alertas_criticas + 1
        
        # Calculamos la media matemática dividiendo la suma entre el total
        puntuacion_media = suma_total_estrellas / total_resenas
        # --------------------------------------------------
        
        # Formateamos el texto para que muestre solo 1 decimal (F-String , Cadena de Formato)
        media_texto = f"{puntuacion_media:.1f} / 5.0 ⭐"

        # Otra forma MENOS pro
        # media_texto = str(puntuacion_media) + " / 5.0 ⭐ "

    # No hay reseñas
    else:
        # Not Available
        media_texto = "N/A"
        alertas_criticas = 0

    # Pintamos los KPIs en la pantalla
    # Tenemos 3 columnas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Volumen de Reseñas", value=total_resenas)
    with col2:
        st.metric(label="Puntuación Media", value=media_texto)
    
    with col3:
        # Decidimos qué texto de alerta mostrar según el número de quejas
        if alertas_criticas > 0:
            texto_alerta = " + Atención requerida"
        else:
            texto_alerta = None  # None significa que no se mostrará nada abajo
            
        # Dibujamos la métrica pasándole la variable ya calculada
        st.metric(
            label="Alertas Críticas (≤ 2⭐)", 
            value=alertas_criticas, 
            delta=texto_alerta,
            # La inversa del + (verde) que es rojo 
            delta_color="inverse"
        )
        
    st.markdown("---")

    # ==========================================
    # SECCIÓN DE GRÁFICOS VISUALES
    # ==========================================

    # Vemos si hay al menos una reseña
    if total_resenas > 0:
        st.write("### 📊 Análisis Visual de Tendencias")
        
        # Convertimos las reseñas filtradas a un DataFrame temporal para los gráficos
        df_graficos = pd.DataFrame(resenas_filtradas)
        
        # Tenemos 2 columnas
        col_graf1, col_graf2 = st.columns(2)
        
        # 1º Columna
        with col_graf1:
            st.write("**Distribución de Calificaciones (Estrellas):**")

            # Creamos un diccionario base asegurando que todas las estrellas (1-5) empiecen en cero
            conteo_manual = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            
            # Ej: valoración [5,1,3,5,2]
            # Recorremos la columna 'valoracion' del DataFrame
            for nota in df_graficos['valoracion']:
                # Vamos sumando 1 (valor, de clave-valor) al casillero de la estrella correspondiente
                conteo_manual[nota] = conteo_manual[nota] + 1


            # Dibujamos el gráfico
            # Claves - Eje X
            # Valores - Eje Y
            st.bar_chart(
                conteo_manual, 
                color="#1f77b4",
                x_label="Estrellas ⭐",       # Nombre para el eje X
                y_label="Cantidad de Reseñas"  # Nombre para el eje Y
            )    

        # 2º Columna  
        with col_graf2:
            st.write("**Evolución Histórica del Negocio:**")
            # Agrupamos por fecha y calculamos la puntuación media de cada día
            evolucion_temporal = df_graficos.groupby('fecha')['valoracion'].mean()

            # ('fecha') Eje X y ['valoracion'] Eje Y
            st.line_chart(evolucion_temporal, color="#ff7f0e")
            
        st.markdown("---")
    # ==========================================
    
    st.write(f"### 📋 Reseñas Registradas ({total_resenas})")

    # Hay reseñas?
    if total_resenas > 0:
        #import csv
        #from io import StringIO
        
        # Fichero virtual temporal donde iremos escribiendo texto
        salida_texto = StringIO()

        # Configuramos herramienta de la librería csv
        escritor = csv.DictWriter(salida_texto, fieldnames=["id", "fecha", "cliente", "valoracion", "comentario"])

        # Cabecera de nuestro fichero CSV
        escritor.writeheader()

        # Volcamos reseñas
        escritor.writerows(resenas_filtradas)

        # Extraemos todo el texto acumulado del fichero virtual como un texto plano
        datos_csv = salida_texto.getvalue()
        
        # Botón para descargar
        st.download_button(
            label="📥 Descargar datos en CSV (Compatible con Numbers / Sheets)",
            data=datos_csv,
            file_name="reporte_feedbackhub.csv",
            mime="text/csv",
            type="secondary"
        )
        
        # Tomamos la lista de diccionarios (resenas_filtradas) y lo convertimos a un DataFrame
        df_tabla = pd.DataFrame(resenas_filtradas)

        # Orden de las columnas
        orden_columnas = ["id", "fecha", "cliente", "valoracion", "comentario"]

        # Aplicamos la lista de ordenamiento sobre la tabla original y guardamos en una variable
        df_tabla_ordenada = df_tabla[orden_columnas]


        # Tabla de reseñas filtradas, con ajuste de anchura automático y omitiendo índice ya que tenemos el id
        #st.dataframe(resenas_filtradas, use_container_width=True, hide_index=True)
        st.dataframe(df_tabla_ordenada, use_container_width=True, hide_index=True)
    
    # No hay reseñas
    else:
        st.warning("⚠️ Ninguna reseña coincide con los filtros aplicados en la barra lateral.")



# PESTAÑA 2: ANALIZAR RESEÑA MANUAL
with tab2:
    st.write("### 🧠 Análisis Unitario bajo Demanda")
    resena_usuario = st.text_area(
        "Reseña del cliente a evaluar:",
        placeholder="Ejemplo: El local estaba limpio pero el precio me pareció excesivo..."
    )
    boton_analizar = st.button("Analizar con IA", type="primary")
    
    # Si ha pulsado el botón de Analizar con IA
    if boton_analizar:

        # Vemos si el usuario ha escrito algo válido, quitando espacios al principio y al final, viendo si quitando esos espacios el texto NO está vacío
        if resena_usuario.strip() != "":

            # Indicador de carga giratorio
            with st.spinner("🤖 El motor de IA está procesando el texto..."):

                # Llamamos la función encargada pasando el texto que escribió el usuario
                resultado_ia = analizar_resena_con_gemini(resena_usuario)
            st.success("✨ Análisis completado con éxito")
            st.info(resultado_ia)
        
        # El usuario no ha escrito nada
        else:
            st.warning("Por favor, escribe un comentario.")

# PIE DE PÁGINA 
st.markdown("---")
st.caption("© Karan Sainani 2026")

st.sidebar.markdown("---")
st.sidebar.caption("© Karan Sainani 2026")