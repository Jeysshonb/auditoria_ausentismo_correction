import pandas as pd
import os

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

    # Para Excel, cambiar extensión de .xlsx a .csv
    if ruta_archivo.endswith('.xlsx'):
        ruta_csv = ruta_archivo.replace('.xlsx', '.csv')
        df_export.to_csv(ruta_csv, index=False, encoding='utf-8-sig', sep=';')
        return ruta_csv

    return ruta_archivo

print("="*80)
print("PASO 1: MERGE DE AUSENTISMO CON RELACIÓN LABORAL")
print("="*80)

# ============================================================================
# PARTE 1: MERGE DE ARCHIVOS
# ============================================================================

# Rutas de archivos para el merge
csv_ausentismo = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida\ausentismo_procesado_completo_v2.csv"
excel_personal = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_planos\MD_26082025.XLSX"
carpeta_salida = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida"
archivo_relacion_laboral = os.path.join(carpeta_salida, "relacion_laboral.csv")

print("\nLeyendo archivo de ausentismo...")
df_ausentismo = pd.read_csv(csv_ausentismo)
print(f"Registros de ausentismo: {len(df_ausentismo)}")

print("\nLeyendo archivo de personal (Excel)...")
df_personal = pd.read_excel(excel_personal)
print(f"Registros de personal: {len(df_personal)}")

# Mostrar las columnas del archivo de personal para verificar
print("\nColumnas disponibles en el archivo de personal:")
print(df_personal.columns.tolist())

# Verificar si existe la columna 'Nº pers.' o variaciones
col_num_pers = None
for col in df_personal.columns:
    if 'pers' in col.lower() or 'personal' in col.lower():
        print(f"\nColumna encontrada relacionada con personal: '{col}'")
        col_num_pers = col
        break

if col_num_pers is None:
    print("\n⚠️ ADVERTENCIA: No se encontró una columna clara para 'Nº pers.'")
    print("Por favor, verifica el nombre exacto de la columna en el Excel")
else:
    # Verificar si existe la columna 'Relación laboral'
    col_relacion = None
    for col in df_personal.columns:
        if 'relaci' in col.lower() and 'labor' in col.lower():
            col_relacion = col
            print(f"Columna encontrada para relación laboral: '{col}'")
            break
    
    if col_relacion is None:
        print("\n⚠️ ADVERTENCIA: No se encontró la columna 'Relación laboral'")
        print("Columnas disponibles:")
        for col in df_personal.columns:
            print(f"  - {col}")
    else:
        # Convertir ambas columnas a string para el merge
        df_ausentismo['id_personal'] = df_ausentismo['id_personal'].astype(str)
        df_personal[col_num_pers] = df_personal[col_num_pers].astype(str)
        
        # Seleccionar solo las columnas necesarias del archivo de personal
        df_personal_reducido = df_personal[[col_num_pers, col_relacion]].copy()
        
        print(f"\nRealizando merge entre 'id_personal' y '{col_num_pers}'...")
        df_resultado = df_ausentismo.merge(
            df_personal_reducido,
            left_on='id_personal',
            right_on=col_num_pers,
            how='left'
        )
        
        # Renombrar la columna de relación laboral si es necesario
        if col_relacion != 'Relación laboral':
            df_resultado.rename(columns={col_relacion: 'Relación laboral'}, inplace=True)
        
        # Eliminar la columna duplicada del merge si existe
        if col_num_pers in df_resultado.columns and col_num_pers != 'id_personal':
            df_resultado.drop(columns=[col_num_pers], inplace=True)
        
        print(f"\nRegistros después del merge: {len(df_resultado)}")
        print(f"Registros con relación laboral: {df_resultado['Relación laboral'].notna().sum()}")
        print(f"Registros sin relación laboral: {df_resultado['Relación laboral'].isna().sum()}")
        
        # Eliminar registros sin relación laboral
        print("\nEliminando registros sin relación laboral...")
        df_resultado = df_resultado[df_resultado['Relación laboral'].notna()]
        print(f"Registros finales (solo con relación laboral): {len(df_resultado)}")
        
        print("\n✓ Proceso de merge completado exitosamente")
        
        # Mostrar una muestra del resultado
        print("\nPrimeras 3 filas del resultado:")
        print(df_resultado[['id_personal', 'nombre_completo', 'Relación laboral']].head(3))
        
        # Guardar temporalmente para las validaciones
        df_resultado.to_csv(archivo_relacion_laboral, index=False, encoding='utf-8-sig')

print("\n" + "="*80)
print("PASO 2: VALIDACIÓN SENA - GENERACIÓN DE ERRORES")
print("="*80)

# ============================================================================
# PARTE 2: VALIDACIÓN SENA
# ============================================================================

archivo_sena_errores = os.path.join(carpeta_salida, "Sena_error_validar.csv")

print("\nLeyendo archivo con relación laboral...")
df = pd.read_csv(archivo_relacion_laboral, low_memory=False)

