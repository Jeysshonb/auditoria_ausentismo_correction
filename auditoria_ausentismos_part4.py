"""
Auditoría de Ausentismos - Parte 4
Análisis de Registros Únicos y Ventana de 30 Días con Ponderación

Filtro de Registros Únicos por Códigos de Ausentismo
Extrae registros únicos por id_personal filtrados por códigos específicos
Luego aplica análisis de 30 días con ponderación específica (25% por columna)
"""

import pandas as pd
import numpy as np
import os

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================

# Rutas (se configurarán desde app.py)
ruta_entrada = ""
directorio_salida = ""
ruta_salida_unicos = ""
ruta_salida_30dias = ""
# Filtro opcional por fecha_ultima (last_approval_status_date)
fecha_ultima_inicio = None
fecha_ultima_fin = None

# Códigos a excluir de registros únicos (con el 215)
CODIGOS_EXCLUIR_UNICOS = [203, 202, 216, 210, 220, 201, 200, 383, 215]

# Códigos a incluir en reporte 30 días (CON el 215)
CODIGOS_INCLUIR_30DIAS = [203, 202, 215, 216, 210, 220, 201, 200, 383]

# PONDERACIONES: 25% cada columna
COLUMNAS_PONDERADAS = {
    'GRUPO': 0.25,
    'Clasificación Sistemas JMC': 0.25,
    'SEGMENTO': 0.25,
    'Clasificación Partes JMC': 0.25
}

# Ventana de días para análisis
VENTANA_DIAS = 30

