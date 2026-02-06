"""
Script de diagnóstico para validación de Integral
"""
import pandas as pd
import os

print("="*80)
print("DIAGNÓSTICO DE VALIDACIÓN INTEGRAL")
print("="*80)

# Ruta del archivo (AJUSTA ESTA RUTA A TU ARCHIVO REAL)
archivo_entrada = r"C:\Users\jjbustos\OneDrive - Grupo Jerónimo Martins\Documents\auditoria ausentismos\archivos_salida\relacion_laboral.csv"

try:
    # Leer archivo
    print("\n1. Leyendo archivo...")
    df = pd.read_csv(archivo_entrada, low_memory=False)
    print(f"   ✓ Total registros: {len(df):,}")

    # Verificar columnas
    print("\n2. Verificando columnas...")
    if 'Relación laboral' in df.columns:
        print("   ✓ Columna 'Relación laboral' existe")
    else:
        print("   ✗ Columna 'Relación laboral' NO existe")
        print(f"   Columnas disponibles: {list(df.columns)}")

    if 'homologacion_clase_de_ausentismo_ssf_vs_sap' in df.columns:
        print("   ✓ Columna 'homologacion_clase_de_ausentismo_ssf_vs_sap' existe")
    else:
        print("   ✗ Columna 'homologacion_clase_de_ausentismo_ssf_vs_sap' NO existe")
        print(f"   Columnas disponibles: {list(df.columns)}")

    # Verificar valores de Relación laboral
    print("\n3. Valores únicos en 'Relación laboral':")
    valores_rel_laboral = df['Relación laboral'].value_counts()
    for valor, cantidad in valores_rel_laboral.items():
        print(f"   - '{valor}': {cantidad} registros")

    # Filtrar Integral
    print("\n4. Filtrando registros con 'Integral'...")
    df_integral = df[df['Relación laboral'].str.contains('Integral', case=False, na=False)].copy()
    print(f"   ✓ Registros con Integral: {len(df_integral):,}")

    if len(df_integral) > 0:
        # Verificar códigos en Integral
        print("\n5. Códigos en registros de Integral:")
        print(f"   Tipo de datos en columna: {df_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'].dtype}")

        # Mostrar primeros 20 códigos únicos
        codigos_unicos = df_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'].value_counts().head(20)
        print(f"   Códigos únicos (top 20):")
        for codigo, cantidad in codigos_unicos.items():
            print(f"      {codigo}: {cantidad} registros")

        # Códigos prohibidos
        codigos_prohibidos = [380, 330, 291, 204, 202, 215, 210, 220, 200,
                              281, 280, 340, 345, 305, 398, 302, 300, 191,
                              310, 190, 232, 250, 230, 381, 198]

        print(f"\n6. Buscando códigos prohibidos...")
        print(f"   Códigos prohibidos: {codigos_prohibidos}")

        # Convertir a numérico
        df_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'] = pd.to_numeric(
            df_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'],
            errors='coerce'
        )

        # Buscar errores
        df_errores = df_integral[
            df_integral['homologacion_clase_de_ausentismo_ssf_vs_sap'].isin(codigos_prohibidos)
        ].copy()

        print(f"\n7. RESULTADO:")
        print(f"   ✓ Errores encontrados: {len(df_errores):,}")

        if len(df_errores) > 0:
            print(f"\n   Códigos prohibidos encontrados:")
            errores_por_codigo = df_errores['homologacion_clase_de_ausentismo_ssf_vs_sap'].value_counts()
            for codigo, cantidad in errores_por_codigo.items():
                print(f"      Código {int(codigo)}: {cantidad} registros")

            print(f"\n   Muestra de registros con error:")
            print(df_errores[['id_personal', 'nombre_completo', 'Relación laboral',
                             'homologacion_clase_de_ausentismo_ssf_vs_sap', 'external_name_label']].head(3))
        else:
            print(f"   ✓ NO HAY ERRORES - Ningún registro de Integral tiene códigos prohibidos")
    else:
        print("   ⚠️ No hay registros con Integral para analizar")

    print("\n" + "="*80)
    print("DIAGNÓSTICO COMPLETADO")
    print("="*80)

except FileNotFoundError:
    print(f"\n✗ ERROR: No se encontró el archivo")
    print(f"   Verifica la ruta: {archivo_entrada}")
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