# Convertir columnas de fecha a formato datetime (día/mes/año)
print("Convirtiendo columnas de fecha al formato correcto (día/mes/año)...")
columnas_fecha = ['start_date', 'end_date', 'last_approval_status_date', 'modificado_el', 'fse_fechas']
for col in columnas_fecha:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
        print(f"  ✓ {col} convertida a datetime")

print(f"Total de registros: {len(df)}")

# Mostrar valores únicos de Relación laboral para debug
print("\nValores únicos encontrados en 'Relación laboral':")
valores_unicos = df['Relación laboral'].value_counts()
for valor, cantidad in valores_unicos.items():
    print(f"  - '{valor}': {cantidad} registros")

# PASO 1: Filtrar SOLO por Relación laboral = Aprendizaje
print("\n" + "="*60)
print("FILTRANDO SOLO APRENDIZAJE...")
print("="*60)
df_aprendizaje = df[df['Relación laboral'].str.contains('Aprendizaje', case=False, na=False)].copy()
print(f"✓ Registros con Aprendizaje encontrados: {len(df_aprendizaje)}")

if len(df_aprendizaje) == 0:
    print("\n⚠️ NO HAY REGISTROS DE APRENDIZAJE!")
    df_vacio = pd.DataFrame(columns=df.columns)
    guardar_csv_con_fechas(df_vacio, archivo_sena_errores)
    print(f"✓ Archivo vacío creado: {archivo_sena_errores}")
else:
    # Mostrar qué conceptos tienen los aprendices
    print("\nConceptos encontrados en external_name_label para Aprendizaje:")
    conceptos_aprendizaje = df_aprendizaje['external_name_label'].value_counts()
    for concepto, cantidad in conceptos_aprendizaje.items():
        print(f"  - {concepto}: {cantidad} registro(s)")
    
    # PASO 2: Definir conceptos VÁLIDOS para SENA
    conceptos_validos_sena = [
        'Incapacidad gral SENA',
        'Licencia de Maternidad SENA',
        'Suspensión contrato SENA'
    ]
    
    print(f"\n{'='*60}")
    print(f"CONCEPTOS VÁLIDOS PARA SENA:")
    for concepto in conceptos_validos_sena:
        print(f"  ✓ {concepto}")
    print(f"{'='*60}")
    
    # PASO 3: Filtrar TODO lo que NO sea esos 3 conceptos = ERRORES
    df_errores_sena = df_aprendizaje[~df_aprendizaje['external_name_label'].isin(conceptos_validos_sena)].copy()
    
    print(f"\n{'='*60}")
    print(f"ERRORES ENCONTRADOS: {len(df_errores_sena)}")
    print(f"{'='*60}")
    
    if len(df_errores_sena) > 0:
        # Mostrar qué errores específicos se encontraron
        print("\nCONCEPTOS INCORRECTOS (ERRORES):")
        conceptos_incorrectos = df_errores_sena['external_name_label'].value_counts()
        for concepto, cantidad in conceptos_incorrectos.items():
            print(f"  ✗ {concepto}: {cantidad} registro(s)")
        
        # GUARDAR EXCEL CON TODOS LOS ERRORES
        print(f"\nGuardando Excel con errores...")
        guardar_csv_con_fechas(df_errores_sena, archivo_sena_errores)

        print(f"\n✓✓✓ ARCHIVO CREADO EXITOSAMENTE ✓✓✓")
        print(f"Ubicación: {archivo_sena_errores}")
        
        # Mostrar muestra
        print("\n" + "="*60)
        print("MUESTRA DE ERRORES (primeros 5):")
        print("="*60)
        columnas_mostrar = ['id_personal', 'nombre_completo', 'Relación laboral', 'external_name_label']
        print(df_errores_sena[columnas_mostrar].head().to_string(index=False))
    else:
        print("\n✓ NO HAY ERRORES - Todos los Aprendizaje tienen conceptos válidos")
        df_vacio = pd.DataFrame(columns=df_aprendizaje.columns)
        guardar_csv_con_fechas(df_vacio, archivo_sena_errores)
        print(f"✓ Archivo vacío creado: {archivo_sena_errores}")

print("\n" + "="*80)
print("PASO 3: VALIDACIÓN LEY 50 - GENERACIÓN DE ERRORES")
print("="*80)

# ============================================================================
# PARTE 3: VALIDACIÓN LEY 50
# ============================================================================

archivo_ley50_errores = os.path.join(carpeta_salida, "Ley_50_error_validar.csv")

# Filtrar SOLO por Relación laboral = Ley 50
print("\n" + "="*60)
print("FILTRANDO SOLO LEY 50...")
print("="*60)
df_ley50 = df[df['Relación laboral'].str.contains('Ley 50', case=False, na=False)].copy()
print(f"✓ Registros con Ley 50 encontrados: {len(df_ley50)}")

if len(df_ley50) == 0:
    print("\n⚠️ NO HAY REGISTROS DE LEY 50!")
    df_vacio = pd.DataFrame(columns=df.columns)
    guardar_csv_con_fechas(df_vacio, archivo_ley50_errores)
    print(f"✓ Archivo vacío creado: {archivo_ley50_errores}")
