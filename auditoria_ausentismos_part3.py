import pandas as pd
import os
import logging
from datetime import datetime

# ===== CONFIGURACIÓN DE LOGGING =====
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auditoria_part3.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== CONFIGURACIÓN DE RUTAS =====
# Archivos de entrada
ruta_relacion_laboral = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida\relacion_laboral_con_validaciones.csv"
ruta_cie10 = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_planos\CIE 10 - AJUSTADO - NÓMINA.xlsx"

# Directorio de salida
directorio_salida = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida"
archivo_final = "ausentismos_completo_con_cie10.csv"
ruta_completa_salida = os.path.join(directorio_salida, archivo_final)

# ===== FILTRO DE 17 CÓDIGOS =====
CODIGOS_FILTRO = [
    '203', '202', '216', '215', '210', '220', '201', '200', 
    '188', '235', '383', '233', '251', '231', '232', '250', '230'
]


def procesar_todo():
    """Función principal que ejecuta todo el proceso"""

    logger.info("=" * 80)
    logger.info("INICIO DEL PROCESO COMPLETO: AUDITORÍA AUSENTISMOS")
    logger.info("=" * 80)
    logger.debug(f"Directorio de trabajo actual: {os.getcwd()}")
    logger.debug(f"Ruta relación laboral: {ruta_relacion_laboral}")
    logger.debug(f"Ruta CIE10: {ruta_cie10}")
    logger.debug(f"Directorio salida: {directorio_salida}")

    print("=" * 80)
    print("PROCESO COMPLETO: AUDITORÍA AUSENTISMOS")
    print("=" * 80)

    try:
        # ============================================
        # PARTE 1: PROCESAR Y FILTRAR RELACIÓN LABORAL
        # ============================================
        print("\n[PARTE 1/2] PROCESANDO RELACIÓN LABORAL")
        print("-" * 80)
        
        print("\n[1.1] Leyendo Relación Laboral...")
        logger.info("[1.1] Iniciando lectura de Relación Laboral...")
        logger.debug(f"Verificando existencia del archivo: {os.path.exists(ruta_relacion_laboral)}")
        logger.debug(f"Ruta absoluta: {os.path.abspath(ruta_relacion_laboral)}")

        df_relacion = pd.read_csv(ruta_relacion_laboral, encoding='utf-8-sig', dtype=str)
        logger.info(f"✅ Archivo leído exitosamente")
        logger.info(f"Registros iniciales: {len(df_relacion)}")
        logger.info(f"Columnas totales: {len(df_relacion.columns)}")
        logger.debug(f"Columnas disponibles: {list(df_relacion.columns)}")
        logger.debug(f"Primeras 2 filas:\n{df_relacion.head(2)}")

        print(f"      Registros iniciales: {len(df_relacion)}")
        print(f"      Columnas totales: {len(df_relacion.columns)}")

        # CORRECCIÓN: Normalizar columna last_approval_status_date (que es equivalente a "Modificado el")
        if 'last_approval_status_date' in df_relacion.columns:
            print("\n[1.1.1] Normalizando columna 'last_approval_status_date' a formato DD/MM/YYYY...")
            logger.info("Procesando columna last_approval_status_date (equivalente a 'Modificado el')")
            try:
                # Intentar parsear la fecha con diferentes formatos
                df_relacion['last_approval_status_date'] = pd.to_datetime(
                    df_relacion['last_approval_status_date'],
                    errors='coerce',  # Valores inválidos se vuelven NaT
                    dayfirst=True,    # CRÍTICO: día primero para formato DD/MM/YYYY
                    format='mixed'    # Permite formatos mixtos
                )
                # Convertir a formato DD/MM/YYYY
                df_relacion['last_approval_status_date'] = df_relacion['last_approval_status_date'].dt.strftime('%d/%m/%Y')
                # Reemplazar NaT con string vacío
                df_relacion['last_approval_status_date'] = df_relacion['last_approval_status_date'].fillna('')
                valores_validos = (df_relacion['last_approval_status_date'] != '').sum()
                print(f"      ✅ Fechas normalizadas: {valores_validos}/{len(df_relacion)}")
                logger.info(f"Fechas normalizadas en last_approval_status_date: {valores_validos}/{len(df_relacion)}")
                if valores_validos > 0:
                    print(f"      📋 Ejemplo: {df_relacion[df_relacion['last_approval_status_date'] != '']['last_approval_status_date'].iloc[0]}")
            except Exception as e:
                print(f"      ⚠️ Error normalizando 'last_approval_status_date': {str(e)}")
                logger.error(f"Error normalizando last_approval_status_date: {str(e)}")
                print(f"      Manteniendo valores originales...")
        else:
            print("\n[1.1.1] ℹ️ Columna 'last_approval_status_date' no encontrada en el archivo")
            logger.warning("Columna 'last_approval_status_date' no encontrada")
        
        # PASO CRÍTICO: FILTRAR POR CÓDIGOS
        print(f"\n[1.2] Aplicando filtro de {len(CODIGOS_FILTRO)} códigos...")
        print(f"      Códigos a buscar: {CODIGOS_FILTRO}")
        logger.info(f"[1.2] Aplicando filtro de {len(CODIGOS_FILTRO)} códigos...")
        logger.debug(f"Códigos de filtro: {CODIGOS_FILTRO}")

        if 'homologacion_clase_de_ausentismo_ssf_vs_sap' not in df_relacion.columns:
            logger.error("❌ Falta columna 'homologacion_clase_de_ausentismo_ssf_vs_sap'")
            logger.error(f"Columnas disponibles: {list(df_relacion.columns)}")
            print("      ❌ Falta columna 'homologacion_clase_de_ausentismo_ssf_vs_sap'")
            print(f"      Columnas disponibles: {list(df_relacion.columns)}")
            return None

        # DIAGNÓSTICO: Mostrar valores únicos ANTES del filtro
        print(f"\n[1.2.1] DIAGNÓSTICO: Analizando valores en columna 'homologacion_clase_de_ausentismo_ssf_vs_sap'...")
        valores_unicos_raw = df_relacion['homologacion_clase_de_ausentismo_ssf_vs_sap'].unique()
        print(f"      Total de valores únicos: {len(valores_unicos_raw)}")
        print(f"      Primeros 20 valores encontrados en el archivo:")
        for i, val in enumerate(valores_unicos_raw[:20], 1):
            count = (df_relacion['homologacion_clase_de_ausentismo_ssf_vs_sap'] == val).sum()
            print(f"         {i:2d}. '{val}' ({count:,} registros)")

        logger.debug(f"Valores únicos antes del filtro: {valores_unicos_raw[:30]}")

        # Limpiar y filtrar
        antes = len(df_relacion)
        print(f"\n[1.2.2] Limpiando valores (strip y eliminando .0) y aplicando filtro...")
        # Convertir a string, hacer strip y eliminar el .0 al final si existe
        df_relacion['homologacion_clase_de_ausentismo_ssf_vs_sap'] = (
            df_relacion['homologacion_clase_de_ausentismo_ssf_vs_sap']
            .astype(str)
            .str.strip()
            .str.replace(r'\.0$', '', regex=True)  # Eliminar .0 al final
        )
        print(f"      ✅ Valores limpiados (eliminado '.0' al final)")
        logger.info("Valores limpiados: eliminado '.0' al final de los códigos")

        # Verificar cuántos registros coinciden con cada código del filtro
        print(f"      Verificando coincidencias por código:")
        coincidencias_por_codigo = {}
        for codigo in CODIGOS_FILTRO:
            count = (df_relacion['homologacion_clase_de_ausentismo_ssf_vs_sap'] == codigo).sum()
            coincidencias_por_codigo[codigo] = count
            if count > 0:
                print(f"         ✅ Código '{codigo}': {count:,} registros")

        # Mostrar códigos sin coincidencias
        codigos_sin_match = [c for c, count in coincidencias_por_codigo.items() if count == 0]
        if codigos_sin_match:
            print(f"      ⚠️ Códigos sin coincidencias: {codigos_sin_match}")

        df_relacion = df_relacion[df_relacion['homologacion_clase_de_ausentismo_ssf_vs_sap'].isin(CODIGOS_FILTRO)]
        despues = len(df_relacion)

        logger.info(f"Antes del filtro: {antes} registros")
        logger.info(f"Después del filtro: {despues} registros")
        logger.info(f"Registros filtrados: {antes - despues}")

        print(f"      Antes: {antes} | Después: {despues} | Filtrados: {antes - despues}")

        if despues == 0:
            logger.error("❌ No quedaron registros después del filtro")
            print("      ❌ No quedaron registros después del filtro")
            return None
        
        # La validación de diagnóstico se hará DESPUÉS del merge con CIE-10
        print("\n[1.3] La validación de diagnóstico se realizará después del merge con CIE-10...")
        
        # ============================================
        # PARTE 2: MERGE CON CIE 10
        # ============================================
        print("\n[PARTE 2/2] MERGE CON CIE 10")
        print("-" * 80)
        
        print("\n[2.1] Leyendo tabla CIE 10...")
        logger.info("[2.1] Iniciando lectura de tabla CIE 10...")
        logger.debug(f"Verificando existencia del archivo CIE10: {os.path.exists(ruta_cie10)}")
        logger.debug(f"Ruta absoluta CIE10: {os.path.abspath(ruta_cie10)}")

        df_cie10 = pd.read_excel(ruta_cie10, dtype=str)
        logger.info(f"✅ CIE 10 leído exitosamente")
        logger.info(f"Registros CIE10: {len(df_cie10)}")
        logger.debug(f"Columnas CIE10: {list(df_cie10.columns)}")
        logger.debug(f"Primeras 2 filas CIE10:\n{df_cie10.head(2)}")

        print(f"      Registros: {len(df_cie10)}")

        # Verificar columnas CIE 10
        if 'Código' not in df_cie10.columns:
            logger.error("❌ Falta columna 'Código' en CIE 10")
            logger.error(f"Columnas disponibles en CIE10: {list(df_cie10.columns)}")
            print("      ❌ Falta columna 'Código' en CIE 10")
            return None
        
        columnas_cie10 = ['Código', 'Descripción', 'TIPO', 'Clasificación Sistemas JMC']
        df_cie10_subset = df_cie10[[col for col in columnas_cie10 if col in df_cie10.columns]].copy()
        
        # Verificar columna de merge en df_relacion
        if 'descripcion_general_external_code' not in df_relacion.columns:
            logger.warning("⚠️ Falta columna 'descripcion_general_external_code'")
            logger.warning("Saltando merge con CIE 10...")
            print("      ⚠️  Falta columna 'descripcion_general_external_code'")
            print("      Saltando merge con CIE 10...")
            df_final = df_relacion
        else:
            print("\n[2.2] Realizando merge LEFT con CIE 10...")
            logger.info("[2.2] Realizando merge LEFT con CIE 10...")

            # Limpiar código: quitar asteriscos, espacios y convertir a mayúsculas
            df_relacion['codigo_clean'] = df_relacion['descripcion_general_external_code'].str.strip().str.replace('*', '', regex=False).str.upper()
            df_cie10_subset['Código_clean'] = df_cie10_subset['Código'].str.strip().str.replace('*', '', regex=False).str.upper()

            logger.debug(f"Códigos limpiados en relacion_laboral (primeros 10): {df_relacion['codigo_clean'].dropna().unique()[:10]}")
            logger.debug(f"Códigos limpiados en CIE10 (primeros 10): {df_cie10_subset['Código_clean'].dropna().unique()[:10]}")

            codigos_base = set(df_relacion['codigo_clean'].dropna())
            codigos_cie10 = set(df_cie10_subset['Código_clean'].dropna())
            coincidencias_cie = codigos_base.intersection(codigos_cie10)

            logger.info(f"Total códigos únicos en relación laboral: {len(codigos_base)}")
            logger.info(f"Total códigos únicos en CIE10: {len(codigos_cie10)}")
            logger.info(f"Coincidencias: {len(coincidencias_cie)}/{len(codigos_base)} ({(len(coincidencias_cie)/len(codigos_base)*100):.1f}%)")
            logger.debug(f"Ejemplos de coincidencias: {list(coincidencias_cie)[:10]}")

            print(f"      Coincidencias: {len(coincidencias_cie)}/{len(codigos_base)} ({(len(coincidencias_cie)/len(codigos_base)*100):.1f}%)")
            
            logger.debug("Ejecutando pd.merge...")
            df_final = pd.merge(
                df_relacion,
                df_cie10_subset,
                left_on='codigo_clean',
                right_on='Código_clean',
                how='left',
                suffixes=('', '_cie10')
            )
            logger.info(f"✅ Merge completado. Registros resultantes: {len(df_final)}")
            logger.debug(f"Columnas después del merge: {list(df_final.columns)}")

            # Renombrar columnas CIE 10
            renombrado = {
                'Código': 'cie10_codigo',
                'Descripción': 'cie10_descripcion',
                'TIPO': 'cie10_tipo',
                'Clasificación Sistemas JMC': 'cie10_clasificacion_sistemas_jmc'
            }
            df_final = df_final.rename(columns={col: renombrado.get(col, col) for col in df_final.columns if col in renombrado})
            logger.debug("Columnas CIE 10 renombradas correctamente")

            # Limpiar columnas temporales
            df_final = df_final.drop(['codigo_clean'], axis=1)
            if 'Código_clean' in df_final.columns:
                df_final = df_final.drop(['Código_clean'], axis=1)
            logger.debug("Columnas temporales eliminadas")

            registros_con_cie10 = df_final['cie10_codigo'].notna().sum() if 'cie10_codigo' in df_final.columns else 0
            logger.info(f"Registros con CIE 10: {registros_con_cie10} ({(registros_con_cie10/len(df_final)*100):.1f}%)")
            print(f"      ✅ Registros con CIE 10: {registros_con_cie10} ({(registros_con_cie10/len(df_final)*100):.1f}%)")
        
        # ============================================
        # CREAR ALERTA_DIAGNOSTICO (DESPUÉS DEL MERGE)
        # ============================================
        print("\n[2.3] Creando columna ALERTA_DIAGNOSTICO...")
        print("      Validando códigos de diagnóstico vs CIE-10...")
        
        def validar_diagnostico_final(row):
            codigo_diag = str(row['descripcion_general_external_code']).strip() if 'descripcion_general_external_code' in row else ''
            tiene_cie10 = pd.notna(row.get('cie10_codigo', None)) and str(row.get('cie10_codigo', '')).strip() != ''
            
            # Si NO tiene código de diagnóstico → ALERTA
            if codigo_diag == '' or codigo_diag.lower() in ['nan', 'none', 'nat', 'null']:
                return 'ALERTA DIAGNOSTICO'
            
            # Si tiene código PERO NO hizo match con CIE-10 → ALERTA
            if not tiene_cie10:
                return 'ALERTA DIAGNOSTICO'
            
            # Si tiene código Y sí hizo match con CIE-10 → OK (sin alerta)
            return ''
        
        df_final['alerta_diagnostico'] = df_final.apply(validar_diagnostico_final, axis=1)
        alertas = (df_final['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO').sum()
        total = len(df_final)
        print(f"      ✅ Alertas generadas: {alertas} de {total} ({(alertas/total*100):.1f}%)")
        
        if alertas > 0:
            print(f"      📋 Muestra de 3 registros con alerta:")
            df_con_alerta = df_final[df_final['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO']
            cols_mostrar = ['descripcion_general_external_code', 'cie10_codigo']
            if 'external_name_label' in df_final.columns:
                cols_mostrar.insert(0, 'external_name_label')
            print(df_con_alerta[cols_mostrar].head(3).to_string(index=False))
        
        # ============================================
        # GENERAR EXCEL DE ALERTA DIAGNOSTICO
        # ============================================
        print("\n[2.4] Generando Excel de ALERTA_DIAGNOSTICO...")
        
        if 'alerta_diagnostico' in df_final.columns:
            df_alertas = df_final[df_final['alerta_diagnostico'] == 'ALERTA DIAGNOSTICO'].copy()
            
            if len(df_alertas) > 0:
                archivo_alertas = os.path.join(directorio_salida, "ALERTA_DIAGNOSTICO.xlsx")
                df_alertas.to_excel(archivo_alertas, index=False, engine='openpyxl')
                print(f"      ✅ Excel generado: {len(df_alertas)} registros con alerta")
                print(f"      📁 {archivo_alertas}")
            else:
                print(f"      ℹ️  No hay registros con ALERTA DIAGNOSTICO")
        else:
            print(f"      ⚠️  Columna 'alerta_diagnostico' no existe")
        
        # ============================================
        # GUARDAR ARCHIVO FINAL
        # ============================================
        print("\n[GUARDANDO ARCHIVO FINAL]")
        print("-" * 80)
        logger.info("[GUARDANDO ARCHIVO FINAL]")
        logger.debug(f"Directorio de salida: {directorio_salida}")
        logger.debug(f"Ruta completa de salida: {ruta_completa_salida}")

        if not os.path.exists(directorio_salida):
            logger.warning(f"Directorio de salida no existe. Creándolo: {directorio_salida}")
            os.makedirs(directorio_salida)
            logger.info("✅ Directorio de salida creado")

        logger.info("Guardando archivo CSV...")
        df_final.to_csv(ruta_completa_salida, index=False, encoding='utf-8-sig', quoting=1, lineterminator='\n')
        logger.info(f"✅ Archivo CSV guardado exitosamente")
        logger.debug(f"Tamaño del archivo: {os.path.getsize(ruta_completa_salida)} bytes")

        registros_con_cie10 = df_final['cie10_codigo'].notna().sum() if 'cie10_codigo' in df_final.columns else 0

        print("\n" + "=" * 80)
        print("✅ PROCESO COMPLETADO")
        print("=" * 80)
        print(f"Registros finales: {len(df_final)}")
        print(f"Columnas totales: {len(df_final.columns)}")
        print(f"Con CIE 10: {registros_con_cie10}")
        print(f"Archivo: {ruta_completa_salida}")
        print("=" * 80)

        logger.info("=" * 80)
        logger.info("✅ PROCESO COMPLETADO EXITOSAMENTE")
        logger.info("=" * 80)
        logger.info(f"Registros finales: {len(df_final)}")
        logger.info(f"Columnas totales: {len(df_final.columns)}")
        logger.info(f"Con CIE 10: {registros_con_cie10}")
        logger.info(f"Archivo: {ruta_completa_salida}")
        logger.info("=" * 80)

        return df_final
        
    except FileNotFoundError as e:
        logger.error("=" * 80)
        logger.error("❌ ERROR: Archivo no encontrado")
        logger.error(f"Detalles: {str(e)}")
        logger.error("=" * 80)
        print(f"\n❌ ERROR: Archivo no encontrado")
        print(f"   {str(e)}")
        return None

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR INESPERADO: {str(e)}")
        logger.error("=" * 80)
        import traceback
        logger.error("Traceback completo:")
        logger.error(traceback.format_exc())
        logger.error("=" * 80)
        print(f"\n❌ ERROR: {str(e)}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("INICIANDO SCRIPT PART 3")
    logger.info("=" * 80)

    print("\nVerificando archivos de entrada...")
    logger.info("Verificando archivos de entrada...")

    archivos = {
        "Relación Laboral": ruta_relacion_laboral,
        "CIE 10": ruta_cie10
    }

    todos_ok = True
    for nombre, ruta in archivos.items():
        existe = os.path.exists(ruta)
        if existe:
            logger.info(f"✅ {nombre} encontrado: {ruta}")
            print(f"   ✅ {nombre}")
        else:
            logger.error(f"❌ {nombre} NO ENCONTRADO: {ruta}")
            print(f"   ❌ {nombre}: NO ENCONTRADO")
            todos_ok = False

    if todos_ok:
        logger.info("✅ Todos los archivos encontrados. Iniciando proceso...")
        print("\n¡Todos los archivos encontrados! Iniciando proceso...\n")
        resultado = procesar_todo()
        if resultado is None:
            logger.error("❌ El proceso falló.")
            print("\n❌ El proceso falló.")
        else:
            logger.info("✅ Proceso completado con éxito")
    else:
        logger.error("❌ Faltan archivos. Verifica las rutas.")
        print("\n❌ Verifica las rutas de los archivos.")

    logger.info("=" * 80)
    logger.info("FIN DEL SCRIPT PART 3")
    logger.info("=" * 80)
