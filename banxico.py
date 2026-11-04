# Práctica 11: una API con token (Banco de México)
# Herramientas de Visualización · IDIA224 · Unidad II
#
#     pip install requests pandas matplotlib seaborn
#     python practica11_banxico.py
#
# Antes de ejecutar necesitas un token gratuito del SIE de Banxico:
#     https://www.banxico.org.mx/SieAPIRest/service/v1/token
# Guárdalo en un archivo token.txt, en la MISMA carpeta desde la que
# ejecutas el script, en texto plano y en un solo renglón.
# Ese archivo nunca se sube a GitHub ni se comparte con nadie.

import os

import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns

# ─── Paleta del curso ──────────────────────────────────────────────────
GRIS = "#B9C3D1"
AZUL = "#1C4C9A"
ROJO = "#B2182B"
sns.set_theme(style="whitegrid")


# ─── Paso 1 · Leer el token sin escribirlo en el código ────────────────
# Se valida al leerlo: un token vacío produce el mismo error que una URL
# mal escrita, y si no se detecta aquí el problema aparece veinte líneas
# después, apuntando al lugar equivocado.
def leer_token():
    token = os.environ.get("BANXICO_TOKEN")
    if token and token.strip():
        return token.strip()

    if os.path.exists("token.txt"):
        with open("token.txt", encoding="utf-8") as f:
            token = f.read().strip()
        if len(token) >= 32:
            return token
        print(f"token.txt existe pero tiene {len(token)} caracteres.")
        print("El token del SIE son 64. Revisa que esté completo,")
        print("en texto plano y sin comillas.")
        raise SystemExit(1)

    print("No encontré token.txt en esta carpeta:")
    print("  ", os.getcwd())
    print("Consíguelo gratis en:")
    print("  https://www.banxico.org.mx/SieAPIRest/service/v1/token")
    raise SystemExit(1)


TOKEN = leer_token()
print("Token leído:", len(TOKEN), "caracteres")


# ─── Paso 2 · Pedir la serie ───────────────────────────────────────────
# SF43718 es el tipo de cambio FIX, pesos por dólar.
# El catálogo completo de series está en el sitio del SIE.
SERIES = "SF43718"
#SERIES = "SR1501"
INICIO = "2021-01-01"
FIN = "2025-12-31"

url = (f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/"
       f"{SERIES}/datos/{INICIO}/{FIN}")

respuesta = requests.get(
    url,
    headers={
        "Bmx-Token": TOKEN,
        "Accept": "application/json",
        "User-Agent": "UPQ-IDIA224/1.0",
    },
    timeout=60,
)

print("Código de estado:", respuesta.status_code)
print("Tipo de contenido:", respuesta.headers.get("Content-Type"))

if respuesta.status_code == 401:
    print("Token rechazado. Pide uno nuevo o revisa que esté completo.")
    raise SystemExit(1)

respuesta.raise_for_status()

# Un 200 no garantiza que llegó JSON: el servidor puede contestar con una
# página de error y seguir siendo un 200 válido. Hay que comprobarlo.
if "json" not in (respuesta.headers.get("Content-Type") or ""):
    print("\nLa respuesta NO es JSON. Esto fue lo que llegó:")
    print(respuesta.text[:300])
    print("\nCausas más comunes:")
    print("  - El token está vacío, incompleto o ya no es válido.")
    print("  - La red bloquea la salida hacia banxico.org.mx.")
    raise SystemExit(1)

datos = respuesta.json()


# ─── Paso 3 · Ver cómo viene armada la respuesta ───────────────────────
# Aquí los datos están más anidados que en Open-Meteo:
# bmx -> series -> [0] -> datos -> lista de {fecha, dato}
print("\nLlaves del primer nivel:", list(datos.keys()))
print("Series recibidas:", len(datos["bmx"]["series"]))

serie = datos["bmx"]["series"][0]
print("Identificador:", serie["idSerie"])
print("Título que declara Banxico:", serie.get("titulo"))
print("Primer registro tal como llega:", serie["datos"][0])


# ─── Paso 4 · De la lista de diccionarios a una tabla ──────────────────
df = pd.DataFrame(serie["datos"])
print("\nTipos de dato al cargar:")
print(df.dtypes)

# La fecha llega como texto en formato día/mes/año
df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y")

# El valor TAMBIÉN llega como texto, y en los días inhábiles trae "N/E".
# errors="coerce" convierte lo que no sea número en NaN, en vez de tronar.
sin_dato = (df["dato"] == "N/E").sum()
df["dato"] = pd.to_numeric(df["dato"].str.replace(",", "", regex=False),
                           errors="coerce")

df = df.rename(columns={"fecha": "Fecha", "dato": "TipoCambio"})
df["Anio"] = df["Fecha"].dt.year
df["Mes"] = df["Fecha"].dt.month

print("\nRegistros recibidos:", len(df))
print("Días marcados como N/E (inhábiles):", sin_dato)
print("Valores nulos después de convertir:", df["TipoCambio"].isna().sum())

# Para graficar se trabaja solo con los días que sí tienen dato
df = df.dropna(subset=["TipoCambio"]).reset_index(drop=True)
print("Registros utilizables:", len(df))
print("Periodo:", df["Fecha"].min().date(), "a", df["Fecha"].max().date())
print("\nResumen:")
print(df["TipoCambio"].describe().round(4).to_string())


# ─── Gráfica 1 · La serie y su tendencia ───────────────────────────────
df["Media30"] = df["TipoCambio"].rolling(window=30).mean()

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(df["Fecha"], df["TipoCambio"], color=GRIS, linewidth=0.9,
        label="Valor diario")
ax.plot(df["Fecha"], df["Media30"], color=AZUL, linewidth=2,
        label="Media móvil 30 días")
ax.set_title(serie.get("titulo", "Serie de Banxico"))
ax.set_xlabel("Fecha")
ax.set_ylabel("Pesos por dólar")
ax.legend(frameon=False)
fig.savefig("g1_serie.png", dpi=150, bbox_inches="tight")


# ─── Gráfica 2 · Qué tanto se movió cada año ───────────────────────────
# Variación diaria en por ciento, para comparar años entre sí.
df["Variacion"] = df["TipoCambio"].pct_change() * 100

fig, ax = plt.subplots(figsize=(10, 4.5))
sns.boxplot(data=df.dropna(subset=["Variacion"]), x="Anio", y="Variacion",
            color=GRIS, ax=ax)
ax.axhline(0, color=ROJO, linewidth=1, linestyle="--")
ax.set_title("Qué tan movido estuvo el peso cada año")
ax.set_xlabel("Año")
ax.set_ylabel("Variación diaria (%)")
fig.savefig("g2_variacion.png", dpi=150, bbox_inches="tight")

print("\nVariación diaria por año (desviación estándar, en %):")
print(df.groupby("Anio")["Variacion"].std().round(3).to_string())

plt.show()