else:
    # Definir CÓDIGOS PROHIBIDOS para Ley 50 (usando homologacion_clase_de_ausentismo_ssf_vs_sap)
    # Incluye códigos de SENA e INTEGRAL que Ley 50 NO puede tener
    codigos_prohibidos_ley50 = [
        # Códigos de SENA
        280,  # Incapacidad gral SENA
        281,  # Incapacidad ARL SENA
        398,  # Lic Maternidad SENA
        198,  # Suspensión contrato SENA

        # Códigos de INTEGRAL
        197,  # Ausencia No Justific Int
        331,  # Calamidad Domést Integral
        333,  # Cuarent Prev. 100% Int.
        334,  # Cuarent Prev. 66.66% Intg
        203,  # Enf Gral Int SOAT
        216,  # Inc. Acci Trabajo Integra
        201,  # Inca. Enfer Gral Integral
        341,  # Ley de Luto Integral
        332,  # Lic remunerada Integral
        303,  # Licenc Mater especial Int
        301,  # Licencia Maternidad Integ
        196,  # Licencia No Remunerada In
        311,  # Licencia Paternidad Inegr
        233,  # Prorr Enf Gral Int SOAT
        251,  # Prorr Inc.Accid. Tr Integ
        231   # Prorr Inc/Enf Gral ntegra
    ]

    print(f"\n{'='*60}")
    print(f"CÓDIGOS PROHIBIDOS PARA LEY 50 (homologacion_clase_de_ausentismo_ssf_vs_sap):")
    print(f"Total códigos prohibidos: {len(codigos_prohibidos_ley50)}")
    print(f"  - Códigos SENA: 280, 281, 398, 198")
    print(f"  - Códigos INTEGRAL: 197, 331, 333, 334, 203, 216, 201, 341, 332, 303, 301, 196, 311, 233, 251, 231")
    print(f"{'='*60}")

    # Convertir la columna a numérico para comparación
    df_ley50['homologacion_clase_de_ausentismo_ssf_vs_sap'] = pd.to_numeric(
        df_ley50['homologacion_clase_de_ausentismo_ssf_vs_sap'],
        errors='coerce'
    )

    # Filtrar los que SÍ tienen esos códigos = ERRORES
    df_errores_ley50 = df_ley50[
        df_ley50['homologacion_clase_de_ausentismo_ssf_vs_sap'].isin(codigos_prohibidos_ley50)
    ].copy()
    
    print(f"\n{'='*60}")
    print(f"ERRORES ENCONTRADOS: {len(df_errores_ley50)}")
    print(f"{'='*60}")
    
    if len(df_errores_ley50) > 0:
        # Mostrar qué errores específicos se encontraron (por código y nombre)
        print("\nCÓDIGOS PROHIBIDOS ENCONTRADOS (ERRORES):")

        # Mostrar códigos encontrados
        codigos_encontrados = df_errores_ley50['homologacion_clase_de_ausentismo_ssf_vs_sap'].value_counts()
        for codigo, cantidad in codigos_encontrados.items():
            # Obtener el nombre del concepto para mostrar
            nombre_concepto = df_errores_ley50[
                df_errores_ley50['homologacion_clase_de_ausentismo_ssf_vs_sap'] == codigo
            ]['external_name_label'].iloc[0] if 'external_name_label' in df_errores_ley50.columns else 'N/A'

            # Identificar si es de SENA o INTEGRAL
            tipo = "SENA" if codigo in [280, 281, 398, 198] else "INTEGRAL"
            print(f"  ✗ Código {int(codigo)} ({nombre_concepto}) [{tipo}]: {cantidad} registro(s)")

        # GUARDAR EXCEL CON TODOS LOS ERRORES
        print(f"\nGuardando Excel con errores...")
        guardar_csv_con_fechas(df_errores_ley50, archivo_ley50_errores)

        print(f"\n✓✓✓ ARCHIVO CREADO EXITOSAMENTE ✓✓✓")
        print(f"Ubicación: {archivo_ley50_errores}")

        # Mostrar muestra
        print("\n" + "="*60)
        print("MUESTRA DE ERRORES (primeros 5):")
        print("="*60)
        columnas_mostrar = ['id_personal', 'nombre_completo', 'Relación laboral',
                           'homologacion_clase_de_ausentismo_ssf_vs_sap', 'external_name_label']
        print(df_errores_ley50[columnas_mostrar].head().to_string(index=False))
    else:
        print("\n✓ NO HAY ERRORES - Ningún registro de Ley 50 tiene conceptos prohibidos")
        df_vacio = pd.DataFrame(columns=df_ley50.columns)
        guardar_csv_con_fechas(df_vacio, archivo_ley50_errores)
        print(f"✓ Archivo vacío creado: {archivo_ley50_errores}")

print("\n" + "="*80)
print("PASO 3.1: VALIDACIÓN INTEGRAL - GENERACIÓN DE ERRORES")
print("="*80)

# ============================================================================
# PARTE 3.1: VALIDACIÓN INTEGRAL
# ============================================================================

