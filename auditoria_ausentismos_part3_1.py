"""
Auditoría de Ausentismos - Parte 3.1
PRE-FILTRADO para Análisis de 30 Días

Aplica filtros específicos antes del análisis de 30 días:
1. Filtrar por last_approval_status_date (rango de fechas)
2. Extraer id_personal únicos
3. Filtrar base completa por esos IDs
4. Filtrar por start_date (mes completo automático)
5. Ordenar: id_personal (asc), start_date (desc)

El resultado se puede usar directamente en auditoria_ausentismos_part4.py
"""

import pandas as pd
import os
import calendar
from datetime import date

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================

# Rutas (se configurarán desde app.py o manualmente)
ruta_entrada = ""
ruta_salida = ""

# Fechas de filtrado (se configurarán desde app.py o manualmente)
fecha_ultima_inicio = None  # date object
fecha_ultima_fin = None     # date object

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def aplicar_prefiltrado():
    """
    Aplica el pre-filtrado de 5 pasos para preparar datos para análisis de 30 días.

    Pasos:
    1. Filtrar por last_approval_status_date (rango)
    2. Extraer id_personal únicos
    3. Filtrar base completa por esos IDs
    4. Filtrar por start_date (mes completo de fecha_ultima_inicio)
    5. Ordenar: id_personal (asc), start_date (desc)

    Returns:
        DataFrame filtrado o None si hay error
    """

    print("=" * 80)
    print("PRE-FILTRADO PARA ANÁLISIS DE 30 DÍAS")
    print("=" * 80)

    # Validar configuración
    if not ruta_entrada:
        print("❌ ERROR: ruta_entrada no está configurada")
        return None

    if not os.path.exists(ruta_entrada):
        print(f"❌ ERROR: No se encuentra el archivo: {ruta_entrada}")
        return None

    if not fecha_ultima_inicio or not fecha_ultima_fin:
        print("❌ ERROR: Fechas de filtro no configuradas")
        return None

    if not ruta_salida:
        print("❌ ERROR: ruta_salida no está configurada")
        return None

    try:
        # ========================================================================
        # LEER CSV COMPLETO
        # ========================================================================
        print(f"\n📂 Leyendo archivo: {os.path.basename(ruta_entrada)}")

        df_completo = pd.read_csv(
            ruta_entrada,
            encoding='utf-8',
            sep=',',
            quotechar='"'
        )

        # Limpiar nombres de columnas
        df_completo.columns = df_completo.columns.str.strip().str.strip('"').str.strip("'")

        print(f"✅ Registros totales: {len(df_completo):,}")
        print(f"✅ Columnas: {len(df_completo.columns)}")

        # Verificar columnas requeridas
        columnas_requeridas = ['id_personal', 'last_approval_status_date', 'start_date']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df_completo.columns]

        if columnas_faltantes:
            print(f"❌ ERROR: Faltan columnas requeridas: {columnas_faltantes}")
            print(f"   Columnas disponibles: {list(df_completo.columns)}")
            return None

        # ========================================================================
        # CONVERTIR FECHAS
        # ========================================================================
        print("\n📅 Convirtiendo fechas a formato datetime...")

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

        fechas_validas_ultima = df_completo['last_approval_status_date'].notna().sum()
        fechas_validas_start = df_completo['start_date'].notna().sum()

        print(f"✅ Fechas válidas last_approval_status_date: {fechas_validas_ultima:,}")
        print(f"✅ Fechas válidas start_date: {fechas_validas_start:,}")

        # ========================================================================
        # PASO 1: FILTRAR POR LAST_APPROVAL_STATUS_DATE
        # ========================================================================
        print(f"\n[PASO 1] Filtrando por last_approval_status_date...")
        print(f"   Rango: {fecha_ultima_inicio.strftime('%d/%m/%Y')} → {fecha_ultima_fin.strftime('%d/%m/%Y')}")

        fu_inicio_dt = pd.to_datetime(fecha_ultima_inicio)
        fu_fin_dt = pd.to_datetime(fecha_ultima_fin)

        df_filtrado_fecha = df_completo[
            (df_completo['last_approval_status_date'] >= fu_inicio_dt) &
            (df_completo['last_approval_status_date'] <= fu_fin_dt)
        ].copy()

        print(f"✅ Registros con fecha_ultima en rango: {len(df_filtrado_fecha):,}")

        # ========================================================================
        # PASO 2: EXTRAER IDs ÚNICOS
        # ========================================================================
        print(f"\n[PASO 2] Extrayendo id_personal únicos...")

        ids_validos = df_filtrado_fecha['id_personal'].unique()

        print(f"✅ IDs únicos: {len(ids_validos):,}")

        # ========================================================================
        # PASO 3: FILTRAR BASE COMPLETA POR ESOS IDs
        # ========================================================================
        print(f"\n[PASO 3] Filtrando base completa por esos IDs...")

        df_filtrado_ids = df_completo[df_completo['id_personal'].isin(ids_validos)].copy()

        print(f"✅ Registros con esos IDs: {len(df_filtrado_ids):,}")

        # DEBUG: Mostrar fechas disponibles en start_date
        fechas_validas_start = df_filtrado_ids['start_date'].dropna()
        if len(fechas_validas_start) > 0:
            fecha_min_start = fechas_validas_start.min()
            fecha_max_start = fechas_validas_start.max()
            print(f"\n🔍 DEBUG - Fechas start_date disponibles:")
            print(f"   • Mínima: {fecha_min_start.strftime('%d/%m/%Y')}")
            print(f"   • Máxima: {fecha_max_start.strftime('%d/%m/%Y')}")
            print(f"   • Total válidas: {len(fechas_validas_start):,}")
        else:
            print(f"\n⚠️ ADVERTENCIA: No hay fechas start_date válidas en los datos filtrados")

        # ========================================================================
        # PASO 4: FILTRAR POR START_DATE (MES COMPLETO)
        # ========================================================================
        print(f"\n[PASO 4] Filtrando por start_date (mes completo)...")

        # Calcular primer y último día del mes de fecha_ultima_inicio
        primer_dia_mes = date(fecha_ultima_inicio.year, fecha_ultima_inicio.month, 1)
        ultimo_dia = calendar.monthrange(fecha_ultima_inicio.year, fecha_ultima_inicio.month)[1]
        ultimo_dia_mes = date(fecha_ultima_inicio.year, fecha_ultima_inicio.month, ultimo_dia)

        print(f"   Rango: {primer_dia_mes.strftime('%d/%m/%Y')} → {ultimo_dia_mes.strftime('%d/%m/%Y')}")

        sd_inicio_dt = pd.to_datetime(primer_dia_mes)
        sd_fin_dt = pd.to_datetime(ultimo_dia_mes)

        df_filtrado_final = df_filtrado_ids[
            (df_filtrado_ids['start_date'] >= sd_inicio_dt) &
            (df_filtrado_ids['start_date'] <= sd_fin_dt)
        ].copy()

        print(f"✅ Registros con start_date en mes: {len(df_filtrado_final):,}")

        # DEBUG: Si queda en 0, mostrar por qué
        if len(df_filtrado_final) == 0:
            print(f"\n⚠️ ADVERTENCIA: 0 registros después de filtrar por start_date")
            print(f"   Posibles causas:")
            print(f"   1. No hay registros con start_date en {primer_dia_mes.strftime('%B %Y')}")
            print(f"   2. Las fechas están en formato diferente")
            print(f"   3. El mes seleccionado no tiene datos")

            # Mostrar muestra de fechas que SÍ existen
            if len(fechas_validas_start) > 0:
                print(f"\n   📋 Muestra de fechas start_date que SÍ existen:")
                muestra = fechas_validas_start.head(10)
                for i, fecha in enumerate(muestra, 1):
                    print(f"      {i}. {fecha.strftime('%d/%m/%Y')}")

                # Contar registros por mes
                df_filtrado_ids['mes_start'] = df_filtrado_ids['start_date'].dt.to_period('M')
                conteo_por_mes = df_filtrado_ids['mes_start'].value_counts().head(5)
                print(f"\n   📊 Registros por mes (top 5):")
                for mes, count in conteo_por_mes.items():
                    print(f"      {mes}: {count:,} registros")
                df_filtrado_ids = df_filtrado_ids.drop('mes_start', axis=1)

        # ========================================================================
        # PASO 5: ORDENAR
        # ========================================================================
        print(f"\n[PASO 5] Ordenando registros...")

        df_filtrado_final = df_filtrado_final.sort_values(
            by=['id_personal', 'start_date'],
            ascending=[True, False]  # id_personal menor→mayor, start_date reciente→antiguo
        )

        print(f"✅ Ordenado correctamente")

        # ========================================================================
        # CONVERTIR FECHAS DE VUELTA A STRING
        # ========================================================================
        print(f"\n📅 Convirtiendo fechas de vuelta a formato DD/MM/YYYY...")

        df_filtrado_final['last_approval_status_date'] = df_filtrado_final['last_approval_status_date'].dt.strftime('%d/%m/%Y')
        df_filtrado_final['start_date'] = df_filtrado_final['start_date'].dt.strftime('%d/%m/%Y')

        # Convertir otras columnas de fecha si existen
        columnas_fecha_adicionales = ['end_date', 'modificado_el', 'fse_fechas']
        for col in columnas_fecha_adicionales:
            if col in df_filtrado_final.columns:
                # Intentar convertir si no es string
                if df_filtrado_final[col].dtype != 'object':
                    try:
                        df_filtrado_final[col] = pd.to_datetime(df_filtrado_final[col], errors='coerce').dt.strftime('%d/%m/%Y')
                    except:
                        pass

        # ========================================================================
        # GUARDAR CSV FILTRADO
        # ========================================================================
        print(f"\n💾 Guardando CSV filtrado...")

        df_filtrado_final.to_csv(
            ruta_salida,
            index=False,
            encoding='utf-8',
            sep=',',
            quoting=2  # QUOTE_NONNUMERIC
        )

        print(f"✅ Guardado: {os.path.basename(ruta_salida)}")

        # ========================================================================
        # RESUMEN FINAL
        # ========================================================================
        print("\n" + "=" * 80)
        print("RESUMEN DE PRE-FILTRADO")
        print("=" * 80)
        print(f"\n📊 Resultados:")
        print(f"  • Registros iniciales: {len(df_completo):,}")
        print(f"  • Registros después de filtros: {len(df_filtrado_final):,}")
        print(f"  • Reducción: {len(df_completo) - len(df_filtrado_final):,} registros ({((len(df_completo) - len(df_filtrado_final)) / len(df_completo) * 100):.1f}%)")
        print(f"\n📋 Filtros aplicados:")
        print(f"  1. fecha_ultima: {fecha_ultima_inicio.strftime('%d/%m/%Y')} → {fecha_ultima_fin.strftime('%d/%m/%Y')}")
        print(f"  2. IDs únicos extraídos: {len(ids_validos):,}")
        print(f"  3. start_date mes: {primer_dia_mes.strftime('%B %Y')}")
        print(f"  4. Ordenamiento: id_personal (↑), start_date (↓)")
        print(f"\n✅ CSV listo para usar en auditoria_ausentismos_part4.py")
        print("=" * 80)

        return df_filtrado_final

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR EN PRE-FILTRADO")
        print("=" * 80)
        print(f"\n🔴 Tipo de Error: {type(e).__name__}")
        print(f"🔴 Mensaje: {str(e)}")
        print("\n📍 TRACEBACK:")
        import traceback
        traceback.print_exc()
        print("=" * 80)
        return None