# Ruta al archivo de códigos en el repositorio
RUTA_CODIGOS_CSV = "datos_numericos.csv"

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def procesar_analisis_completo():
    """
    Ejecuta el análisis completo:
    1. Filtra registros únicos por códigos
    2. Analiza ventana de 30 días con ponderación

    Returns:
        tuple: (df_unicos, df_reporte_30dias) o (None, None) si hay error
    """

    print("=" * 80)
    print("PROCESAMIENTO DE REGISTROS ÚNICOS Y ANÁLISIS 30 DÍAS")
    print("=" * 80)

    # DEBUG: Verificar configuración inicial
    print("\n🔍 DEBUG - Configuración inicial:")
    print(f"  - ruta_entrada: {ruta_entrada}")
    print(f"  - directorio_salida: {directorio_salida}")
    print(f"  - ruta_salida_unicos: {ruta_salida_unicos}")
    print(f"  - ruta_salida_30dias: {ruta_salida_30dias}")
    print(f"  - fecha_ultima_inicio: {fecha_ultima_inicio}")
    print(f"  - fecha_ultima_fin: {fecha_ultima_fin}")
    print(f"  - RUTA_CODIGOS_CSV: {RUTA_CODIGOS_CSV}")

    def normalizar_texto(valor):
        """Convierte valores mixtos a texto seguro para joins/comparaciones."""
        if pd.isna(valor):
            return ''
        valor_str = str(valor).strip()
        if valor_str.lower() in {'nan', 'none'}:
            return ''
        return valor_str

    def join_seguro(valores, separador):
        """Une valores heterogéneos evitando TypeError por floats/NaN."""
        return separador.join(
            [normalizar_texto(v) for v in valores if normalizar_texto(v)]
        )

    try:
        # ============================================================================
        # PASO 1: FILTRAR Y OBTENER REGISTROS ÚNICOS
        # ============================================================================
        print("\n1. Procesando registros únicos...")

        # DEBUG: Verificar archivo de entrada
        if not ruta_entrada:
            raise ValueError("❌ ruta_entrada no está configurada")
        if not os.path.exists(ruta_entrada):
            raise FileNotFoundError(f"❌ No se encuentra el archivo: {ruta_entrada}")

        print(f"   📂 Leyendo archivo: {os.path.basename(ruta_entrada)}")
        # Leer código diagnóstico como texto para evitar coerción a float/NaN
        df = pd.read_csv(
            ruta_entrada,
            encoding='utf-8-sig',
            dtype={'descripcion_general_external_code': 'string'}
        )
        print(f"   ✅ Registros totales: {len(df):,}")
        print(f"   📋 Columnas encontradas: {len(df.columns)}")

        # DEBUG: Mostrar primeras columnas
        print(f"   🔍 Primeras 5 columnas: {list(df.columns[:5])}")
        print(f"   🔍 Todas las columnas ({len(df.columns)}): {list(df.columns)}")

        # COMPATIBILIDAD: Verificar si existe fse_fechas o Final Salario enfer.
        tiene_fse_fechas = 'fse_fechas' in df.columns
        tiene_final_salario = 'Final Salario enfer.' in df.columns
        print(f"   🔍 Columna 'fse_fechas': {'SÍ' if tiene_fse_fechas else 'NO'}")
        print(f"   🔍 Columna 'Final Salario enfer.': {'SÍ' if tiene_final_salario else 'NO'}")

        # FILTRAR PARA REGISTROS ÚNICOS: EXCLUIR los códigos especificados
        if 'homologacion_clase_de_ausentismo_ssf_vs_sap' not in df.columns:
            raise ValueError(f"❌ ERROR: Columna 'homologacion_clase_de_ausentismo_ssf_vs_sap' NO EXISTE en el archivo. Columnas disponibles: {list(df.columns)}")

        # Validar que existan las columnas CRÍTICAS requeridas
        columnas_criticas = ['id_personal', 'last_approval_status_date', 'start_date',
                             'descripcion_general_external_code']
        columnas_faltantes = [col for col in columnas_criticas if col not in df.columns]
        if columnas_faltantes:
            print(f"❌ ERROR CRÍTICO: Faltan columnas OBLIGATORIAS: {columnas_faltantes}")
            print(f"   Columnas disponibles: {list(df.columns)}")
            return None, None

        # Verificar/agregar columnas opcionales para mantener compatibilidad
        if 'external_name_label' not in df.columns:
            print("   ⚠️ ADVERTENCIA: Columna opcional 'external_name_label' NO existe (se crea con 'N/A')")
            df['external_name_label'] = 'N/A'
        else:
            print("   ✅ Columna opcional 'external_name_label' encontrada")

        if 'cie10_descripcion' not in df.columns:
            print("   ⚠️ ADVERTENCIA: Columna opcional 'cie10_descripcion' NO existe (se crea vacía)")
            df['cie10_descripcion'] = ''
        else:
            print("   ✅ Columna opcional 'cie10_descripcion' encontrada")

        if 'end_date' not in df.columns:
            print("   ⚠️ ADVERTENCIA: Columna opcional 'end_date' NO existe (se crea vacía)")
            df['end_date'] = ''
        else:
            print("   ✅ Columna opcional 'end_date' encontrada")

        # Normalizar columnas de texto usadas en joins/formateo
        df['descripcion_general_external_code'] = df['descripcion_general_external_code'].map(normalizar_texto)
        df['external_name_label'] = df['external_name_label'].map(normalizar_texto)
        df['cie10_descripcion'] = df['cie10_descripcion'].map(normalizar_texto)

        # Convertir fechas una sola vez (acepta DD/MM/YYYY o YYYY-MM-DD)
        df['last_approval_status_date'] = pd.to_datetime(
            df['last_approval_status_date'],
            dayfirst=True,
            errors='coerce'
        )
        df['start_date'] = pd.to_datetime(
            df['start_date'],
            dayfirst=True,
            errors='coerce'
        )
        df['end_date'] = pd.to_datetime(
            df['end_date'],
            dayfirst=True,
            errors='coerce'
        )

        # Filtro opcional por fecha_ultima
        if fecha_ultima_inicio is not None and fecha_ultima_fin is not None:
            fu_inicio_dt = pd.to_datetime(fecha_ultima_inicio, errors='coerce')
            fu_fin_dt = pd.to_datetime(fecha_ultima_fin, errors='coerce')

            if pd.isna(fu_inicio_dt) or pd.isna(fu_fin_dt):
                print("   ⚠️ Filtro fecha_ultima ignorado por fechas inválidas")
            else:
                registros_antes_filtro_fecha = len(df)
                df = df[
                    (df['last_approval_status_date'] >= fu_inicio_dt) &
                    (df['last_approval_status_date'] <= fu_fin_dt)
                ].copy()
                print(
                    f"   ✅ Filtro fecha_ultima aplicado: {fu_inicio_dt.strftime('%d/%m/%Y')} → "
                    f"{fu_fin_dt.strftime('%d/%m/%Y')} | {registros_antes_filtro_fecha:,} → {len(df):,}"
                )
        elif (fecha_ultima_inicio is not None) != (fecha_ultima_fin is not None):
            print("   ⚠️ Filtro fecha_ultima incompleto (falta inicio o fin), se omite")

        # Filtrar para registros únicos (ya con fechas convertidas)
        df_filtrado_unicos = df[~df['homologacion_clase_de_ausentismo_ssf_vs_sap'].isin(CODIGOS_EXCLUIR_UNICOS)].copy()
        print(f"   Registros excluyendo códigos {CODIGOS_EXCLUIR_UNICOS}: {len(df_filtrado_unicos):,}")

        # Ordenar por: id_personal, last_approval_status_date (desc), start_date (desc)
        # Así el registro con la fecha más reciente en start_date quedará primero
        df_filtrado_unicos = df_filtrado_unicos.sort_values(
            by=['id_personal', 'last_approval_status_date', 'start_date'],
            ascending=[True, False, False]
        )

        # Tomar el primer registro de cada id_personal (que ahora es el más reciente)
        df_unicos = df_filtrado_unicos.drop_duplicates(subset=['id_personal'], keep='first')

        print(f"   Registros únicos (SIN códigos filtrados): {len(df_unicos):,}")
        print(f"   → Criterio: Última last_approval_status_date y start_date más reciente")

        df_unicos.to_csv(ruta_salida_unicos, index=False, encoding='utf-8-sig', date_format='%d/%m/%Y')
        print(f"✅ Guardado: {os.path.basename(ruta_salida_unicos)}")

        # FILTRAR PARA REPORTE 30 DÍAS: INCLUIR SOLO los códigos especificados
        df_filtrado_30dias = df[df['homologacion_clase_de_ausentismo_ssf_vs_sap'].isin(CODIGOS_INCLUIR_30DIAS)].copy()
        print(f"   Registros CON códigos {CODIGOS_INCLUIR_30DIAS}: {len(df_filtrado_30dias):,}")

        df_filtrado_30dias = df_filtrado_30dias.sort_values(
            by=['id_personal', 'start_date', 'last_approval_status_date'],
            ascending=[True, False, False]
        )
        df_filtrado_30dias_unicos = df_filtrado_30dias.drop_duplicates(subset=['id_personal'], keep='first')
        print(f"   IDs únicos para reporte 30 días: {len(df_filtrado_30dias_unicos):,}")
        
        # ============================================================================
        # PASO 2: CARGAR MATRIZ DE CÓDIGOS
        # ============================================================================
        print("\n2. Cargando matriz de códigos CIE-10...")
        
        # Verificar si existe el archivo en el repositorio
        if not os.path.exists(RUTA_CODIGOS_CSV):
            print(f"❌ ERROR: No se encontró el archivo {RUTA_CODIGOS_CSV}")
            return None, None
        
        df_codigos = pd.read_csv(
            RUTA_CODIGOS_CSV,
            encoding='utf-8-sig',
            dtype={'Código': 'string'}
        )
        
        # Eliminar columna porcentaje_relacion si existe
        if 'porcentaje_relacion' in df_codigos.columns:
            df_codigos = df_codigos.drop('porcentaje_relacion', axis=1)

        df_codigos['Código'] = df_codigos['Código'].map(normalizar_texto)
        
        print(f"✅ Columnas disponibles en matriz: {list(df_codigos.columns)}")
        
        # Verificar que las columnas ponderadas existen
        columnas_faltantes = [col for col in COLUMNAS_PONDERADAS.keys() if col not in df_codigos.columns]
        if columnas_faltantes:
            print(f"❌ ERROR: Faltan columnas en la matriz: {columnas_faltantes}")
            return None, None
        
        # ============================================================================
        # PASO 3: PREPARAR DATOS PARA ANÁLISIS 30 DÍAS
        # ============================================================================
        print("\n3. Preparando datos para análisis 30 días...")
        print("   ℹ️ Se usan los datos ya cargados y preprocesados una sola vez")

        # Obtener solo los IDs únicos del filtro CON CÓDIGOS (para reporte 30 días)
        ids_filtrados = df_filtrado_30dias_unicos['id_personal'].unique()

        print(f"✅ IDs a procesar: {len(ids_filtrados):,}")
        print(f"✅ Ponderación configurada:")
        for col, peso in COLUMNAS_PONDERADAS.items():
            print(f"   • {col}: {peso*100:.0f}%")

        # Filtrar por IDs
        df_ausentismos = df[df['id_personal'].isin(ids_filtrados)].copy()

        # Validar que haya datos
        if len(df_ausentismos) == 0:
            print("❌ ERROR: No hay datos después de filtrar por IDs")
            return None, None

        print(f"✅ Registros válidos para análisis: {len(df_ausentismos):,}")
        
        # ============================================================================
        # PASO 4: CREAR DICCIONARIO DE CÓDIGOS
        # ============================================================================
        print("\n4. Creando diccionario de códigos...")
        
        codigo_a_valores = {}
        for idx, row in df_codigos.iterrows():
            codigo = normalizar_texto(row['Código'])
            if not codigo:
                continue
            valores = {col: row[col] for col in COLUMNAS_PONDERADAS.keys()}
            codigo_a_valores[codigo] = valores
        
        print(f"✅ {len(codigo_a_valores)} códigos en diccionario")
        
        # ============================================================================
        # PASO 5: PROCESAR CADA ID_PERSONAL
        # ============================================================================
        print("\n5. Procesando análisis de 30 días...")
        
        resultados = []
        id_actual = None
        
        for contador, id_pers in enumerate(ids_filtrados, 1):
            id_actual = id_pers
            # Obtener datos de este ID
            datos_id = df_ausentismos[df_ausentismos['id_personal'] == id_pers].copy()

            # PROTECCIÓN: Verificar que haya datos para este ID
            if len(datos_id) == 0:
                print(f"  ⚠️ SALTANDO ID {id_pers} (#{contador}/{len(ids_filtrados)}): Sin datos")
                continue

            # PRIORIDAD 1: Buscar el start_date más reciente
            # PRIORIDAD 2: Si hay empate, desempatar por last_approval_status_date más reciente
            datos_id_ordenado = datos_id.sort_values(
                by=['start_date', 'last_approval_status_date'],
                ascending=[False, False]  # Ambos descendentes (más reciente primero)
            )

            # PROTECCIÓN: Verificar que datos_id_ordenado no esté vacío
            if len(datos_id_ordenado) == 0:
                print(f"  ⚠️ SALTANDO ID {id_pers} (#{contador}/{len(ids_filtrados)}): DataFrame vacío tras ordenar")
                continue

            # Tomar el primer registro (start_date más reciente)
            registro_ultimo = datos_id_ordenado.iloc[0]

            fecha_aprobacion_maxima = registro_ultimo['last_approval_status_date']
            codigo_ultima_fecha = normalizar_texto(registro_ultimo['descripcion_general_external_code'])
            start_date_ultimo = registro_ultimo['start_date']
            end_date_ultimo = registro_ultimo['end_date']
            # CORRECCIÓN: pandas Series no tiene método .get(), usar in index
            if 'external_name_label' in registro_ultimo.index:
                external_label_ultimo = registro_ultimo['external_name_label']
            else:
                external_label_ultimo = 'N/A'
            
            # Calcular fecha límite (30 días antes del start_date)
            fecha_limite = start_date_ultimo - pd.Timedelta(days=VENTANA_DIAS)
            
            # Filtrar registros dentro de la ventana de 30 días
            datos_filtrados = datos_id[
                (datos_id['start_date'] >= fecha_limite) & 
                (datos_id['start_date'] <= start_date_ultimo)
            ].copy()
            
            # Calcular días transcurridos
            datos_filtrados['dias_transcurridos'] = (start_date_ultimo - datos_filtrados['start_date']).dt.days
            
            # Excluir el código que choca (el del registro más reciente)
            datos_filtrados_sin_choque = datos_filtrados[
                (datos_filtrados['descripcion_general_external_code'] != codigo_ultima_fecha) |
                (datos_filtrados['start_date'] != start_date_ultimo)
            ].copy()

            # ORDENAR por start_date de menor a mayor (más antigua primero)
            datos_filtrados_sin_choque = datos_filtrados_sin_choque.sort_values('start_date', ascending=True)

            # Calcular duración en días del código que choca
            if pd.notna(end_date_ultimo) and pd.notna(start_date_ultimo):
                duracion_dias = (end_date_ultimo - start_date_ultimo).days + 1
            else:
                duracion_dias = 0

            # Crear tipo_concepto (el código que choca con todos)
            tipo_concepto = f"{codigo_ultima_fecha}(start:{start_date_ultimo.strftime('%d/%m/%Y')},dias:{duracion_dias})({external_label_ultimo})"

            # Si no hay datos para comparar
            if len(datos_filtrados_sin_choque) == 0:
                resultados.append({
                    'id_personal': id_pers,
                    'fecha_ultima': fecha_aprobacion_maxima,  # Mantener como datetime
                    'start_date': start_date_ultimo,  # Mantener como datetime
                    'end_date': end_date_ultimo if pd.notna(end_date_ultimo) else pd.NaT,  # Mantener como datetime
                    'codigo_ultima_fecha': codigo_ultima_fecha,
                    'tipo_concepto': tipo_concepto,
                    'todos_codigos': '',
                    'detalle_codigos_con_fechas': '',
                    'cantidad_codigos': 0,
                    'comparaciones_detalle': '',
                    'porcentaje_relacion': 0.0,
                    'cie10_descripcion': ''
                })
                continue
            
            # Verificar si el código que choca existe en la tabla
            if codigo_ultima_fecha not in codigo_a_valores:
                detalle_codigos = []
                cie10_descripciones = []
                
                for idx, row in datos_filtrados_sin_choque.iterrows():
                    cod = normalizar_texto(row['descripcion_general_external_code'])
                    sd = row['start_date'].strftime('%d/%m/%Y')
                    dias = row['dias_transcurridos']
                    # CORRECCIÓN: pandas Series no tiene método .get()
                    external_label = row['external_name_label'] if 'external_name_label' in row.index else 'N/A'
                    cie10_desc = row['cie10_descripcion'] if 'cie10_descripcion' in row.index else ''
                    
                    detalle_codigos.append(f"{cod}(start:{sd},dias:{dias})({external_label})")
                    
                    if pd.notna(cie10_desc) and cie10_desc != '':
                        cie10_descripciones.append(f"({str(cie10_desc)})")
                
                todos_codigos = [
                    normalizar_texto(cod)
                    for cod in datos_filtrados_sin_choque['descripcion_general_external_code'].unique().tolist()
                    if normalizar_texto(cod)
                ]

                resultados.append({
                    'id_personal': id_pers,
                    'fecha_ultima': fecha_aprobacion_maxima,  # Mantener como datetime
                    'start_date': start_date_ultimo,  # Mantener como datetime
                    'end_date': end_date_ultimo if pd.notna(end_date_ultimo) else pd.NaT,  # Mantener como datetime
                    'codigo_ultima_fecha': codigo_ultima_fecha,
                    'tipo_concepto': tipo_concepto,
                    'todos_codigos': join_seguro(todos_codigos, ', '),
                    'detalle_codigos_con_fechas': ' | '.join(detalle_codigos),
                    'cantidad_codigos': len(todos_codigos),
                    'comparaciones_detalle': 'Código que choca no encontrado en tabla',
                    'porcentaje_relacion': 0.0,
                    'cie10_descripcion': join_seguro(cie10_descripciones, '|')
                })
                continue
            
            # Procesar comparaciones con PONDERACIÓN
            detalle_codigos = []
            comparaciones_detalle = []
            porcentajes = []
            cie10_descripciones = []
            valores_ultima = codigo_a_valores[codigo_ultima_fecha]
            
            for idx, row in datos_filtrados_sin_choque.iterrows():
                cod = normalizar_texto(row['descripcion_general_external_code'])
                sd = row['start_date'].strftime('%d/%m/%Y')
                dias = row['dias_transcurridos']
                # CORRECCIÓN: pandas Series no tiene método .get()
                external_label = row['external_name_label'] if 'external_name_label' in row.index else 'N/A'
                cie10_desc = row['cie10_descripcion'] if 'cie10_descripcion' in row.index else ''

                # Verificar si el código tiene caracteres especiales
                # CORRECCIÓN: Verificar que cod no sea None y manejar casos especiales
                cod_str = str(cod).strip() if cod is not None else ''
                if not cod_str or '*' in cod_str or not cod_str.replace(' ', '').replace('.', '').isalnum():
                    detalle_codigos.append(f"{cod}(start:{sd},dias:{dias},error_codigo)({external_label})")
                    comparaciones_detalle.append(f"{cod}:error_codigo")
                else:
                    detalle_codigos.append(f"{cod}(start:{sd},dias:{dias})({external_label})")
                    
                    # Verificar si el código existe en el diccionario
                    if cod in codigo_a_valores:
                        valores_hist = codigo_a_valores[cod]
                        
                        # CALCULAR PORCENTAJE PONDERADO: 25% por cada columna
                        porcentaje_total = 0.0
                        
                        for columna, peso in COLUMNAS_PONDERADAS.items():
                            # Si coincide la columna, sumar el 25%
                            if valores_ultima[columna] == valores_hist[columna]:
                                porcentaje_total += (peso * 100)
                        
                        porcentajes.append(porcentaje_total)
                        comparaciones_detalle.append(f"{cod}:{porcentaje_total:.1f}%")
                    else:
                        comparaciones_detalle.append(f"{cod}:N/A")
                
                # Agregar descripción CIE-10 si existe con formato |(DESCRIPCION)|
                if pd.notna(cie10_desc) and cie10_desc != '':
                    cie10_descripciones.append(f"({str(cie10_desc)})")
            
            # Crear strings de detalle
            detalle_str = ' | '.join(detalle_codigos)
            comparaciones_str = ' | '.join(comparaciones_detalle)
            todos_codigos = [
                normalizar_texto(cod)
                for cod in datos_filtrados_sin_choque['descripcion_general_external_code'].unique().tolist()
                if normalizar_texto(cod)
            ]
            
            # Calcular promedio de porcentajes
            porcentaje_promedio = np.mean(porcentajes) if porcentajes else 0.0

            # Guardar resultado
            resultados.append({
                'id_personal': id_pers,
                'fecha_ultima': fecha_aprobacion_maxima,  # Mantener como datetime
                'start_date': start_date_ultimo,  # Mantener como datetime
                'end_date': end_date_ultimo if pd.notna(end_date_ultimo) else pd.NaT,  # Mantener como datetime
                'codigo_ultima_fecha': codigo_ultima_fecha,
                'tipo_concepto': tipo_concepto,
                'todos_codigos': join_seguro(todos_codigos, ', '),
                'detalle_codigos_con_fechas': join_seguro([detalle_str], ' | '),
                'cantidad_codigos': len([c for c in todos_codigos if normalizar_texto(c)]),
                'comparaciones_detalle': join_seguro([comparaciones_str], ' | '),
                'porcentaje_relacion': round(porcentaje_promedio, 2),
                'cie10_descripcion': join_seguro(cie10_descripciones, '|')
            })
            
            # Mostrar progreso
            if contador % 500 == 0:
                print(f"  Procesados {contador}/{len(ids_filtrados)} IDs...")
        
        print(f"✅ Procesamiento completado")
        
        # ============================================================================
        # PASO 6: GUARDAR REPORTE 30 DÍAS
        # ============================================================================
        print("\n6. Guardando reporte 30 días...")
        
        df_resultado = pd.DataFrame(resultados)
        
        # NOMBRES DE COLUMNAS CORRECTOS Y EN ESPAÑOL
        columnas_orden = [
            'id_personal',
            'fecha_ultima',
            'start_date',
            'end_date',
            'codigo_ultima_fecha',
            'tipo_concepto',
            'todos_codigos',
            'detalle_codigos_con_fechas',
            'cantidad_codigos',
            'comparaciones_detalle',
            'porcentaje_relacion',
            'cie10_descripcion'
        ]
        
        df_resultado = df_resultado[columnas_orden]
        
        # Guardar CSV con formato CORRECTO y fechas en DD/MM/YYYY
        df_resultado.to_csv(
            ruta_salida_30dias,
            index=False,
            sep=';',
            encoding='utf-8-sig',
            decimal=',',
            date_format='%d/%m/%Y',  # Formato día/mes/año para fechas
            quoting=1,
            lineterminator='\n'
        )
        
        print(f"✅ Guardado: {os.path.basename(ruta_salida_30dias)}")
        
        # ============================================================================
        # PASO 7: ESTADÍSTICAS FINALES
        # ============================================================================
        print("\n" + "=" * 80)
        print("RESUMEN FINAL")
        print("=" * 80)
        
        print(f"\n📊 Archivos generados:")
        print(f"  1. {os.path.basename(ruta_salida_unicos)}: {len(df_unicos):,} registros")
        print(f"     → Registros únicos EXCLUYENDO códigos {CODIGOS_EXCLUIR_UNICOS}")
        print(f"  2. {os.path.basename(ruta_salida_30dias)}: {len(df_resultado):,} registros")
        print(f"     → Análisis 30 días SOLO con códigos {CODIGOS_INCLUIR_30DIAS}")
        
        print(f"\n📈 Estadísticas reporte 30 días:")
        print(f"  IDs con códigos para comparar: {len(df_resultado[df_resultado['cantidad_codigos'] > 0]):,}")
        print(f"  IDs sin códigos para comparar: {len(df_resultado[df_resultado['cantidad_codigos'] == 0]):,}")
        print(f"  Porcentaje promedio: {df_resultado['porcentaje_relacion'].mean():.2f}%")
        
        print(f"\n💡 Ponderación aplicada:")
        for col, peso in COLUMNAS_PONDERADAS.items():
            print(f"  • {col}: {peso*100:.0f}%")
        print(f"  → Total posible: 100% (si coinciden las 4 columnas)")
        
        print("\n✅ PROCESO COMPLETADO")
        print("=" * 80)
        
        return df_unicos, df_resultado
    
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR CRÍTICO EN PROCESAMIENTO")
        print("=" * 80)
        print(f"\n🔴 Tipo de Error: {type(e).__name__}")
        print(f"🔴 Mensaje: {str(e)}")
        if 'id_actual' in locals() and id_actual is not None:
            print(f"🔴 Último id_personal procesado: {id_actual}")
        print("\n📍 TRACEBACK COMPLETO:")
        print("-" * 80)
        import traceback
        print(traceback.format_exc())
        print("-" * 80)
        print("\n💡 INFORMACIÓN DE DEBUG:")
        print(f"  - Archivo de entrada existe: {os.path.exists(ruta_entrada) if ruta_entrada else 'NO CONFIGURADO'}")
        print(f"  - Archivo códigos existe: {os.path.exists(RUTA_CODIGOS_CSV)}")
        print(f"  - Directorio salida: {directorio_salida if directorio_salida else 'NO CONFIGURADO'}")
        print("=" * 80)
        return None, None


# ============================================================================
# EJECUCIÓN DIRECTA (PARA PRUEBAS LOCALES)
# ============================================================================

if __name__ == "__main__":
    # Configuración de ejemplo para ejecución local
    ruta_entrada = r"C:\Users\jjbustos\Downloads\PASO_3_CIE10\ausentismos_completo_con_cie10.csv"
    directorio_salida = r"C:\Users\jjbustos\Downloads\salida"
    ruta_salida_unicos = os.path.join(directorio_salida, "Registros_unicos.csv")
    ruta_salida_30dias = os.path.join(directorio_salida, "reporte_30_dias.csv")
    
    # Crear directorio de salida si no existe
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Ejecutar proceso
    df_unicos, df_reporte = procesar_analisis_completo()
    
    if df_unicos is not None and df_reporte is not None:
        print("\n✅ Archivos generados correctamente")
    else:
        print("\n❌ Error en el procesamiento")