archivo_integral_errores = os.path.join(carpeta_salida, "Integral_error_validar.csv")

# Filtrar SOLO por Relación laboral = Integral
print("\n" + "="*60)
print("FILTRANDO SOLO INTEGRAL...")
print("="*60)
df_integral = df[df['Relación laboral'].str.contains('Integral', case=False, na=False)].copy()
print(f"✓ Registros con Integral encontrados: {len(df_integral)}")

if len(df_integral) == 0:
    print("\n⚠️ NO HAY REGISTROS DE INTEGRAL!")
    df_vacio = pd.DataFrame(columns=df.columns)
    guardar_csv_con_fechas(df_vacio, archivo_integral_errores)
    print(f"✓ Archivo vacío creado: {archivo_integral_errores}")
else:
    # Definir CÓDIGOS PROHIBIDOS para Integral (usando homologacion_clase_de_ausentismo_ssf_vs_sap)
    codigos_prohibidos_integral = [
        380,  # Ausencia No Justificada
        330,  # Calamidad Doméstica
        291,  # Cuarentena Prev. 100%
        204,  # cuarentena Prev. 66.67
        202,  # Enf Gral SOAT
        215,  # Inc. Accidente de Trabajo
        210,  # Inc. Enfer. General Hospi
        220,  # Inc. Enfermed Profesional
        200,  # Inca. Enfermedad  General
        281,  # Incapacidad ARL SENA
        280,  # Incapacidad gral SENA
        340,  # Ley de Luto
        345,  # Lic Jurado Votación
        305,  # Lic Mater Interrumpida
        398,  # Lic Maternidad SENA
        302,  # Licencia Mater especial
        300,  # Licencia Maternidad
        191,  # Licencia No Remunerada
        310,  # Licencia Paternidad
        190,  # Licencia Remunerada
        232,  # Prorroga Enf Gral SOAT
        250,  # Prorroga Inc. Accid. Trab
        230,  # Prorroga Inca/Enfer Gene
        381,  # Suspensión
        198   # Suspensión contrato SENA
    ]

    print(f"\n{'='*60}")
    print(f"CÓDIGOS PROHIBIDOS PARA INTEGRAL (homologacion_clase_de_ausentismo_ssf_vs_sap):")
    print(f"Total códigos prohibidos: {len(codigos_prohibidos_integral)}")
    print(f"Códigos: {codigos_prohibidos_integral}")
    print(f"{'='*60}")

    # Convertir la columna a numérico para comparación
    df_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'] = pd.to_numeric(
        df_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'],
        errors='coerce'
    )

    # Filtrar los que SÍ tienen esos códigos = ERRORES
    df_errores_integral = df_integral[
        df_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'].isin(codigos_prohibidos_integral)
    ].copy()

    print(f"\n{'='*60}")
    print(f"ERRORES ENCONTRADOS: {len(df_errores_integral)}")
    print(f"{'='*60}")

    if len(df_errores_integral) > 0:
        # Mostrar qué errores específicos se encontraron (por código y nombre)
        print("\nCÓDIGOS PROHIBIDOS ENCONTRADOS (ERRORES):")

        # Mostrar códigos encontrados
        codigos_encontrados = df_errores_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'].value_counts()
        for codigo, cantidad in codigos_encontrados.items():
            # Obtener el nombre del concepto para mostrar
            nombre_concepto = df_errores_integral[
                df_errores_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'] == codigo
            ]['external_name_label'].iloc[0] if 'external_name_label' in df_errores_integral.columns else 'N/A'

            print(f"  ✗ Código {int(codigo)} ({nombre_concepto}): {cantidad} registro(s)")

        # GUARDAR EXCEL CON TODOS LOS ERRORES
        print(f"\nGuardando Excel con errores...")
        guardar_csv_con_fechas(df_errores_integral, archivo_integral_errores)

        print(f"\n✓✓✓ ARCHIVO CREADO EXITOSAMENTE ✓✓✓")
        print(f"Ubicación: {archivo_integral_errores}")

        # Mostrar muestra
        print("\n" + "="*60)
        print("MUESTRA DE ERRORES (primeros 5):")
        print("="*60)
        columnas_mostrar = ['id_personal', 'nombre_completo', 'Relación laboral',
                           'homologacion_clase_de_ausentismo_ssf_vs_sap', 'external_name_label']
        print(df_errores_integral[columnas_mostrar].head().to_string(index=False))
    else:
        print("\n✓ NO HAY ERRORES - Ningún registro de Integral tiene conceptos prohibidos")
        df_vacio = pd.DataFrame(columns=df_integral.columns)
        guardar_csv_con_fechas(df_vacio, archivo_integral_errores)
        print(f"✓ Archivo vacío creado: {archivo_integral_errores}")

print("\n" + "="*80)
print("PASO 4: CREACIÓN DE COLUMNAS DE VALIDACIÓN")
print("="*80)

# ============================================================================
# PARTE 4: CREAR COLUMNAS DE VALIDACIÓN
# ============================================================================

