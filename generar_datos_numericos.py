import pandas as pd
import time
from sklearn.preprocessing import LabelEncoder

# ============================================================================
# PASO 1: CARGAR DATOS
# ============================================================================
ruta_archivo = r"C:\Users\jjbustos\Downloads\CIE 10 - AJUSTADO - NÓMINA 2.xlsx"

print("Cargando datos...")
inicio = time.time()
df_original = pd.read_excel(ruta_archivo)
print(f"✓ Cargado en {time.time() - inicio:.2f}s")

print(f"\n{'=' * 80}")
print(f"DATASET ORIGINAL")
print(f"{'=' * 80}")
print(f"Dimensiones: {df_original.shape[0]} filas x {df_original.shape[1]} columnas")
print(f"\nColumnas: {list(df_original.columns)}")

print(f"\nPrimeras 5 filas ORIGINALES:")
print(df_original.head())

# ============================================================================
# PASO 2: TRANSFORMAR CATEGÓRICO A NUMÉRICO
# ============================================================================
print(f"\n{'=' * 80}")
print(f"TRANSFORMANDO CATEGÓRICO A NUMÉRICO")
print(f"{'=' * 80}")
print("Regla: La misma categoría = el mismo número en todas las filas\n")

inicio = time.time()

# Crear copia para transformar
df_numerico = df_original.copy()

# Diccionario para guardar los mapeos
mapeos = {}

# Columnas que NO se deben transformar
columnas_mantener = ['Código', 'Descripción']

# Transformar cada columna (excepto Código y Descripción)
for columna in df_numerico.columns:
    if columna in columnas_mantener:
        print(f"Manteniendo sin cambios: {columna}")
        continue

    if df_numerico[columna].dtype == 'object':  # Si es texto/categórico
        print(f"Transformando: {columna}")

        # Limpiar espacios en blanco y manejar vacíos
        df_numerico[columna] = df_numerico[columna].fillna('VACIO')
        df_numerico[columna] = df_numerico[columna].astype(str).str.strip()
        df_numerico[columna] = df_numerico[columna].replace('', 'VACIO')
        df_numerico[columna] = df_numerico[columna].replace('nan', 'VACIO')

        # Crear el codificador
        le = LabelEncoder()

        # Transformar a números
        valores_codificados = le.fit_transform(df_numerico[columna])

        # AJUSTAR: VACIO siempre debe ser 0.0
        if 'VACIO' in le.classes_:
            # Crear nuevo mapeo donde VACIO = 0.0 y los demás se desplazan
            nuevo_mapeo = {}
            nuevo_mapeo['VACIO'] = 0.0

            contador = 1.0
            for categoria in sorted(le.classes_):
                if categoria != 'VACIO':
                    nuevo_mapeo[categoria] = contador
                    contador += 1.0

            # Aplicar el nuevo mapeo
            df_numerico[columna] = df_numerico[columna].map(nuevo_mapeo)
            mapeos[columna] = nuevo_mapeo
        else:
            # Si no hay vacíos, mapear desde 1.0
            nuevo_mapeo = {}
            contador = 1.0
            for categoria in sorted(le.classes_):
                nuevo_mapeo[categoria] = contador
                contador += 1.0

            df_numerico[columna] = df_numerico[columna].map(nuevo_mapeo)
            mapeos[columna] = nuevo_mapeo

        # Convertir a float
        df_numerico[columna] = df_numerico[columna].astype(float)

        # Mostrar resumen
        print(f"  Valores únicos: {len(mapeos[columna])}")
        print(f"  0.0 = VACIO (valores vacíos)")
        print(f"  Categorías reales: desde 1.0 hasta {len(mapeos[columna]) - 1.0 if 'VACIO' in mapeos[columna] else len(mapeos[columna])}.0")
        print()

print(f"✓ Transformación completada en {time.time() - inicio:.2f}s")

# ============================================================================
# PASO 3: MOSTRAR RESULTADO
# ============================================================================
print(f"\n{'=' * 80}")
print(f"DATASET TRANSFORMADO A NÚMEROS")
print(f"{'=' * 80}")

print(f"\nPrimeras 5 filas NUMÉRICAS:")
print(df_numerico.head())

print(f"\nTipos de datos:")
print(df_numerico.dtypes)

print(f"\nVerificación - Ejemplo con primeras 3 filas:")
print(f"\nCódigo y Descripción se mantienen sin cambios:")
for i in range(min(3, len(df_numerico))):
    print(f"  Código: {df_numerico.iloc[i]['Código']}")
    if 'GRUPO' in df_numerico.columns:
        print(f"  GRUPO: {df_original.iloc[i]['GRUPO']} -> {df_numerico.iloc[i]['GRUPO']:.0f}")
    print()

# ============================================================================
# PASO 4: GUARDAR ARCHIVOS
# ============================================================================
print(f"\n{'=' * 80}")
print(f"GUARDANDO ARCHIVOS")
print(f"{'=' * 80}")

# Guardar SOLO el CSV principal
df_numerico.to_csv('datos_numericos.csv', index=False, encoding='utf-8-sig', float_format='%.1f')
print(f"✓ datos_numericos.csv guardado")

# Guardar mapeos en TXT con formato: Código | Número | Categoría
with open('codigos_mapeo.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("MAPEO DE CÓDIGOS: NÚMERO Y CATEGORÍA\n")
    f.write("=" * 80 + "\n")
    f.write("Formato: Columna -> Número = Categoría\n")
    f.write("Nota: Valores vacíos = 0.0\n\n")

    for columna, mapeo in mapeos.items():
        f.write(f"\n{'-' * 80}\n")
        f.write(f"{columna} ({len(mapeo)} categorías únicas):\n")
        f.write(f"{'-' * 80}\n")

        # Ordenar por número
        for categoria, numero in sorted(mapeo.items(), key=lambda x: x[1]):
            f.write(f"{numero:>6.1f} = {categoria}\n")

print(f"✓ codigos_mapeo.txt guardado")

# ============================================================================
# PASO 5: ESTADÍSTICAS BÁSICAS
# ============================================================================
print(f"\n{'=' * 80}")
print(f"ESTADÍSTICAS DEL DATASET NUMÉRICO")
print(f"{'=' * 80}")

print(f"\nRango de valores por columna:")
for col in df_numerico.columns:
    print(f"  {col}:")
    if col in columnas_mantener:
        print(f"    Tipo: Texto (sin transformar)")
        print(f"    Valores únicos: {df_numerico[col].nunique()}")
    else:
        print(f"    Mínimo: {df_numerico[col].min():.0f}")
        print(f"    Máximo: {df_numerico[col].max():.0f}")
        print(f"    Valores únicos: {df_numerico[col].nunique()}")

# ============================================================================
# RESUMEN
# ============================================================================
print(f"\n{'=' * 80}")
print(f"✅ TRANSFORMACIÓN COMPLETADA")
print(f"{'=' * 80}")

print(f"\n📁 Archivos generados:")
print(f"   1. datos_numericos.csv - Dataset transformado a números")
print(f"   2. codigos_mapeo.txt - Mapeo completo de números y categorías")

print(f"\n💡 Verificación importante:")
print(f"   • Si dos filas tienen la misma categoría, tienen el mismo número")
print(f"   • Valores vacíos = 0.0")
print(f"   • Formato: FLOAT (ejemplo: 90.0)")

print(f"\n{'=' * 80}")
print(f"✓ PROCESO FINALIZADO")
print(f"{'=' * 80}")
