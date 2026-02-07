import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
import os
import tempfile

# Función helper para guardar CSV con fechas en formato DD/MM/YYYY
def guardar_csv_con_fechas(df, ruta_archivo):
    """
    Guarda un DataFrame a CSV con fechas en formato DD/MM/YYYY como texto

    Args:
        df: DataFrame a guardar
        ruta_archivo: Ruta del archivo CSV de salida
    """
    # Crear una copia para no modificar el original
    df_export = df.copy()

    # Convertir columnas de fecha datetime a string DD/MM/YYYY
    columnas_fecha = ['start_date', 'end_date', 'last_approval_status_date', 'modificado_el', 'fse_fechas']
    for col in columnas_fecha:
        if col in df_export.columns:
            # Convertir datetime a string DD/MM/YYYY
            df_export[col] = df_export[col].apply(
                lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) and hasattr(x, 'strftime') else x
            )

    # Guardar como CSV
    df_export.to_csv(ruta_archivo, index=False, encoding='utf-8-sig', sep=';')
    return ruta_archivo

st.set_page_config(
    page_title="Auditoría Ausentismos Corrección",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS CSS
# ============================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        color: white;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    .paso-header {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 2rem;
    }
    
    .paso-header h2 {
        color: #2c3e50;
        margin: 0;
        font-size: 1.8rem;
    }
    
    .paso-header p {
        color: #7f8c8d;
        margin: 0.5rem 0 0 0;
    }
    
    .success-box {
        background: #27ae60;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .warning-box {
        background: #e74c3c;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .info-box {
        background: #3498db;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INICIALIZACIÓN
# ============================================================================
if 'paso_actual' not in st.session_state:
    st.session_state.paso_actual = 1

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================
def crear_zip_desde_archivos(archivos_paths):
    """Crea ZIP desde rutas de archivos existentes"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for ruta in archivos_paths:
            if os.path.exists(ruta):
                zip_file.write(ruta, os.path.basename(ruta))
    return zip_buffer.getvalue()

def mostrar_header_principal():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Auditoría Ausentismos Corrección</h1>
        <p>Sistema Integrado de Gestión y Validación</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PASO 1: PROCESAMIENTO INICIAL
# ============================================================================
def paso1():
    mostrar_header_principal()
    
    st.markdown("""
    <div class="paso-header">
        <h2>📄 PASO 1: Procesamiento Inicial</h2>
        <p>CONCAT de CSV + Excel Reporte 45 con homologación y validaciones</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ ¿Qué hace este paso?", expanded=False):
        st.write("**📥 Archivos de Entrada:**")
        st.write("• CSV de Ausentismos (Success Factors)")
        st.write("• Excel Reporte 45 (SAP)")
        
        st.write("**📤 Archivos de Salida:**")
        st.write("• ausentismo_procesado_completo_v2.csv")
        
        st.write("**🔧 Procesos Ejecutados:**")
        st.write("• Concatenación de CSV + Excel")
        st.write("• Homologación SSF vs SAP")
        st.write("• Identificación de validadores")
        st.write("• Generación de llaves únicas")
    
    st.warning("🔴 Este paso requiere 2 archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Archivo 1")
        csv_file = st.file_uploader(
            "CSV de Ausentismos",
            type=['csv'],
            key="csv1",
            help="Archivo exportado desde Success Factors"
        )
    
    with col2:
        st.subheader("📤 Archivo 2")
        excel_file = st.file_uploader(
            "Excel Reporte 45",
            type=['xlsx', 'xls'],
            key="excel1",
            help="Reporte 45 exportado desde SAP"
        )
    
    if csv_file and excel_file:
        st.divider()
        
        if st.button("🚀 PROCESAR ARCHIVOS", use_container_width=True, type="primary"):
            try:
                with st.spinner('⏳ Procesando archivos...'):
                    temp_dir = tempfile.mkdtemp()
                    
                    csv_path = os.path.join(temp_dir, "input.csv")
                    excel_path = os.path.join(temp_dir, "reporte45.xlsx")
                    
                    with open(csv_path, "wb") as f:
                        f.write(csv_file.getbuffer())
                    with open(excel_path, "wb") as f:
                        f.write(excel_file.getbuffer())
                    
                    import auditoria_ausentismos_part1 as part1
                    import importlib
                    importlib.reload(part1)
                    
                    part1.ruta_entrada_csv = csv_path
                    part1.ruta_entrada_excel = excel_path
                    part1.directorio_salida = temp_dir
                    part1.archivo_salida = "ausentismo_procesado_completo_v2.csv"
                    part1.ruta_completa_salida = os.path.join(temp_dir, "ausentismo_procesado_completo_v2.csv")
                    
                    df_resultado = part1.procesar_archivo_ausentismos()
                    
                    if df_resultado is not None:
                        st.success("✅ Procesamiento completado exitosamente")

                        # Debug: Verificar columna fse_fechas
                        if 'fse_fechas' in df_resultado.columns:
                            valores_fse_con_fecha = df_resultado['fse_fechas'].notna().sum()
                            st.info(f"✅ Columna 'fse_fechas' encontrada: {valores_fse_con_fecha:,} registros con fecha de {len(df_resultado):,} totales")
                        else:
                            st.warning("⚠️ Columna 'fse_fechas' NO encontrada en el resultado")
                            st.write("Columnas disponibles:")
                            st.write(list(df_resultado.columns))

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Total Registros", f"{len(df_resultado):,}")
                        with col2:
                            st.metric("🔑 Llaves Únicas", f"{df_resultado['llave'].nunique():,}")
                        with col3:
                            alertas = (df_resultado['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO').sum()
                            st.metric("⚠️ Alertas", alertas)
                        with col4:
                            st.metric("📋 Columnas", len(df_resultado.columns))
                        
                        st.divider()
                        st.subheader("👀 Vista Previa de Datos")
                        st.dataframe(df_resultado.head(10), use_container_width=True)
                        
                        st.divider()
                        st.subheader("📦 Descargar Resultados")

                        archivo_salida = os.path.join(temp_dir, "ausentismo_procesado_completo_v2.csv")

                        if os.path.exists(archivo_salida):
                            # Crear ZIP solo con el archivo principal
                            archivos_para_zip = [archivo_salida]
                            zip_data = crear_zip_desde_archivos(archivos_para_zip)

                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.download_button(
                                    "📥 DESCARGAR ZIP - PASO 1",
                                    zip_data,
                                    "PASO_1_Procesado.zip",
                                    "application/zip",
                                    use_container_width=True,
                                    type="primary"
                                )
                            with col2:
                                if st.button("▶️ Siguiente", use_container_width=True):
                                    st.session_state.paso_actual = 2
                                    st.rerun()
                    else:
                        st.error("❌ Error en el procesamiento")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("🔍 Ver detalles"):
                    import traceback
                    st.code(traceback.format_exc())

# ============================================================================
# PASO 2: VALIDACIONES
# ============================================================================
def paso2():
    mostrar_header_principal()
    
    st.markdown("""
    <div class="paso-header">
        <h2>🔗 PASO 2: Validaciones y Merge con Personal</h2>
        <p>Cruza con datos de personal y ejecuta múltiples validaciones</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ ¿Qué hace este paso?", expanded=False):
        st.write("**📥 Archivos de Entrada:**")
        st.write("• CSV del Paso 1")
        st.write("• Excel MD")

        st.write("**📤 Archivos de Salida:**")
        st.write("• relacion_laboral_con_validaciones.csv (COMPLETO, sin filtro)")
        st.write("• Múltiples archivos Excel de alertas (pueden filtrarse por fechas)")

        st.write("**🔧 Validaciones:**")
        st.write("• Validación SENA")
        st.write("• Validación Ley 50")
        st.write("• Validación Integral")
        st.write("• Validación de licencias (6 tipos)")

        st.write("**📅 Filtro de Fechas Opcional:**")
        st.write("• Puedes filtrar SOLO los archivos Excel de alertas por rango de fechas")
        st.write("• El CSV principal siempre se guarda completo")
    
    st.warning("🔴 Este paso requiere 2 archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Archivo 1")
        csv_paso1 = st.file_uploader(
            "CSV del Paso 1",
            type=['csv'],
            key="csv2"
        )
    
    with col2:
        st.subheader("📤 Archivo 2")
        excel_personal = st.file_uploader(
            "Excel MD",
            type=['xlsx', 'xls'],
            key="excel2",
            help="Archivo MD_*.xlsx con datos de personal"
        )

    st.divider()
    st.subheader("📅 Filtro de Fechas (Opcional)")
    st.caption("**Alertas (Excel):** Fecha inicio → automático hasta fin de mes | **CSV principal:** Rango personalizado")

    col_fecha1, col_fecha2 = st.columns(2)

    with col_fecha1:
        fecha_inicio_alertas = st.date_input(
            "📅 Fecha Inicio",
            value=None,
            format="DD/MM/YYYY",
            key="fecha_inicio_alertas_paso2",
            help="Fecha de inicio para filtrar"
        )

    with col_fecha2:
        fecha_fin_csv = st.date_input(
            "📅 Fecha Fin (CSV principal)",
            value=None,
            format="DD/MM/YYYY",
            key="fecha_fin_csv_paso2",
            help="Fecha fin para filtrar el CSV principal (opcional)"
        )

    # Calcular automáticamente el fin de mes PARA ALERTAS
    fecha_fin_alertas = None
    if fecha_inicio_alertas is not None:
        import calendar
        from datetime import date
        ultimo_dia = calendar.monthrange(fecha_inicio_alertas.year, fecha_inicio_alertas.month)[1]
        fecha_fin_alertas = date(fecha_inicio_alertas.year, fecha_inicio_alertas.month, ultimo_dia)

        st.success(f"✅ **Alertas (Excel):** {fecha_inicio_alertas.strftime('%d/%m/%Y')} → {fecha_fin_alertas.strftime('%d/%m/%Y')} (fin de mes automático)")

    # Mostrar info del CSV principal si hay fecha fin
    if fecha_inicio_alertas is not None and fecha_fin_csv is not None:
        st.info(f"📊 **CSV principal:** Se filtrará entre {fecha_inicio_alertas.strftime('%d/%m/%Y')} y {fecha_fin_csv.strftime('%d/%m/%Y')}")
    elif fecha_inicio_alertas is not None and fecha_fin_csv is None:
        st.warning("⚠️ **CSV principal:** Se guardará completo SIN filtrar (no hay fecha fin)")

    usar_filtro_alertas = fecha_inicio_alertas is not None and fecha_fin_alertas is not None

    if csv_paso1 and excel_personal:
        st.divider()
        
        if st.button("🚀 PROCESAR ARCHIVOS", use_container_width=True, type="primary"):
            try:
                with st.spinner('⏳ Procesando validaciones...'):
                    temp_dir = tempfile.mkdtemp()
                    
                    csv_path = os.path.join(temp_dir, "ausentismo_procesado_completo_v2.csv")
                    excel_path = os.path.join(temp_dir, "MD_personal.xlsx")
                    
                    with open(csv_path, "wb") as f:
                        f.write(csv_paso1.getbuffer())
                    with open(excel_path, "wb") as f:
                        f.write(excel_personal.getbuffer())

                    # Validar que el archivo CSV no esté vacío
                    if os.path.getsize(csv_path) == 0:
                        st.error("❌ El archivo CSV del Paso 1 está vacío. Por favor, sube un archivo válido.")
                        st.stop()

                    # Intentar leer el CSV con manejo de errores
                    try:
                        df_ausentismo = pd.read_csv(csv_path, encoding='utf-8-sig')
                        if df_ausentismo.empty or len(df_ausentismo.columns) == 0:
                            st.error("❌ El archivo CSV no contiene datos válidos o no tiene columnas.")
                            st.stop()
                    except pd.errors.EmptyDataError:
                        st.error("❌ El archivo CSV está vacío o no tiene un formato válido. Verifica que sea el archivo correcto del Paso 1.")
                        st.stop()
                    except Exception as e:
                        st.error(f"❌ Error al leer el archivo CSV: {str(e)}")
                        st.stop()

                    df_personal = pd.read_excel(excel_path)
                    
                    st.info(f"📊 CSV: {len(df_ausentismo):,} | Excel: {len(df_personal):,}")
                    
                    col_num_pers = next((col for col in df_personal.columns if 'pers' in col.lower()), None)
                    col_relacion = next((col for col in df_personal.columns if 'relaci' in col.lower() and 'labor' in col.lower()), None)
                    
                    if not col_num_pers or not col_relacion:
                        st.error("❌ No se encontraron las columnas necesarias")
                        st.stop()
                    
                    df_ausentismo['id_personal'] = df_ausentismo['id_personal'].astype(str).str.strip()
                    df_personal[col_num_pers] = df_personal[col_num_pers].astype(str).str.strip()

                    # Si ya existe 'Relación laboral' en df_ausentismo, eliminarla antes del merge
                    # para evitar conflictos (_x, _y) y usar la del archivo de personal
                    if 'Relación laboral' in df_ausentismo.columns:
                        st.info("ℹ️ Eliminando columna 'Relación laboral' antigua del CSV para actualizar con datos del Excel")
                        df_ausentismo = df_ausentismo.drop('Relación laboral', axis=1)

                    df = pd.merge(
                        df_ausentismo,
                        df_personal[[col_num_pers, col_relacion]],
                        left_on='id_personal',
                        right_on=col_num_pers,
                        how='left'
                    )

                    # Eliminar columna duplicada de número de personal si existe
                    if col_num_pers in df.columns and col_num_pers != 'id_personal':
                        df.drop(columns=[col_num_pers], inplace=True)

                    # Renombrar la columna a 'Relación laboral' si tiene otro nombre
                    if col_relacion != 'Relación laboral':
                        df.rename(columns={col_relacion: 'Relación laboral'}, inplace=True)

                    # Manejar sufijos _x, _y si aparecen (por columnas duplicadas)
                    if 'Relación laboral' not in df.columns:
                        if 'Relación laboral_y' in df.columns:
                            # Usar la del archivo de personal (_y) y eliminar la antigua (_x)
                            df.rename(columns={'Relación laboral_y': 'Relación laboral'}, inplace=True)
                            if 'Relación laboral_x' in df.columns:
                                df.drop(columns=['Relación laboral_x'], inplace=True)
                            st.warning("⚠️ Se detectaron columnas duplicadas. Usando 'Relación laboral' del archivo Excel de personal.")
                        elif 'Relación laboral_x' in df.columns:
                            df.rename(columns={'Relación laboral_x': 'Relación laboral'}, inplace=True)

                    # Convertir columnas de fecha a formato datetime (día/mes/año)
                    columnas_fecha = ['start_date', 'end_date', 'last_approval_status_date', 'modificado_el', 'fse_fechas']
                    for col in columnas_fecha:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')

                    # Verificar que la columna 'Relación laboral' exista
                    if 'Relación laboral' not in df.columns:
                        st.error(f"❌ Error: La columna 'Relación laboral' no existe después del merge.")
                        st.error(f"📋 Columna buscada: '{col_relacion}'")
                        st.error(f"📋 Columnas disponibles después del merge:")
                        st.code(', '.join(df.columns))
                        st.stop()

                    # Filtrar registros sin relación laboral
                    registros_antes = len(df)
                    df = df[df['Relación laboral'].notna()]
                    registros_despues = len(df)

                    if registros_despues == 0:
                        st.error("❌ No hay registros con Relación laboral válida después del merge.")
                        st.error("💡 Verifica que los IDs de personal coincidan entre ambos archivos.")
                        st.stop()

                    st.success(f"✅ Merge exitoso: {registros_despues:,} registros con Relación laboral (eliminados {registros_antes - registros_despues:,} sin relación)")
                    
                    # Validaciones SENA
                    df_aprendizaje = df[df['Relación laboral'].str.contains('Aprendizaje', case=False, na=False)].copy()
                    conceptos_validos = ['Incapacidad gral SENA', 'Licencia de Maternidad SENA', 'Suspensión contrato SENA']
                    df_errores_sena = df_aprendizaje[~df_aprendizaje['external_name_label'].isin(conceptos_validos)].copy()
                    
                    # Validaciones Ley 50
                    df_ley50 = df[df['Relación laboral'].str.contains('Ley 50', case=False, na=False)].copy()
                    prohibidos = ['Incapacidad gral SENA', 'Licencia de Maternidad SENA', 'Suspensión contrato SENA',
                                 'Inca. Enfer Gral Integral', 'Prorr Inc/Enf Gral ntegra']
                    df_errores_ley50 = df_ley50[df_ley50['external_name_label'].isin(prohibidos)].copy()
                    
                    # Convertir calendar_days y quantity_in_days a numérico
                    df['calendar_days'] = pd.to_numeric(df['calendar_days'], errors='coerce')
                    df['quantity_in_days'] = pd.to_numeric(df['quantity_in_days'], errors='coerce')
                    
                    # Columnas de validación
                    df['licencia_paternidad'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia Paternidad" and r['calendar_days'] == 14 
                        else "Concepto No Aplica", axis=1)
                    
                    df['licencia_maternidad'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia Maternidad" and r['calendar_days'] == 126 
                        else "Concepto No Aplica", axis=1)
                    
                    df['ley_de_luto'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Ley de luto" and r['quantity_in_days'] == 5 
                        else "Concepto No Aplica", axis=1)
                    
                    df['incap_fuera_de_turno'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Incapa.fuera de turno" and r['calendar_days'] <= 1 
                        else "Concepto No Aplica", axis=1)
                    
                    df['lic_maternidad_sena'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Licencia de Maternidad SENA" and r['calendar_days'] == 126 
                        else "Concepto No Aplica", axis=1)
                    
                    df['lic_jurado_votacion'] = df.apply(
                        lambda r: "Concepto Si Aplica" if r['external_name_label'] == "Lic Jurado Votación" and r['calendar_days'] <= 1 
                        else "Concepto No Aplica", axis=1)
                    
                    # Guardar archivo principal COMPLETO (SIEMPRE SIN FILTRAR)
                    archivo_principal = os.path.join(temp_dir, "relacion_laboral_con_validaciones.csv")
                    df.to_csv(archivo_principal, index=False, encoding='utf-8-sig')

                    archivos_generados = [archivo_principal]

                    # ============================================================================
                    # OPCIÓN 1: FILTRAR CSV PRINCIPAL SI HAY FECHA FIN
                    # ============================================================================
                    if fecha_inicio_alertas is not None and fecha_fin_csv is not None:
                        st.info(f"🔍 Filtrando CSV principal: {fecha_inicio_alertas.strftime('%d/%m/%Y')} → {fecha_fin_csv.strftime('%d/%m/%Y')}")

                        df_csv_filtrado = df.copy()
                        df_csv_filtrado['start_date'] = pd.to_datetime(df_csv_filtrado['start_date'], errors='coerce')
                        df_csv_filtrado['end_date'] = pd.to_datetime(df_csv_filtrado['end_date'], errors='coerce')

                        fecha_inicio_dt = pd.to_datetime(fecha_inicio_alertas)
                        fecha_fin_csv_dt = pd.to_datetime(fecha_fin_csv)

                        df_csv_filtrado = df_csv_filtrado[
                            (df_csv_filtrado['start_date'] >= fecha_inicio_dt) &
                            (df_csv_filtrado['end_date'] <= fecha_fin_csv_dt)
                        ].copy()

                        # Convertir fechas de vuelta
                        df_csv_filtrado['start_date'] = df_csv_filtrado['start_date'].dt.strftime('%d/%m/%Y')
                        df_csv_filtrado['end_date'] = df_csv_filtrado['end_date'].dt.strftime('%d/%m/%Y')

                        # Guardar CSV filtrado
                        archivo_csv_filtrado = os.path.join(temp_dir, "relacion_laboral_FILTRADO.csv")
                        df_csv_filtrado.to_csv(archivo_csv_filtrado, index=False, encoding='utf-8-sig')
                        archivos_generados.append(archivo_csv_filtrado)

                        st.success(f"✅ CSV filtrado: {len(df):,} → {len(df_csv_filtrado):,} registros")

                    # ============================================================================
                    # OPCIÓN 2: APLICAR FILTRO DE FECHAS PARA ALERTAS (SOLO START_DATE EN EL MES)
                    # ============================================================================
                    df_para_alertas = df.copy()

                    if usar_filtro_alertas:
                        st.info(f"🔍 Aplicando filtro a ALERTAS (solo start_date): {fecha_inicio_alertas.strftime('%d/%m/%Y')} → {fecha_fin_alertas.strftime('%d/%m/%Y')}")

                        # Convertir columnas de fecha a datetime para filtrar
                        df_para_alertas['start_date'] = pd.to_datetime(df_para_alertas['start_date'], errors='coerce')
                        df_para_alertas['end_date'] = pd.to_datetime(df_para_alertas['end_date'], errors='coerce')

                        fecha_inicio_dt = pd.to_datetime(fecha_inicio_alertas)
                        fecha_fin_alertas_dt = pd.to_datetime(fecha_fin_alertas)

                        # CRÍTICO: Filtrar SOLO por start_date (no importa end_date)
                        # Si start_date está en enero, traer el registro aunque end_date sea febrero o después
                        df_para_alertas = df_para_alertas[
                            (df_para_alertas['start_date'] >= fecha_inicio_dt) &
                            (df_para_alertas['start_date'] <= fecha_fin_alertas_dt)
                        ].copy()

                        registros_antes = len(df)
                        registros_despues = len(df_para_alertas)
                        st.success(f"✅ Filtro alertas aplicado (solo start_date en el mes): {registros_antes:,} → {registros_despues:,} registros")

                        # Convertir fechas de vuelta a formato DD/MM/AAAA
                        df_para_alertas['start_date'] = df_para_alertas['start_date'].dt.strftime('%d/%m/%Y')
                        df_para_alertas['end_date'] = df_para_alertas['end_date'].dt.strftime('%d/%m/%Y')
                    else:
                        # Si no hay filtro, asegurar que las fechas estén en formato correcto
                        df_para_alertas['start_date'] = pd.to_datetime(df_para_alertas['start_date'], errors='coerce').dt.strftime('%d/%m/%Y')
                        df_para_alertas['end_date'] = pd.to_datetime(df_para_alertas['end_date'], errors='coerce').dt.strftime('%d/%m/%Y')

                    # Recrear DataFrames de validación con el DataFrame filtrado
                    df_aprendizaje_filt = df_para_alertas[df_para_alertas['Relación laboral'].str.contains('Aprendizaje', case=False, na=False)].copy()
                    conceptos_validos = ['Incapacidad gral SENA', 'Licencia de Maternidad SENA', 'Suspensión contrato SENA']
                    df_errores_sena = df_aprendizaje_filt[~df_aprendizaje_filt['external_name_label'].isin(conceptos_validos)].copy()

                    # Validaciones Ley 50 - CON CÓDIGOS NUMÉRICOS
                    st.info("🔍 Validando registros con Ley 50...")

                    df_ley50_filt = df_para_alertas[df_para_alertas['Relación laboral'].str.contains('Ley 50', case=False, na=False)].copy()

                    st.write(f"📊 **Registros con 'Ley 50' encontrados:** {len(df_ley50_filt):,}")

                    # Códigos prohibidos para Ley 50 (códigos de SENA e INTEGRAL)
                    codigos_prohibidos_ley50 = [
                        197, 331, 333, 334, 203, 216, 201, 281, 280,
                        341, 398, 332, 303, 301, 196, 311, 233, 251, 231, 198
                    ]

                    if len(df_ley50_filt) > 0:
                        # Mostrar códigos únicos en Ley 50 ANTES de filtrar
                        codigos_unicos_ley50 = df_ley50_filt['homologacion_clase_de_ausentismo_ssf_vs_sap'].value_counts().head(10)
                        with st.expander("🔍 Ver top 10 códigos en registros Ley 50"):
                            for codigo, cantidad in codigos_unicos_ley50.items():
                                st.write(f"  - Código **{codigo}**: {cantidad} registros")

                        # Convertir columna a numérico
                        df_ley50_filt['homologacion_clase_de_ausentismo_ssf_vs_sap'] = pd.to_numeric(
                            df_ley50_filt['homologacion_clase_de_ausentismo_ssf_vs_sap'],
                            errors='coerce'
                        )

                        # Filtrar SOLO los que tienen códigos prohibidos
                        df_errores_ley50 = df_ley50_filt[
                            df_ley50_filt['homologacion_clase_de_ausentismo_ssf_vs_sap'].isin(codigos_prohibidos_ley50)
                        ].copy()

                        st.write(f"🚨 **Errores encontrados (Ley 50 con códigos prohibidos):** {len(df_errores_ley50):,}")

                        if len(df_errores_ley50) > 0:
                            # Mostrar códigos prohibidos encontrados
                            with st.expander("⚠️ Ver códigos prohibidos encontrados en Ley 50"):
                                codigos_encontrados = df_errores_ley50['homologacion_clase_de_ausentismo_ssf_vs_sap'].value_counts()
                                for codigo, cantidad in codigos_encontrados.items():
                                    st.write(f"  - Código **{int(codigo)}**: {cantidad} registros")
                    else:
                        df_errores_ley50 = pd.DataFrame()
                        st.warning("⚠️ No se encontraron registros con 'Ley 50' en Relación laboral")

                    # Validaciones Integral - CON CÓDIGOS NUMÉRICOS
                    st.info("🔍 Validando registros con Integral...")

                    df_integral_filt = df_para_alertas[df_para_alertas['Relación laboral'].str.contains('Integral', case=False, na=False)].copy()

                    st.write(f"📊 **Registros con 'Integral' encontrados:** {len(df_integral_filt):,}")

                    # Códigos prohibidos para Integral (los 25 que NO deben estar)
                    codigos_prohibidos_integral = [
                        380, 330, 291, 204, 202, 215, 210, 220, 200,
                        281, 280, 340, 345, 305, 398, 302, 300, 191,
                        310, 190, 232, 250, 230, 381, 198
                    ]

                    if len(df_integral_filt) > 0:
                        # Mostrar códigos únicos en Integral ANTES de filtrar
                        codigos_unicos_integral = df_integral_filt['homologacion_clase_de_ausentismo_ssf_vs_sap'].value_counts().head(10)
                        with st.expander("🔍 Ver top 10 códigos en registros Integral"):
                            for codigo, cantidad in codigos_unicos_integral.items():
                                st.write(f"  - Código **{codigo}**: {cantidad} registros")

                        # Convertir columna a numérico
                        df_integral_filt['homologacion_clase_de_ausentismo_ssf_vs_sap'] = pd.to_numeric(
                            df_integral_filt['homologacion_clase_de_ausentismo_ssf_vs_sap'],
                            errors='coerce'
                        )

                        # Filtrar SOLO los que tienen códigos prohibidos
                        df_errores_integral = df_integral_filt[
                            df_integral_filt['homologacion_clase_de_ausentismo_ssf_vs_sap'].isin(codigos_prohibidos_integral)
                        ].copy()

                        st.write(f"🚨 **Errores encontrados (Integral con códigos prohibidos):** {len(df_errores_integral):,}")

                        if len(df_errores_integral) > 0:
                            # Mostrar códigos prohibidos encontrados
                            with st.expander("⚠️ Ver códigos prohibidos encontrados en Integral"):
                                codigos_encontrados = df_errores_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'].value_counts()
                                for codigo, cantidad in codigos_encontrados.items():
                                    st.write(f"  - Código **{int(codigo)}**: {cantidad} registros")
                    else:
                        df_errores_integral = pd.DataFrame()
                        st.warning("⚠️ No se encontraron registros con 'Integral' en Relación laboral")

                    # Errores SENA
                    if len(df_errores_sena) > 0:
                        path = os.path.join(temp_dir, "Sena_error_validar.csv")
                        guardar_csv_con_fechas(df_errores_sena, path)
                        archivos_generados.append(path)

                    # Errores Ley 50
                    if len(df_errores_ley50) > 0:
                        path = os.path.join(temp_dir, "Ley_50_error_validar.csv")
                        guardar_csv_con_fechas(df_errores_ley50, path)
                        archivos_generados.append(path)

                    # Errores Integral (SOLO los que tienen códigos prohibidos)
                    if len(df_errores_integral) > 0:
                        path = os.path.join(temp_dir, "Integral_error_validar.csv")
                        guardar_csv_con_fechas(df_errores_integral, path)
                        archivos_generados.append(path)

                    # Alertas por columna (usando df_para_alertas que puede estar filtrado)
                    df_alert_pat = df_para_alertas[(df_para_alertas['licencia_paternidad'] == 'Concepto No Aplica') & (df_para_alertas['external_name_label'] == 'Licencia Paternidad')]
                    if len(df_alert_pat) > 0:
                        path = os.path.join(temp_dir, "alerta_licencia_paternidad.csv")
                        guardar_csv_con_fechas(df_alert_pat, path)
                        archivos_generados.append(path)

                    df_alert_mat = df_para_alertas[(df_para_alertas['licencia_maternidad'] == 'Concepto No Aplica') & (df_para_alertas['external_name_label'] == 'Licencia Maternidad')]
                    if len(df_alert_mat) > 0:
                        path = os.path.join(temp_dir, "alerta_licencia_maternidad.csv")
                        guardar_csv_con_fechas(df_alert_mat, path)
                        archivos_generados.append(path)

                    df_alert_luto = df_para_alertas[(df_para_alertas['ley_de_luto'] == 'Concepto No Aplica') & (df_para_alertas['external_name_label'] == 'Ley de luto')]
                    if len(df_alert_luto) > 0:
                        path = os.path.join(temp_dir, "alerta_ley_de_luto.csv")
                        guardar_csv_con_fechas(df_alert_luto, path)
                        archivos_generados.append(path)

                    df_alert_incap = df_para_alertas[(df_para_alertas['incap_fuera_de_turno'] == 'Concepto No Aplica') & (df_para_alertas['external_name_label'] == 'Incapa.fuera de turno')]
                    if len(df_alert_incap) > 0:
                        path = os.path.join(temp_dir, "alerta_incap_fuera_de_turno.csv")
                        guardar_csv_con_fechas(df_alert_incap, path)
                        archivos_generados.append(path)

                    df_alert_mat_sena = df_para_alertas[(df_para_alertas['lic_maternidad_sena'] == 'Concepto No Aplica') & (df_para_alertas['external_name_label'] == 'Licencia de Maternidad SENA')]
                    if len(df_alert_mat_sena) > 0:
                        path = os.path.join(temp_dir, "alerta_lic_maternidad_sena.csv")
                        guardar_csv_con_fechas(df_alert_mat_sena, path)
                        archivos_generados.append(path)
                    
                    df_alert_jurado = df_para_alertas[(df_para_alertas['lic_jurado_votacion'] == 'Concepto No Aplica') & (df_para_alertas['external_name_label'] == 'Lic Jurado Votación')]
                    if len(df_alert_jurado) > 0:
                        path = os.path.join(temp_dir, "alerta_lic_jurado_votacion.csv")
                        guardar_csv_con_fechas(df_alert_jurado, path)
                        archivos_generados.append(path)

                    conceptos_incap = ['Incapacidad enfermedad general', 'Prorroga Inca/Enfer Gene', 'Enf Gral SOAT',
                                      'Inc. Accidente de Trabajo', 'Prorroga Inc. Accid. Trab']
                    df_incap30 = df_para_alertas[(df_para_alertas['external_name_label'].isin(conceptos_incap)) & (df_para_alertas['calendar_days'] > 30)]
                    if len(df_incap30) > 0:
                        path = os.path.join(temp_dir, "incp_mayor_30_dias.csv")
                        guardar_csv_con_fechas(df_incap30, path)
                        archivos_generados.append(path)

                    conceptos_sin_pago = ['Aus Reg sin Soporte', 'Suspensión']
                    df_sin_pago = df_para_alertas[(df_para_alertas['external_name_label'].isin(conceptos_sin_pago)) & (df_para_alertas['calendar_days'] > 10)]
                    if len(df_sin_pago) > 0:
                        path = os.path.join(temp_dir, "Validacion_ausentismos_sin_pago_mayor_10_dias.csv")
                        guardar_csv_con_fechas(df_sin_pago, path)
                        archivos_generados.append(path)

                    df_dia_fam = df_para_alertas[(df_para_alertas['external_name_label'] == 'Día de la familia') & (df_para_alertas['calendar_days'] > 1)]
                    if len(df_dia_fam) > 0:
                        path = os.path.join(temp_dir, "dia_de_la_familia.csv")
                        guardar_csv_con_fechas(df_dia_fam, path)
                        archivos_generados.append(path)

                    # Validación: Incapacidad sin enlace (FSE Si Aplica pero sin fecha)
                    if 'fse_fechas' in df_para_alertas.columns:
                        df_incap_sin_enlace = df_para_alertas[
                            (df_para_alertas['fse'] == 'Si Aplica') &
                            (df_para_alertas['fse_fechas'].isna() | (df_para_alertas['fse_fechas'] == ''))
                        ]
                        if len(df_incap_sin_enlace) > 0:
                            path = os.path.join(temp_dir, "Incapacidad_sin_enlace.csv")
                            guardar_csv_con_fechas(df_incap_sin_enlace, path)
                            archivos_generados.append(path)
                            st.info(f"🔗 Incapacidad sin enlace: {len(df_incap_sin_enlace)} registros con FSE='Si Aplica' sin fecha")

                    # Validación: Validadores no encontrados
                    if 'nombre_validador' in df_para_alertas.columns:
                        df_validadores_no_encontrados = df_para_alertas[
                            df_para_alertas['nombre_validador'] == 'ALERTA VALIDADOR NO ENCONTRADO'
                        ]
                        if len(df_validadores_no_encontrados) > 0:
                            # Seleccionar columnas relevantes (las que existan)
                            columnas_alerta = [
                                'id_personal',
                                'nombre_completo',
                                'last_modified_by',
                                'llave',
                                'start_date',
                                'end_date',
                                'nombre_validador',
                                'usuario_validador',
                                'codigo_validador',
                                'Relación laboral'
                            ]
                            columnas_disponibles = [col for col in columnas_alerta if col in df_validadores_no_encontrados.columns]
                            df_alerta = df_validadores_no_encontrados[columnas_disponibles].copy()

                            path = os.path.join(temp_dir, "usuario_aprobador_no_encontrado.csv")
                            guardar_csv_con_fechas(df_alerta, path)
                            archivos_generados.append(path)

                            st.warning(f"⚠️ ALERTA: Se encontraron {len(df_validadores_no_encontrados)} registros con validador NO ENCONTRADO")
                            st.info(f"📊 Registros en alerta: {len(df_alerta)}")

                            # Mostrar valores únicos de lastModifiedBy no encontrados
                            if 'last_modified_by' in df_validadores_no_encontrados.columns:
                                valores_unicos = df_validadores_no_encontrados['last_modified_by'].unique()
                                st.write(f"**📋 Valores de last_modified_by no encontrados ({len(valores_unicos)}):**")
                                for i, valor in enumerate(valores_unicos[:10], 1):
                                    frecuencia = (df_validadores_no_encontrados['last_modified_by'] == valor).sum()
                                    st.write(f"  {i:2d}. '{valor}' ({frecuencia} registros)")
                                if len(valores_unicos) > 10:
                                    st.write(f"  ... y {len(valores_unicos) - 10} más")

                    # Validación: Registros sin diagnóstico (códigos de incapacidad sin descripcion_general_external_code)
                    codigos_requieren_diagnostico = [
                        '203', '202', '216', '215', '210', '220', '201', '200',
                        '188', '235', '383', '233', '251', '231', '232', '250', '230'
                    ]

                    if 'homologacion_clase_de_ausentismo_ssf_vs_sap' in df_para_alertas.columns:
                        # Convertir a string para comparación
                        df_para_alertas['homologacion_clase_de_ausentismo_ssf_vs_sap'] = df_para_alertas['homologacion_clase_de_ausentismo_ssf_vs_sap'].astype(str).str.strip()

                        # Filtrar registros con esos códigos
                        df_codigos_diagnostico = df_para_alertas[
                            df_para_alertas['homologacion_clase_de_ausentismo_ssf_vs_sap'].isin(codigos_requieren_diagnostico)
                        ].copy()

                        if len(df_codigos_diagnostico) > 0:
                            if 'descripcion_general_external_code' in df_codigos_diagnostico.columns:
                                # Verificar si descripcion_general_external_code está vacía
                                mask_sin_diagnostico = (
                                    df_codigos_diagnostico['descripcion_general_external_code'].isna() |
                                    (df_codigos_diagnostico['descripcion_general_external_code'].astype(str).str.strip() == '') |
                                    (df_codigos_diagnostico['descripcion_general_external_code'].astype(str).str.strip() == 'nan')
                                )

                                df_sin_diagnostico = df_codigos_diagnostico[mask_sin_diagnostico].copy()

                                if len(df_sin_diagnostico) > 0:
                                    # Escribir "registros_sin_diagnostico" en la columna vacía
                                    df_sin_diagnostico['descripcion_general_external_code'] = 'registros_sin_diagnostico'

                                    path = os.path.join(temp_dir, "registros_sin_diagnostico.csv")
                                    guardar_csv_con_fechas(df_sin_diagnostico, path)
                                    archivos_generados.append(path)

                                    st.warning(f"⚠️ ALERTA: Se encontraron {len(df_sin_diagnostico)} registros SIN DIAGNÓSTICO")
                                    st.info(f"📊 Códigos afectados: {df_sin_diagnostico['homologacion_clase_de_ausentismo_ssf_vs_sap'].unique().tolist()}")

                    # Validación: Diagnóstico incorrecto (menos de 2 caracteres)
                    if 'descripcion_general_external_code' in df_para_alertas.columns:
                        # Convertir a string
                        df_para_alertas['descripcion_general_external_code_str'] = df_para_alertas['descripcion_general_external_code'].astype(str).str.strip()

                        # Filtrar: no vacío, no 'nan', y longitud < 2
                        mask_diagnostico_incorrecto = (
                            (df_para_alertas['descripcion_general_external_code_str'] != '') &
                            (df_para_alertas['descripcion_general_external_code_str'] != 'nan') &
                            (df_para_alertas['descripcion_general_external_code_str'].str.len() < 2)
                        )

                        df_diagnostico_incorrecto = df_para_alertas[mask_diagnostico_incorrecto].copy()

                        # Eliminar columna temporal
                        df_para_alertas.drop('descripcion_general_external_code_str', axis=1, inplace=True)

                        if len(df_diagnostico_incorrecto) > 0:
                            path = os.path.join(temp_dir, "diagnostico_incorrecto.csv")
                            guardar_csv_con_fechas(df_diagnostico_incorrecto, path)
                            archivos_generados.append(path)

                            st.warning(f"⚠️ ALERTA: Se encontraron {len(df_diagnostico_incorrecto)} registros con DIAGNÓSTICO INCORRECTO (< 2 caracteres)")
                            st.info(f"📊 Valores incorrectos: {df_diagnostico_incorrecto['descripcion_general_external_code'].unique().tolist()[:10]}")

                    st.success("✅ Validaciones completadas")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 Total", f"{len(df):,}")
                    with col2:
                        st.metric("🚨 SENA", len(df_errores_sena))
                    with col3:
                        st.metric("🚨 Ley 50", len(df_errores_ley50))
                    with col4:
                        st.metric("🚨 Integral", len(df_errores_integral))

                    col1b, col2b = st.columns(2)
                    with col1b:
                        st.metric("📁 Archivos Generados", len(archivos_generados))
                    with col2b:
                        total_errores = len(df_errores_sena) + len(df_errores_ley50) + len(df_errores_integral)
                        st.metric("⚠️ Total Errores", total_errores)
                    
                    st.divider()
                    st.subheader("👀 Vista Previa")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    st.divider()
                    
                    zip_data = crear_zip_desde_archivos(archivos_generados)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.download_button(
                            f"📥 DESCARGAR ZIP - PASO 2 ({len(archivos_generados)} archivos)",
                            zip_data,
                            "PASO_2_Validaciones.zip",
                            "application/zip",
                            use_container_width=True,
                            type="primary"
                        )
                    with col2:
                        if st.button("▶️ Siguiente", use_container_width=True):
                            st.session_state.paso_actual = 3
                            st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("🔍 Ver detalles"):
                    import traceback
                    st.code(traceback.format_exc())

# ============================================================================
# PASO 3: CIE-10
# ============================================================================
def paso3():
    mostrar_header_principal()
    
    st.markdown("""
    <div class="paso-header">
        <h2>🏥 PASO 3: Merge con CIE-10</h2>
        <p>Enriquecimiento con clasificación CIE-10 y generación de alertas diagnósticas</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ ¿Qué hace este paso?", expanded=False):
        st.write("**📥 Archivos de Entrada:**")
        st.write("• CSV del Paso 2 (Relación Laboral con Validaciones)")
        st.write("• Excel CIE-10 (Clasificación de diagnósticos)")

        st.write("**📤 Archivos de Salida:**")
        st.write("• ausentismos_completo_con_cie10.csv")
        st.write("• ALERTA_DIAGNOSTICO.xlsx")

        st.write("**🔧 Procesos Ejecutados:**")
        st.write("• Merge LEFT con tabla CIE-10")
        st.write("• Validación de diagnósticos requeridos")
        st.write("• Generación de alertas por falta de diagnóstico")
    
    st.warning("🔴 Este paso requiere 2 archivos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Archivo 1")
        csv_paso2 = st.file_uploader(
            "CSV del Paso 2", 
            type=['csv'], 
            key="csv3",
            help="Archivo relacion_laboral_con_validaciones.csv"
        )
    
    with col2:
        st.subheader("📤 Archivo 2")
        excel_cie10 = st.file_uploader(
            "Excel CIE-10",
            type=['xlsx', 'xls'],
            key="excel_cie10",
            help="Archivo CIE 10 - AJUSTADO - NÓMINA.xlsx"
        )

    if csv_paso2 and excel_cie10:
        st.divider()
        st.success("✅ Los 2 archivos están listos")
        
        if st.button("🚀 PROCESAR ARCHIVOS", use_container_width=True, type="primary"):
            try:
                with st.spinner('⏳ Procesando merge con CIE-10...'):
                    temp_dir = tempfile.mkdtemp()
                    
                    csv_path = os.path.join(temp_dir, "relacion_laboral_con_validaciones.csv")
                    cie10_path = os.path.join(temp_dir, "CIE10.xlsx")
                    
                    with open(csv_path, "wb") as f:
                        f.write(csv_paso2.getbuffer())
                    with open(cie10_path, "wb") as f:
                        f.write(excel_cie10.getbuffer())
                    
                    import auditoria_ausentismos_part3 as part3
                    import importlib
                    importlib.reload(part3)

                    part3.ruta_relacion_laboral = csv_path
                    part3.ruta_cie10 = cie10_path
                    part3.directorio_salida = temp_dir
                    part3.archivo_final = "ausentismos_completo_con_cie10.csv"
                    part3.ruta_completa_salida = os.path.join(temp_dir, "ausentismos_completo_con_cie10.csv")

                    # CAPTURAR SALIDA DE PRINT() Y LOGS PARA MOSTRAR EN STREAMLIT
                    import sys
                    from io import StringIO

                    st.write("🔄 Iniciando procesamiento del Paso 3...")

                    # Crear buffer para capturar prints
                    old_stdout = sys.stdout
                    sys.stdout = captured_output = StringIO()

                    try:
                        df_resultado = part3.procesar_todo()
                    finally:
                        # Restaurar stdout
                        sys.stdout = old_stdout

                        # Obtener y mostrar la salida capturada
                        output_text = captured_output.getvalue()

                        if output_text:
                            with st.expander("📋 VER LOG COMPLETO DEL PROCESAMIENTO", expanded=True):
                                st.code(output_text, language="text")
                    
                    if df_resultado is not None:
                        st.success("✅ Proceso completado exitosamente")

                        alertas = (df_resultado['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum() if 'alerta_diagnostico' in df_resultado.columns else 0
                        con_cie = df_resultado['cie10_codigo'].notna().sum() if 'cie10_codigo' in df_resultado.columns else 0

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Total Registros", f"{len(df_resultado):,}")
                        with col2:
                            st.metric("🚨 Alertas Diagnóstico", alertas)
                        with col3:
                            st.metric("🏥 Con CIE-10", con_cie)
                        with col4:
                            porcentaje_cie = (con_cie / len(df_resultado) * 100) if len(df_resultado) > 0 else 0
                            st.metric("📊 % CIE-10", f"{porcentaje_cie:.1f}%")
                        
                        st.divider()
                        st.subheader("👀 Vista Previa de Datos")
                        st.dataframe(df_resultado.head(10), use_container_width=True)
                        
                        if alertas > 0:
                            st.divider()
                            st.warning(f"⚠️ Se encontraron {alertas} registros con ALERTA DIAGNOSTICO")
                            
                            with st.expander("Ver registros con alerta"):
                                df_alertas_view = df_resultado[df_resultado['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO']
                                st.dataframe(df_alertas_view[['id_personal', 'external_name_label', 'alerta_diagnostico']].head(20))
                        
                        st.divider()
                        st.subheader("📦 Descargar Resultados")

                        archivo_final = os.path.join(temp_dir, "ausentismos_completo_con_cie10.csv")
                        archivo_alertas = os.path.join(temp_dir, "ALERTA_DIAGNOSTICO.xlsx")
                        archivo_log = "auditoria_part3.log"

                        archivos = [archivo_final]
                        if os.path.exists(archivo_alertas):
                            archivos.append(archivo_alertas)

                        # Agregar archivo de log si existe
                        if os.path.exists(archivo_log):
                            archivos.append(archivo_log)
                            st.info(f"📄 El ZIP incluye el archivo de log: {archivo_log}")

                        zip_data = crear_zip_desde_archivos(archivos)
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.download_button(
                                f"📥 DESCARGAR ZIP - PASO 3 ({len(archivos)} archivo{'s' if len(archivos) > 1 else ''})",
                                zip_data,
                                "PASO_3_CIE10.zip",
                                "application/zip",
                                use_container_width=True,
                                type="primary"
                            )
                        with col2:
                            if st.button("▶️ Siguiente", use_container_width=True):
                                st.session_state.paso_actual = 4
                                st.rerun()
                        
                        st.balloons()
                    else:
                        st.error("❌ Error en el procesamiento")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("🔍 Ver detalles del error"):
                    import traceback
                    st.code(traceback.format_exc())

# ============================================================================
# PASO 4: ANÁLISIS 30 DÍAS CON PONDERACIÓN
# ============================================================================
def paso4():
    mostrar_header_principal()
    
    st.markdown("""
    <div class="paso-header">
        <h2>📊 PASO 4: Análisis de 30 Días con Ponderación</h2>
        <p>Filtrado de registros únicos y análisis de relación con ponderación 25% por columna</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("ℹ️ ¿Qué hace este paso?", expanded=False):
        st.write("**📥 Archivos de Entrada:**")
        st.write("• CSV del Paso 3 (ausentismos_completo_con_cie10.csv)")
        
        st.write("**📤 Archivos de Salida:**")
        st.write("• Registros_unicos.csv - Registros únicos por id_personal filtrados por códigos")
        st.write("• reporte_30_dias.csv - Análisis de ventana de 30 días con ponderación")
        
        st.write("**🔧 Procesos Ejecutados:**")
        st.write("• Filtrado por códigos específicos: [203, 202, 216, 210, 220, 201, 200, 383]")
        st.write("• Extracción de registros únicos por id_personal")
        st.write("• Análisis de ventana de 30 días antes del último registro")
        st.write("• Cálculo de porcentaje de relación con ponderación:")
        st.write("  - GRUPO: 25%")
        st.write("  - Clasificación Sistemas JMC: 25%")
        st.write("  - SEGMENTO: 25%")
        st.write("  - Clasificación Partes JMC: 25%")
        
        st.write("**📊 Matriz de Códigos:**")
        st.write("• Se usa el archivo datos_numericos.csv del repositorio")
    
    st.warning("🔴 Este paso requiere 1 archivo")
    
    st.subheader("📤 Archivo de Entrada")
    csv_paso3 = st.file_uploader(
        "CSV del Paso 3 (ausentismos_completo_con_cie10.csv)",
        type=['csv'],
        key="csv4",
        help="Archivo completo con CIE-10 del Paso 3"
    )
    
    st.divider()
    st.subheader("⚙️ Configuración del Análisis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Códigos a Filtrar:**")
        st.code("203, 202, 216, 210, 220, 201, 200, 383")
    
    with col2:
        st.info("**Ventana de Análisis:**")
        st.metric("Días hacia atrás", "30 días")
    
    st.divider()
    st.subheader("📅 Filtro de Fechas para Reporte 30 Días (Opcional)")
    st.caption("Filtra por AMBAS columnas: fecha_ultima Y start_date")
    
    usar_filtro = st.checkbox("🔍 Activar filtro de fechas", value=False)
    
    fecha_ultima_inicio = None
    fecha_ultima_fin = None
    start_date_inicio = None
    start_date_fin = None
    
    if usar_filtro:
        st.markdown("### 📋 Rango para: **fecha_ultima**")
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            fecha_ultima_inicio = st.date_input(
                "Fecha Inicio (fecha_ultima)",
                value=None,
                format="DD/MM/YYYY",
                key="fecha_ultima_inicio",
                help="Inicio del rango para fecha_ultima"
            )
        
        with col_f2:
            fecha_ultima_fin = st.date_input(
                "Fecha Fin (fecha_ultima)",
                value=None,
                format="DD/MM/YYYY",
                key="fecha_ultima_fin",
                help="Fin del rango para fecha_ultima"
            )
        
        st.markdown("### 📋 Rango para: **start_date**")
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            start_date_inicio = st.date_input(
                "Fecha Inicio (start_date)",
                value=None,
                format="DD/MM/YYYY",
                key="start_date_inicio",
                help="Inicio del rango para start_date"
            )
        
        with col_s2:
            start_date_fin = st.date_input(
                "Fecha Fin (start_date)",
                value=None,
                format="DD/MM/YYYY",
                key="start_date_fin",
                help="Fin del rango para start_date"
            )
        
        # Mostrar resumen del filtro
        tiene_filtro_fecha_ultima = fecha_ultima_inicio or fecha_ultima_fin
        tiene_filtro_start_date = start_date_inicio or start_date_fin
        
        if tiene_filtro_fecha_ultima or tiene_filtro_start_date:
            st.divider()
            st.info("📊 **Resumen del Filtro:**")
            
            if tiene_filtro_fecha_ultima:
                if fecha_ultima_inicio and fecha_ultima_fin:
                    st.write(f"✅ **fecha_ultima**: {fecha_ultima_inicio.strftime('%d/%m/%Y')} → {fecha_ultima_fin.strftime('%d/%m/%Y')}")
                elif fecha_ultima_inicio:
                    st.write(f"✅ **fecha_ultima**: >= {fecha_ultima_inicio.strftime('%d/%m/%Y')}")
                elif fecha_ultima_fin:
                    st.write(f"✅ **fecha_ultima**: <= {fecha_ultima_fin.strftime('%d/%m/%Y')}")
            
            if tiene_filtro_start_date:
                if start_date_inicio and start_date_fin:
                    st.write(f"✅ **start_date**: {start_date_inicio.strftime('%d/%m/%Y')} → {start_date_fin.strftime('%d/%m/%Y')}")
                elif start_date_inicio:
                    st.write(f"✅ **start_date**: >= {start_date_inicio.strftime('%d/%m/%Y')}")
                elif start_date_fin:
                    st.write(f"✅ **start_date**: <= {start_date_fin.strftime('%d/%m/%Y')}")
    
    if csv_paso3:
        st.divider()
        
        if st.button("🚀 PROCESAR ANÁLISIS", use_container_width=True, type="primary"):
            try:
                with st.spinner('⏳ Ejecutando análisis de 30 días...'):
                    temp_dir = tempfile.mkdtemp()
                    
                    # Guardar el archivo subido
                    csv_path_original = os.path.join(temp_dir, "ausentismos_completo_con_cie10.csv")
                    with open(csv_path_original, "wb") as f:
                        f.write(csv_paso3.getbuffer())

                    # ============================================================================
                    # PRE-FILTRADO SI HAY FILTROS ACTIVADOS
                    # ============================================================================
                    csv_path_a_procesar = csv_path_original

                    if usar_filtro and (fecha_ultima_inicio and fecha_ultima_fin and start_date_inicio):
                        st.info("🔍 Aplicando pre-filtrado antes del análisis de 30 días")

                        # Leer CSV completo
                        df_completo = pd.read_csv(csv_path_original, encoding='utf-8-sig', sep=';')
                        st.caption(f"📊 Registros totales: {len(df_completo):,}")

                        # Convertir fechas
                        df_completo['last_approval_status_date'] = pd.to_datetime(
                            df_completo['last_approval_status_date'],
                            format='%d/%m/%Y',
                            dayfirst=True,
                            errors='coerce'
                        )
                        df_completo['start_date'] = pd.to_datetime(
                            df_completo['start_date'],
                            format='%d/%m/%Y',
                            dayfirst=True,
                            errors='coerce'
                        )

                        # PASO 1: Filtrar por last_approval_status_date
                        fu_inicio_dt = pd.to_datetime(fecha_ultima_inicio)
                        fu_fin_dt = pd.to_datetime(fecha_ultima_fin)

                        df_filtrado_fecha = df_completo[
                            (df_completo['last_approval_status_date'] >= fu_inicio_dt) &
                            (df_completo['last_approval_status_date'] <= fu_fin_dt)
                        ].copy()
                        st.caption(f"✅ Paso 1: {len(df_filtrado_fecha):,} registros con fecha_ultima en rango")

                        # PASO 2: Extraer IDs únicos
                        ids_validos = df_filtrado_fecha['id_personal'].unique()
                        st.caption(f"✅ Paso 2: {len(ids_validos):,} IDs únicos")

                        # PASO 3: Filtrar base completa por esos IDs
                        df_filtrado_ids = df_completo[df_completo['id_personal'].isin(ids_validos)].copy()
                        st.caption(f"✅ Paso 3: {len(df_filtrado_ids):,} registros con esos IDs")

                        # PASO 4: Filtrar por start_date (inicio mes → fin mes)
                        import calendar
                        from datetime import date
                        ultimo_dia = calendar.monthrange(start_date_inicio.year, start_date_inicio.month)[1]
                        start_date_fin_auto = date(start_date_inicio.year, start_date_inicio.month, ultimo_dia)

                        sd_inicio_dt = pd.to_datetime(start_date_inicio)
                        sd_fin_dt = pd.to_datetime(start_date_fin_auto)

                        df_filtrado_final = df_filtrado_ids[
                            (df_filtrado_ids['start_date'] >= sd_inicio_dt) &
                            (df_filtrado_ids['start_date'] <= sd_fin_dt)
                        ].copy()
                        st.caption(f"✅ Paso 4: {len(df_filtrado_final):,} registros con start_date en mes")

                        # PASO 5: Ordenar
                        df_filtrado_final = df_filtrado_final.sort_values(
                            by=['id_personal', 'start_date'],
                            ascending=[True, False]
                        )
                        st.caption(f"✅ Paso 5: Ordenado correctamente")

                        # Convertir fechas de vuelta a string
                        df_filtrado_final['last_approval_status_date'] = df_filtrado_final['last_approval_status_date'].dt.strftime('%d/%m/%Y')
                        df_filtrado_final['start_date'] = df_filtrado_final['start_date'].dt.strftime('%d/%m/%Y')

                        # Guardar CSV filtrado
                        csv_path_filtrado = os.path.join(temp_dir, "ausentismos_PREFILTRADO.csv")
                        df_filtrado_final.to_csv(csv_path_filtrado, index=False, encoding='utf-8-sig', sep=';')

                        csv_path_a_procesar = csv_path_filtrado
                        st.success(f"✅ Pre-filtrado completo: {len(df_completo):,} → {len(df_filtrado_final):,} registros")

                    # Importar y ejecutar el procesamiento
                    import auditoria_ausentismos_part4 as part4
                    import importlib
                    importlib.reload(part4)

                    # Configurar rutas (usar CSV filtrado si existe)
                    part4.ruta_entrada = csv_path_a_procesar
                    part4.directorio_salida = temp_dir
                    part4.ruta_salida_unicos = os.path.join(temp_dir, "Registros_unicos.csv")
                    part4.ruta_salida_30dias = os.path.join(temp_dir, "reporte_30_dias.csv")

                    # DEBUG: Mostrar configuración antes de procesar
                    st.info(f"📂 Archivo a procesar: {os.path.basename(csv_path_a_procesar)}")
                    st.info(f"📁 Directorio salida: {temp_dir}")

                    # Ejecutar procesamiento
                    st.write("🔄 Iniciando análisis de 30 días sobre datos filtrados...")

                    # CAPTURAR SALIDA DE PRINT() PARA MOSTRAR EN STREAMLIT
                    import sys
                    from io import StringIO

                    # Crear buffer para capturar prints
                    old_stdout = sys.stdout
                    sys.stdout = captured_output = StringIO()

                    try:
                        df_unicos, df_reporte_30dias = part4.procesar_analisis_completo()
                    finally:
                        # Restaurar stdout
                        sys.stdout = old_stdout

                        # Obtener y mostrar la salida capturada
                        output_text = captured_output.getvalue()

                        if output_text:
                            with st.expander("📋 VER LOG COMPLETO DEL PROCESAMIENTO", expanded=True):
                                st.code(output_text, language="text")

                    # IMPORTANTE: Recargar el archivo con el separador correcto
                    # porque part4 guarda con sep=';'
                    archivo_30dias_temp = os.path.join(temp_dir, "reporte_30_dias.csv")
                    if os.path.exists(archivo_30dias_temp):
                        df_reporte_30dias = pd.read_csv(
                            archivo_30dias_temp, 
                            sep=';', 
                            encoding='utf-8-sig',
                            decimal=','
                        )
                    
                    if df_unicos is not None and df_reporte_30dias is not None:
                        st.success("✅ Análisis completado exitosamente")
                        
                        # DEBUG: Mostrar información del DataFrame
                        with st.expander("🔍 DEBUG - Información del DataFrame", expanded=False):
                            st.write(f"**Columnas:** {', '.join(df_reporte_30dias.columns.tolist())}")
                            st.write(f"**Total registros:** {len(df_reporte_30dias):,}")
                            st.write(f"**Primera fecha_ultima:** '{df_reporte_30dias['fecha_ultima'].iloc[0]}'")
                            st.write(f"**Primera start_date:** '{df_reporte_30dias['start_date'].iloc[0]}'")
                            st.dataframe(df_reporte_30dias.head(3))
                        
                        # ============================================================================
                        # NOTA: El filtrado ya se aplicó ANTES del análisis
                        # El reporte de 30 días ya contiene solo los datos filtrados
                        # ============================================================================
                        df_reporte_filtrado = None

                        # Si se aplicó pre-filtrado, el reporte ya está filtrado
                        if usar_filtro and (fecha_ultima_inicio and fecha_ultima_fin and start_date_inicio):
                            st.info("✅ El análisis de 30 días se ejecutó sobre datos YA filtrados")
                            df_reporte_filtrado = df_reporte_30dias.copy()

                        # Mantener lógica antigua comentada por si se necesita
                        if False:  # Desactivado - ahora se filtra ANTES
                            st.info("🔍 Aplicando lógica de filtrado avanzado")

                            # Verificar que existan las columnas
                            if 'fecha_ultima' not in df_reporte_30dias.columns or 'start_date' not in df_reporte_30dias.columns:
                                st.error(f"❌ ERROR: Columnas no encontradas. Disponibles: {df_reporte_30dias.columns.tolist()}")
                            else:
                                registros_antes = len(df_reporte_30dias)

                                try:
                                    # Convertir columnas a datetime
                                    df_temp = df_reporte_30dias.copy()
                                    df_temp['fecha_ultima_dt'] = pd.to_datetime(
                                        df_temp['fecha_ultima'],
                                        format='%d/%m/%Y',
                                        dayfirst=True,
                                        errors='coerce'
                                    )
                                    df_temp['start_date_dt'] = pd.to_datetime(
                                        df_temp['start_date'],
                                        format='%d/%m/%Y',
                                        dayfirst=True,
                                        errors='coerce'
                                    )

                                    # ============================================================================
                                    # PASO 1: Filtrar por fecha_ultima (last_approval_status_date)
                                    # ============================================================================
                                    if fecha_ultima_inicio and fecha_ultima_fin:
                                        fu_inicio_dt = pd.to_datetime(fecha_ultima_inicio)
                                        fu_fin_dt = pd.to_datetime(fecha_ultima_fin)

                                        df_filtrado_fecha_ultima = df_temp[
                                            (df_temp['fecha_ultima_dt'] >= fu_inicio_dt) &
                                            (df_temp['fecha_ultima_dt'] <= fu_fin_dt)
                                        ].copy()

                                        st.caption(f"✅ Paso 1: Filtrado fecha_ultima: {fu_inicio_dt.strftime('%d/%m/%Y')} → {fu_fin_dt.strftime('%d/%m/%Y')}")
                                        st.caption(f"   Registros con fecha_ultima en rango: {len(df_filtrado_fecha_ultima):,}")

                                        # ============================================================================
                                        # PASO 2: Extraer id_personal únicos
                                        # ============================================================================
                                        ids_validos = df_filtrado_fecha_ultima['id_personal'].unique()
                                        st.caption(f"✅ Paso 2: IDs únicos extraídos: {len(ids_validos):,}")

                                        # ============================================================================
                                        # PASO 3: Filtrar base completa por esos id_personal
                                        # ============================================================================
                                        df_filtrado_ids = df_temp[df_temp['id_personal'].isin(ids_validos)].copy()
                                        st.caption(f"✅ Paso 3: Registros con esos IDs en base completa: {len(df_filtrado_ids):,}")

                                        # ============================================================================
                                        # PASO 4: Filtrar por start_date (inicio mes hasta fin mes) - SIN end_date
                                        # ============================================================================
                                        if start_date_inicio:
                                            # Calcular fin de mes automático
                                            import calendar
                                            from datetime import date
                                            ultimo_dia = calendar.monthrange(start_date_inicio.year, start_date_inicio.month)[1]
                                            start_date_fin_auto = date(start_date_inicio.year, start_date_inicio.month, ultimo_dia)

                                            sd_inicio_dt = pd.to_datetime(start_date_inicio)
                                            sd_fin_dt = pd.to_datetime(start_date_fin_auto)

                                            df_reporte_filtrado = df_filtrado_ids[
                                                (df_filtrado_ids['start_date_dt'] >= sd_inicio_dt) &
                                                (df_filtrado_ids['start_date_dt'] <= sd_fin_dt)
                                            ].copy()

                                            st.caption(f"✅ Paso 4: Filtrado start_date: {sd_inicio_dt.strftime('%d/%m/%Y')} → {sd_fin_dt.strftime('%d/%m/%Y')} (fin mes automático)")
                                            st.caption(f"   Registros finales: {len(df_reporte_filtrado):,}")
                                        else:
                                            # Si no hay start_date, mantener todos los de paso 3
                                            df_reporte_filtrado = df_filtrado_ids.copy()

                                        # ============================================================================
                                        # PASO 5: Ordenar - id_personal (asc), start_date (desc)
                                        # ============================================================================
                                        df_reporte_filtrado = df_reporte_filtrado.sort_values(
                                            by=['id_personal', 'start_date_dt'],
                                            ascending=[True, False]  # id_personal menor→mayor, start_date reciente→antiguo
                                        )
                                        st.caption(f"✅ Paso 5: Ordenado por id_personal (asc) y start_date (desc)")

                                    else:
                                        # Si no hay filtro de fecha_ultima completo, mantener todos
                                        df_reporte_filtrado = df_temp.copy()
                                        st.warning("⚠️ Se requieren fecha_ultima inicio Y fin para aplicar el filtro avanzado")

                                    # Eliminar columnas auxiliares
                                    df_reporte_filtrado = df_reporte_filtrado.drop(['fecha_ultima_dt', 'start_date_dt'], axis=1)

                                    registros_despues = len(df_reporte_filtrado)
                                    
                                    if registros_despues == 0:
                                        st.error(f"❌ El filtro eliminó TODOS los registros.")
                                        st.warning("💡 Verifica que los rangos de fechas sean correctos y estén dentro de los datos disponibles")
                                        df_reporte_filtrado = None
                                    else:
                                        # Guardar archivo filtrado
                                        ruta_filtrado = os.path.join(temp_dir, "reporte_30_dias_FILTRADO.csv")
                                        
                                        df_reporte_filtrado.to_csv(
                                            ruta_filtrado,
                                            index=False,
                                            sep=';',
                                            encoding='utf-8-sig',
                                            decimal=',',
                                            quoting=1,
                                            lineterminator='\n'
                                        )
                                        
                                        st.success(f"✅ Filtrado exitoso: {registros_antes:,} → {registros_despues:,} registros")
                                        
                                        # Mostrar muestra del archivo filtrado
                                        with st.expander("👀 Ver muestra del archivo filtrado (primeros 10 registros)"):
                                            st.dataframe(df_reporte_filtrado[['id_personal', 'fecha_ultima', 'start_date', 'porcentaje_relacion']].head(10))
                                
                                except Exception as e:
                                    st.error(f"❌ Error al aplicar filtros: {str(e)}")
                                    import traceback
                                    st.code(traceback.format_exc())
                                    df_reporte_filtrado = None
                        
                        # Métricas principales
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("👥 IDs Únicos", f"{len(df_unicos):,}")
                        with col2:
                            if df_reporte_filtrado is not None:
                                st.metric("📅 Filtrados", f"{len(df_reporte_filtrado):,}")
                            else:
                                con_codigos = len(df_reporte_30dias[df_reporte_30dias['cantidad_codigos'] > 0])
                                st.metric("📊 Con Códigos", f"{con_codigos:,}")
                        with col3:
                            if df_reporte_filtrado is not None:
                                sin_codigos_f = len(df_reporte_filtrado[df_reporte_filtrado['cantidad_codigos'] == 0])
                                st.metric("⚠️ Sin Códigos (Filtrado)", f"{sin_codigos_f:,}")
                            else:
                                sin_codigos = len(df_reporte_30dias[df_reporte_30dias['cantidad_codigos'] == 0])
                                st.metric("⚠️ Sin Códigos", f"{sin_codigos:,}")
                        with col4:
                            if df_reporte_filtrado is not None:
                                promedio_f = df_reporte_filtrado['porcentaje_relacion'].mean()
                                st.metric("📈 % Promedio (Filtrado)", f"{promedio_f:.1f}%")
                            else:
                                promedio = df_reporte_30dias['porcentaje_relacion'].mean()
                                st.metric("📈 % Promedio", f"{promedio:.1f}%")
                        
                        st.divider()
                        
                        # Vista previa de registros únicos
                        st.subheader("👀 Vista Previa - Registros Únicos")
                        st.dataframe(df_unicos.head(10), use_container_width=True)
                        
                        st.divider()
                        
                        # Vista previa de reporte 30 días
                        st.subheader("👀 Vista Previa - Reporte 30 Días")
                        if df_reporte_filtrado is not None:
                            st.caption("⚠️ Mostrando datos FILTRADOS por fechas")
                            st.dataframe(df_reporte_filtrado.head(10), use_container_width=True)
                        else:
                            st.caption("Mostrando datos SIN filtro")
                            st.dataframe(df_reporte_30dias.head(10), use_container_width=True)
                        
                        st.divider()
                        
                        # Estadísticas adicionales
                        st.subheader("📊 Estadísticas del Análisis")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Distribución de Porcentajes:**")
                            
                            rangos = [
                                (0, 25, "0-25%"),
                                (25, 50, "25-50%"),
                                (50, 75, "50-75%"),
                                (75, 101, "75-100%")
                            ]
                            
                            for min_val, max_val, etiqueta in rangos:
                                count = len(df_reporte_30dias[
                                    (df_reporte_30dias['porcentaje_relacion'] >= min_val) & 
                                    (df_reporte_30dias['porcentaje_relacion'] < max_val)
                                ])
                                st.metric(etiqueta, f"{count:,}")
                        
                        with col2:
                            st.write("**Top 5 IDs con Mayor Relación:**")
                            df_para_top5 = df_reporte_filtrado if df_reporte_filtrado is not None else df_reporte_30dias
                            top5 = df_para_top5.nlargest(5, 'porcentaje_relacion')[
                                ['id_personal', 'porcentaje_relacion', 'cantidad_codigos']
                            ]
                            st.dataframe(top5, use_container_width=True, hide_index=True)
                        
                        st.divider()
                        st.subheader("📦 Descargar Resultados")
                        
                        # Crear ZIP con archivos
                        archivo_unicos = os.path.join(temp_dir, "Registros_unicos.csv")
                        archivo_30dias = os.path.join(temp_dir, "reporte_30_dias.csv")
                        archivo_30dias_filtrado = os.path.join(temp_dir, "reporte_30_dias_FILTRADO.csv")
                        
                        archivos = []
                        if os.path.exists(archivo_unicos):
                            archivos.append(archivo_unicos)
                        if os.path.exists(archivo_30dias):
                            archivos.append(archivo_30dias)
                        if df_reporte_filtrado is not None and os.path.exists(archivo_30dias_filtrado):
                            archivos.append(archivo_30dias_filtrado)
                        
                        if archivos:
                            zip_data = crear_zip_desde_archivos(archivos)
                            
                            num_archivos = len(archivos)
                            label_descarga = f"📥 DESCARGAR ZIP - PASO 4 ({num_archivos} archivo{'s' if num_archivos > 1 else ''})"
                            
                            if df_reporte_filtrado is not None:
                                st.info("📦 El ZIP incluye el archivo FILTRADO: reporte_30_dias_FILTRADO.csv")
                            
                            st.download_button(
                                label_descarga,
                                zip_data,
                                "PASO_4_Analisis_30_Dias.zip",
                                "application/zip",
                                use_container_width=True,
                                type="primary"
                            )
                            
                            st.balloons()
                            st.success("✅ ¡Proceso completo! Todos los pasos finalizados.")
                        else:
                            st.error("❌ No se encontraron archivos para descargar")
                    else:
                        st.error("❌ Error en el procesamiento")
                        st.error("⚠️ df_unicos o df_reporte_30dias es None")
                        st.write(f"df_unicos is None: {df_unicos is None}")
                        st.write(f"df_reporte_30dias is None: {df_reporte_30dias is None}")

            except Exception as e:
                st.error("=" * 50)
                st.error("🔴 ERROR DETECTADO EN PASO 4")
                st.error("=" * 50)
                st.error(f"**Tipo de error:** {type(e).__name__}")
                st.error(f"**Mensaje:** {str(e)}")

                with st.expander("🔍 VER TRACEBACK COMPLETO (ABRIR ESTO)", expanded=True):
                    import traceback
                    error_traceback = traceback.format_exc()
                    st.code(error_traceback, language="python")

                    # Agregar información adicional
                    st.divider()
                    st.write("**📍 Información adicional de debug:**")
                    try:
                        st.write(f"- Archivo CSV cargado: {csv_path if 'csv_path' in locals() else 'No disponible'}")
                        st.write(f"- Archivo existe: {os.path.exists(csv_path) if 'csv_path' in locals() else 'N/A'}")
                        st.write(f"- Tamaño archivo: {os.path.getsize(csv_path) if 'csv_path' in locals() and os.path.exists(csv_path) else 'N/A'} bytes")
                        if 'csv_path' in locals() and os.path.exists(csv_path):
                            df_test = pd.read_csv(csv_path, encoding='utf-8-sig', nrows=1)
                            st.write(f"- Columnas en CSV: {len(df_test.columns)}")
                            st.write(f"- Primeras columnas: {list(df_test.columns[:5])}")
                    except Exception as debug_error:
                        st.write(f"- Error al obtener información del archivo: {str(debug_error)}")

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.title("🧭 Navegación")
    
    st.divider()
    
    progreso = (st.session_state.paso_actual - 1) / 3 * 100
    st.progress(progreso / 100)
    st.write(f"**Progreso: {progreso:.0f}%**")
    
    st.divider()
    
    if st.button("📄 PASO 1: Procesamiento", use_container_width=True, 
                 disabled=(st.session_state.paso_actual == 1)):
        st.session_state.paso_actual = 1
        st.rerun()
    
    if st.button("🔗 PASO 2: Validaciones", use_container_width=True,
                 disabled=(st.session_state.paso_actual == 2)):
        st.session_state.paso_actual = 2
        st.rerun()
    
    if st.button("🏥 PASO 3: CIE-10", use_container_width=True,
                 disabled=(st.session_state.paso_actual == 3)):
        st.session_state.paso_actual = 3
        st.rerun()
    
    if st.button("📊 PASO 4: Análisis 30 Días", use_container_width=True,
                 disabled=(st.session_state.paso_actual == 4)):
        st.session_state.paso_actual = 4
        st.rerun()
    
    st.divider()
    
    st.info("""
    **📋 Flujo del Proceso**
    
    **PASO 1:** CSV + Excel → Procesado
    
    **PASO 2:** CSV + Personal → Validaciones
    
    **PASO 3:** CSV + CIE-10 → Completo
    
    **PASO 4:** CSV → Análisis 30 Días
    """)
    
    st.divider()
    
    st.caption("📧 **Soporte**")
    st.caption("Grupo Jerónimo Martins")

# ============================================================================
# MAIN
# ============================================================================
if st.session_state.paso_actual == 1:
    paso1()
elif st.session_state.paso_actual == 2:
    paso2()
elif st.session_state.paso_actual == 3:
    paso3()
elif st.session_state.paso_actual == 4:
    paso4()