archivo_con_validaciones = os.path.join(carpeta_salida, "relacion_laboral_con_validaciones.csv")

print("\nCreando columnas de validación...")

# COLUMNA 1: licencia_paternidad
print("\n1. Creando columna licencia_paternidad...")
df['licencia_paternidad'] = df.apply(
    lambda row: "Concepto Si Aplica" 
    if row['external_name_label'] == "Licencia Paternidad" and row['calendar_days'] == 14 
    else "Concepto No Aplica",
    axis=1
)
print(f"   ✓ Columna creada")
print(f"   - Concepto Si Aplica: {(df['licencia_paternidad'] == 'Concepto Si Aplica').sum()}")
print(f"   - Concepto No Aplica: {(df['licencia_paternidad'] == 'Concepto No Aplica').sum()}")

# COLUMNA 2: licencia_maternidad
print("\n2. Creando columna licencia_maternidad...")
df['licencia_maternidad'] = df.apply(
    lambda row: "Concepto Si Aplica" 
    if row['external_name_label'] == "Licencia Maternidad" and row['calendar_days'] == 126 
    else "Concepto No Aplica",
    axis=1
)
print(f"   ✓ Columna creada")
print(f"   - Concepto Si Aplica: {(df['licencia_maternidad'] == 'Concepto Si Aplica').sum()}")
print(f"   - Concepto No Aplica: {(df['licencia_maternidad'] == 'Concepto No Aplica').sum()}")

# COLUMNA 3: ley_de_luto (USA quantity_in_days)
print("\n3. Creando columna ley_de_luto...")
df['ley_de_luto'] = df.apply(
    lambda row: "Concepto Si Aplica" 
    if row['external_name_label'] == "Ley de luto" and row['quantity_in_days'] == 5 
    else "Concepto No Aplica",
    axis=1
)
print(f"   ✓ Columna creada")
print(f"   - Concepto Si Aplica: {(df['ley_de_luto'] == 'Concepto Si Aplica').sum()}")
print(f"   - Concepto No Aplica: {(df['ley_de_luto'] == 'Concepto No Aplica').sum()}")

# COLUMNA 4: incap_fuera_de_turno
print("\n4. Creando columna incap_fuera_de_turno...")
df['incap_fuera_de_turno'] = df.apply(
    lambda row: "Concepto Si Aplica" 
    if row['external_name_label'] == "Incapa.fuera de turno" and row['calendar_days'] <= 1 
    else "Concepto No Aplica",
    axis=1
)
print(f"   ✓ Columna creada")
print(f"   - Concepto Si Aplica: {(df['incap_fuera_de_turno'] == 'Concepto Si Aplica').sum()}")
print(f"   - Concepto No Aplica: {(df['incap_fuera_de_turno'] == 'Concepto No Aplica').sum()}")

# COLUMNA 5: lic_maternidad_sena
print("\n5. Creando columna lic_maternidad_sena...")
df['lic_maternidad_sena'] = df.apply(
    lambda row: "Concepto Si Aplica" 
    if row['external_name_label'] == "Licencia de Maternidad SENA" and row['calendar_days'] == 126 
    else "Concepto No Aplica",
    axis=1
)
print(f"   ✓ Columna creada")
print(f"   - Concepto Si Aplica: {(df['lic_maternidad_sena'] == 'Concepto Si Aplica').sum()}")
print(f"   - Concepto No Aplica: {(df['lic_maternidad_sena'] == 'Concepto No Aplica').sum()}")

# COLUMNA 6: lic_jurado_votacion
print("\n6. Creando columna lic_jurado_votacion...")
df['lic_jurado_votacion'] = df.apply(
    lambda row: "Concepto Si Aplica" 
    if row['external_name_label'] == "Lic Jurado Votación" and row['calendar_days'] <= 1 
    else "Concepto No Aplica",
    axis=1
)
print(f"   ✓ Columna creada")
print(f"   - Concepto Si Aplica: {(df['lic_jurado_votacion'] == 'Concepto Si Aplica').sum()}")
print(f"   - Concepto No Aplica: {(df['lic_jurado_votacion'] == 'Concepto No Aplica').sum()}")

# Guardar el archivo con las nuevas columnas
print("\n" + "="*80)
print("GUARDANDO ARCHIVO CON VALIDACIONES...")
print("="*80)
df.to_csv(archivo_con_validaciones, index=False, encoding='utf-8-sig')
print(f"\n✓✓✓ ARCHIVO GUARDADO EXITOSAMENTE ✓✓✓")
print(f"Ubicación: {archivo_con_validaciones}")

# Eliminar el archivo temporal relacion_laboral.csv
if os.path.exists(archivo_relacion_laboral):
    os.remove(archivo_relacion_laboral)
    print(f"\n✓ Archivo temporal eliminado: relacion_laboral.csv")

print("\n" + "="*80)
print("PASO 5: GENERANDO EXCELES DE ALERTAS POR COLUMNA")
print("="*80)

# ============================================================================
# PARTE 5: GENERAR EXCELES DE ALERTAS
# ============================================================================