# ============================================================================
# EJECUCIÓN DIRECTA (PARA PRUEBAS LOCALES)
# ============================================================================

if __name__ == "__main__":
    # Configuración de ejemplo para ejecución local
    from datetime import date

    # CONFIGURAR ESTAS RUTAS
    ruta_entrada = r"C:\Users\TU_USUARIO\Downloads\ausentismos_completo_con_cie10.csv"
    ruta_salida = r"C:\Users\TU_USUARIO\Downloads\ausentismos_PREFILTRADO.csv"

    # CONFIGURAR ESTAS FECHAS
    fecha_ultima_inicio = date(2026, 1, 3)   # 3 de enero 2026
    fecha_ultima_fin = date(2026, 1, 31)     # 31 de enero 2026

    print("Configuración:")
    print(f"  Entrada: {ruta_entrada}")
    print(f"  Salida: {ruta_salida}")
    print(f"  Fecha última inicio: {fecha_ultima_inicio.strftime('%d/%m/%Y')}")
    print(f"  Fecha última fin: {fecha_ultima_fin.strftime('%d/%m/%Y')}")
    print()

    # Ejecutar pre-filtrado
    df_resultado = aplicar_prefiltrado()

    if df_resultado is not None:
        print(f"\n✅ Pre-filtrado completado exitosamente")
        print(f"   Usa el archivo: {ruta_salida}")
        print(f"   Como entrada para: auditoria_ausentismos_part4.py")
    else:
        print("\n❌ Error en el pre-filtrado")