# Excel 1: Alertas de licencia_paternidad
print("\n1. Generando Excel de alertas: licencia_paternidad...")
df_alert_paternidad = df[(df['licencia_paternidad'] == 'Concepto No Aplica') & 
                         (df['external_name_label'] == 'Licencia Paternidad')].copy()
if len(df_alert_paternidad) > 0:
    archivo_alert = os.path.join(carpeta_salida, "alerta_licencia_paternidad.csv")
    guardar_csv_con_fechas(df_alert_paternidad, archivo_alert)
    print(f"   ✓ {len(df_alert_paternidad)} alertas encontradas → {archivo_alert}")
else:
    print(f"   ✓ 0 alertas (todos los registros de Licencia Paternidad tienen 14 días)")

# Excel 2: Alertas de licencia_maternidad
print("\n2. Generando Excel de alertas: licencia_maternidad...")
df_alert_maternidad = df[(df['licencia_maternidad'] == 'Concepto No Aplica') & 
                         (df['external_name_label'] == 'Licencia Maternidad')].copy()
if len(df_alert_maternidad) > 0:
    archivo_alert = os.path.join(carpeta_salida, "alerta_licencia_maternidad.csv")
    guardar_csv_con_fechas(df_alert_maternidad, archivo_alert)
    print(f"   ✓ {len(df_alert_maternidad)} alertas encontradas → {archivo_alert}")
else:
    print(f"   ✓ 0 alertas (todos los registros de Licencia Maternidad tienen 126 días)")

# Excel 3: Alertas de ley_de_luto
print("\n3. Generando Excel de alertas: ley_de_luto...")
df_alert_luto = df[(df['ley_de_luto'] == 'Concepto No Aplica') & 
                   (df['external_name_label'] == 'Ley de luto')].copy()
if len(df_alert_luto) > 0:
    archivo_alert = os.path.join(carpeta_salida, "alerta_ley_de_luto.csv")
    guardar_csv_con_fechas(df_alert_luto, archivo_alert)
    print(f"   ✓ {len(df_alert_luto)} alertas encontradas → {archivo_alert}")
else:
    print(f"   ✓ 0 alertas (todos los registros de Ley de luto tienen 5 días)")

# Excel 4: Alertas de incap_fuera_de_turno
print("\n4. Generando Excel de alertas: incap_fuera_de_turno...")
df_alert_incap = df[(df['incap_fuera_de_turno'] == 'Concepto No Aplica') & 
                    (df['external_name_label'] == 'Incapa.fuera de turno')].copy()
if len(df_alert_incap) > 0:
    archivo_alert = os.path.join(carpeta_salida, "alerta_incap_fuera_de_turno.csv")
    guardar_csv_con_fechas(df_alert_incap, archivo_alert)
    print(f"   ✓ {len(df_alert_incap)} alertas encontradas → {archivo_alert}")
else:
    print(f"   ✓ 0 alertas (todos los registros de Incapa.fuera de turno tienen <=1 día)")

# Excel 5: Alertas de lic_maternidad_sena
print("\n5. Generando Excel de alertas: lic_maternidad_sena...")
df_alert_mat_sena = df[(df['lic_maternidad_sena'] == 'Concepto No Aplica') & 
                       (df['external_name_label'] == 'Licencia de Maternidad SENA')].copy()
if len(df_alert_mat_sena) > 0:
    archivo_alert = os.path.join(carpeta_salida, "alerta_lic_maternidad_sena.csv")
    guardar_csv_con_fechas(df_alert_mat_sena, archivo_alert)
    print(f"   ✓ {len(df_alert_mat_sena)} alertas encontradas → {archivo_alert}")
else:
    print(f"   ✓ 0 alertas (todos los registros de Licencia de Maternidad SENA tienen 126 días)")

# Excel 6: Alertas de lic_jurado_votacion
print("\n6. Generando Excel de alertas: lic_jurado_votacion...")
df_alert_jurado = df[(df['lic_jurado_votacion'] == 'Concepto No Aplica') & 
                     (df['external_name_label'] == 'Lic Jurado Votación')].copy()
if len(df_alert_jurado) > 0:
    archivo_alert = os.path.join(carpeta_salida, "alerta_lic_jurado_votacion.csv")
    guardar_csv_con_fechas(df_alert_jurado, archivo_alert)
    print(f"   ✓ {len(df_alert_jurado)} alertas encontradas → {archivo_alert}")
else:
    print(f"   ✓ 0 alertas (todos los registros de Lic Jurado Votación tienen <=1 día)")

# Excel 7: Incapacidades mayores a 30 días
print("\n7. Generando Excel de alertas: incp_mayor_30_dias...")
conceptos_incapacidad = [
    'Incapacidad enfermedad general',
    'Prorroga Inca/Enfer Gene',
    'Enf Gral SOAT',
    'Inc. Accidente de Trabajo',
    'Prorroga Inc. Accid. Trab'
]
df_incap_mayor_30 = df[
    (df['external_name_label'].isin(conceptos_incapacidad)) & 
    (df['calendar_days'] > 30)
].copy()
if len(df_incap_mayor_30) > 0:
    archivo_alert = os.path.join(carpeta_salida, "incp_mayor_30_dias.csv")
    guardar_csv_con_fechas(df_incap_mayor_30, archivo_alert)
    print(f"   ✓ {len(df_incap_mayor_30)} alertas encontradas → {archivo_alert}")
    print(f"   Conceptos encontrados:")
    conceptos_encontrados = df_incap_mayor_30['external_name_label'].value_counts()
    for concepto, cantidad in conceptos_encontrados.items():
        print(f"     - {concepto}: {cantidad} registro(s)")
else:
    print(f"   ✓ 0 alertas (ninguna incapacidad tiene más de 30 días)")

# Excel 8: Ausentismos sin pago mayores a 10 días
print("\n8. Generando Excel de alertas: Validación ausentismos sin pago > 10 días...")
conceptos_sin_pago = [
    'Aus Reg sin Soporte',
    'Suspensión'
]
df_sin_pago_mayor_10 = df[
    (df['external_name_label'].isin(conceptos_sin_pago)) & 
    (df['calendar_days'] > 10)
].copy()
if len(df_sin_pago_mayor_10) > 0:
    archivo_alert = os.path.join(carpeta_salida, "Validacion_ausentismos_sin_pago_mayor_10_dias.csv")
    guardar_csv_con_fechas(df_sin_pago_mayor_10, archivo_alert)
    print(f"   ✓ {len(df_sin_pago_mayor_10)} alertas encontradas → {archivo_alert}")
    print(f"   Conceptos encontrados:")
    conceptos_encontrados = df_sin_pago_mayor_10['external_name_label'].value_counts()
    for concepto, cantidad in conceptos_encontrados.items():
        print(f"     - {concepto}: {cantidad} registro(s)")
else:
    print(f"   ✓ 0 alertas (ningún ausentismo sin pago tiene más de 10 días)")

# Excel 9: Día de la familia mayor de 1 día
print("\n9. Generando Excel de alertas: dia_de_la_familia...")
df_dia_familia = df[
    (df['external_name_label'] == 'Día de la familia') & 
    (df['calendar_days'] > 1)
].copy()
if len(df_dia_familia) > 0:
    archivo_alert = os.path.join(carpeta_salida, "dia_de_la_familia.csv")
    guardar_csv_con_fechas(df_dia_familia, archivo_alert)
    print(f"   ✓ {len(df_dia_familia)} alertas encontradas → {archivo_alert}")
else:
    print(f"   ✓ 0 alertas (ningún Día de la familia tiene > 1 día)")

# ============================================================================
# VALIDACIÓN 10: INCAPACIDAD SIN ENLACE (FSE SI APLICA PERO SIN FECHA)
# ============================================================================
print("\n10. Generando Excel de alertas: Incapacidad_sin_enlace...")
print("    Filtro: fse = 'Si Aplica' AND fse_fechas vacía")

# Verificar si existe la columna fse_fechas
if 'fse_fechas' in df.columns:
    # Filtrar registros donde FSE = "Si Aplica" Y fse_fechas está vacía
    df_incap_sin_enlace = df[
        (df['fse'] == 'Si Aplica') &
        (df['fse_fechas'].isna() | (df['fse_fechas'] == ''))
    ].copy()

    if len(df_incap_sin_enlace) > 0:
        archivo_alert = os.path.join(carpeta_salida, "Incapacidad_sin_enlace.csv")
        guardar_csv_con_fechas(df_incap_sin_enlace, archivo_alert)
        print(f"   ✓ {len(df_incap_sin_enlace)} alertas encontradas → {archivo_alert}")
        print(f"   💡 Estos registros tienen FSE='Si Aplica' pero les falta la fecha de Final Salario enfer.")
    else:
        print(f"   ✓ 0 alertas (todos los registros con FSE='Si Aplica' tienen fecha)")
else:
    print(f"   ⚠️ ADVERTENCIA: Columna 'fse_fechas' no encontrada en el archivo")
    print(f"   📋 Columnas disponibles: {', '.join(df.columns)}")

# ============================================================================
# VALIDACIÓN 11: REGISTROS SIN DIAGNÓSTICO
# ============================================================================
print("\n11. Generando CSV de alertas: registros_sin_diagnostico...")
print("    Filtro: Códigos de incapacidad SIN descripcion_general_external_code")

# Códigos que requieren diagnóstico
codigos_requieren_diagnostico = [
    '203', '202', '216', '215', '210', '220', '201', '200',
    '188', '235', '383', '233', '251', '231', '232', '250', '230'
]

if 'homologacion_clase_de_ausentismo_ssf_vs_sap' in df.columns:
    # Convertir a string para comparación
    df['homologacion_clase_de_ausentismo_ssf_vs_sap'] = df['homologacion_clase_de_ausentismo_ssf_vs_sap'].astype(str).str.strip()

    # Filtrar registros con esos códigos
    df_codigos_diagnostico = df[
        df['homologacion_clase_de_ausentismo_ssf_vs_sap'].isin(codigos_requieren_diagnostico)
    ].copy()

    print(f"   📊 Registros con códigos que requieren diagnóstico: {len(df_codigos_diagnostico)}")

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

                archivo_alert = os.path.join(carpeta_salida, "registros_sin_diagnostico.csv")
                guardar_csv_con_fechas(df_sin_diagnostico, archivo_alert)
                print(f"   ✓ {len(df_sin_diagnostico)} alertas encontradas → {archivo_alert}")
                print(f"   💡 Códigos afectados: {df_sin_diagnostico['homologacion_clase_de_ausentismo_ssf_vs_sap'].unique().tolist()}")
            else:
                print(f"   ✓ 0 alertas (todos los registros tienen diagnóstico)")
        else:
            print(f"   ⚠️ ADVERTENCIA: Columna 'descripcion_general_external_code' no encontrada")
    else:
        print(f"   ✓ 0 registros con códigos que requieren diagnóstico")
else:
    print(f"   ⚠️ ADVERTENCIA: Columna 'homologacion_clase_de_ausentismo_ssf_vs_sap' no encontrada")

# ============================================================================
# VALIDACIÓN 12: DIAGNÓSTICO INCORRECTO (MENOS DE 2 CARACTERES)
# ============================================================================
print("\n12. Generando CSV de alertas: diagnostico_incorrecto...")
print("    Filtro: descripcion_general_external_code con menos de 2 caracteres")

if 'descripcion_general_external_code' in df.columns:
    # Convertir a string y filtrar los que tienen menos de 2 caracteres (y no están vacíos)
    df['descripcion_general_external_code_str'] = df['descripcion_general_external_code'].astype(str).str.strip()

    # Filtrar: no vacío, no 'nan', y longitud < 2
    mask_diagnostico_incorrecto = (
        (df['descripcion_general_external_code_str'] != '') &
        (df['descripcion_general_external_code_str'] != 'nan') &
        (df['descripcion_general_external_code_str'].str.len() < 2)
    )

    df_diagnostico_incorrecto = df[mask_diagnostico_incorrecto].copy()

    # Eliminar columna temporal
    df.drop('descripcion_general_external_code_str', axis=1, inplace=True)

    if len(df_diagnostico_incorrecto) > 0:
        archivo_alert = os.path.join(carpeta_salida, "diagnostico_incorrecto.csv")
        guardar_csv_con_fechas(df_diagnostico_incorrecto, archivo_alert)
        print(f"   ✓ {len(df_diagnostico_incorrecto)} alertas encontradas → {archivo_alert}")
        print(f"   💡 Valores incorrectos encontrados: {df_diagnostico_incorrecto['descripcion_general_external_code'].unique().tolist()[:10]}")
    else:
        print(f"   ✓ 0 alertas (todos los diagnósticos tienen 2+ caracteres)")
else:
    print(f"   ⚠️ ADVERTENCIA: Columna 'descripcion_general_external_code' no encontrada")

print("\n" + "="*80)
print("RESUMEN FINAL DE TODOS LOS PROCESOS")
print("="*80)
print(f"\nArchivos principales generados:")
print(f"  1. {archivo_con_validaciones}")
print(f"  2. {archivo_sena_errores}")
print(f"  3. {archivo_ley50_errores}")
print(f"  4. {archivo_integral_errores}")
print(f"\nArchivos de alertas por columna (si hay errores):")
print(f"  5. alerta_licencia_paternidad.csv")
print(f"  6. alerta_licencia_maternidad.csv")
print(f"  7. alerta_ley_de_luto.csv")
print(f"  8. alerta_incap_fuera_de_turno.csv")
print(f"  9. alerta_lic_maternidad_sena.csv")
print(f"  10. alerta_lic_jurado_votacion.csv")
print(f"  11. Incapacidad_sin_enlace.csv (FSE Si Aplica sin fecha)")
print(f"  12. registros_sin_diagnostico.csv (incapacidades sin diagnóstico CIE-10)")
print(f"  13. diagnostico_incorrecto.csv (diagnóstico con menos de 2 caracteres)")
print("\nEstadísticas:")
print(f"  - Total registros con relación laboral: {len(df)}")
print(f"\n  APRENDIZAJE:")
print(f"    - Registros: {len(df_aprendizaje)}")
if len(df_aprendizaje) > 0:
    print(f"    - Errores encontrados: {len(df_errores_sena)}")
print(f"\n  LEY 50:")
print(f"    - Registros: {len(df_ley50)}")
if len(df_ley50) > 0:
    print(f"    - Errores encontrados: {len(df_errores_ley50)}")
print(f"\n  INTEGRAL:")
print(f"    - Registros: {len(df_integral)}")
if len(df_integral) > 0:
    print(f"    - Errores encontrados: {len(df_errores_integral)}")
print("\n  COLUMNAS DE VALIDACIÓN CREADAS: 6")
print("="*80)
print(f"\n✓✓✓ TODOS LOS ARCHIVOS CREADOS EN: {carpeta_salida} ✓✓✓")
print("="*80)
