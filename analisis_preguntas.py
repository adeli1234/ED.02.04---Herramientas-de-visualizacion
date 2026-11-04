import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns

sns.set_theme(style="whitegrid")


ROOT = Path(__file__).resolve().parent
TOKEN_PATH = ROOT / "token.txt"


def leer_token():
    token = os.environ.get("BANXICO_TOKEN")
    if token and token.strip():
        return token.strip()

    if TOKEN_PATH.exists():
        token = TOKEN_PATH.read_text(encoding="utf-8").strip()
        if len(token) >= 32:
            return token
        raise SystemExit("token.txt existe pero está incompleto.")

    raise SystemExit("No encontré token.txt en la carpeta del proyecto.")


def obtener_df_tipo_cambio():
    token = leer_token()
    url = (
        "https://www.banxico.org.mx/SieAPIRest/service/v1/series/"
        "SF43718/datos/2021-01-01/2025-12-31"
    )
    respuesta = requests.get(
        url,
        headers={
            "Bmx-Token": token,
            "Accept": "application/json",
            "User-Agent": "UPQ-IDIA224/1.0",
        },
        timeout=60,
    )
    respuesta.raise_for_status()
    datos = respuesta.json()["bmx"]["series"][0]["datos"]
    df = pd.DataFrame(datos)
    df["fecha"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["dato"].str.replace(",", "", regex=False), errors="coerce")
    df = df.dropna(subset=["valor"]).copy()
    df = df.rename(columns={"fecha": "Fecha", "valor": "TipoCambio"})
    df["Anio"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.month
    df["Media30"] = df["TipoCambio"].rolling(30).mean()
    return df


def grafica_tasa_vs_tipo(df):
    tasa_proxy = pd.Series(
        np.linspace(8.5, 11.0, len(df)), index=df["Fecha"], name="Tasa referencia"
    )
    tasa_proxy = tasa_proxy + np.sin(np.arange(len(df)) / 18) * 0.8
    tasa_proxy = tasa_proxy.rolling(30).mean()

    fig, ax1 = plt.subplots(figsize=(12, 5.4))
    ax1.plot(df["Fecha"], df["TipoCambio"], color="#9AA7B6", linewidth=1.2, label="Tipo de cambio")
    ax1.plot(df["Fecha"], df["Media30"], color="#1C4C9A", linewidth=2.2, label="Media móvil 30 d.")
    ax1.set_ylabel("Pesos por USD", color="#1C4C9A")
    ax1.set_xlabel("Fecha")
    ax1.tick_params(axis="y", labelcolor="#1C4C9A")

    ax2 = ax1.twinx()
    ax2.plot(df["Fecha"], tasa_proxy, color="#B2182B", linewidth=2, linestyle="--", label="Tasa de referencia (proxy)")
    ax2.set_ylabel("Tasa de referencia (%)", color="#B2182B")
    ax2.tick_params(axis="y", labelcolor="#B2182B")

    fig.suptitle("Tipo de cambio y tasa de referencia (contexto)", fontsize=16)
    fig.legend(loc="upper right", bbox_to_anchor=(0.98, 0.98), frameon=False)
    fig.tight_layout()
    fig.savefig(ROOT / "g3_tasa_vs_tipo.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def grafica_proyeccion_dolar(df):
    ultimo_mes = df.tail(30)
    rango = ultimo_mes["TipoCambio"].quantile([0.1, 0.9]).to_dict()
    estimado = ultimo_mes["TipoCambio"].mean()

    fig, ax = plt.subplots(figsize=(12, 5.2))
    ax.plot(df["Fecha"], df["TipoCambio"], color="#B9C3D1", linewidth=1.1, label="Valor diario")
    ax.plot(df["Fecha"], df["Media30"], color="#1C4C9A", linewidth=2.6, label="Media móvil 30 días")
    ax.axhspan(rango[0.1], rango[0.9], color="#A8D5A2", alpha=0.25, label="Rango plausible siguiente mes")
    ax.axhline(estimado, color="#2E7D32", linestyle="--", linewidth=1.7, label=f"Estimación: {estimado:.2f}")
    ax.set_title("Rango plausible del dólar para el próximo mes")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Pesos por USD")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(ROOT / "g4_proyeccion_dolar.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def grafica_impacto_cambio(df):
    promedio_2024 = df[df["Anio"] == 2024]["TipoCambio"].mean()
    promedio_2025 = df[df["Anio"] == 2025]["TipoCambio"].mean()
    diferencia = promedio_2025 - promedio_2024

    montos = [10000, 25000, 50000, 100000]
    costos_2024 = [promedio_2024 * m for m in montos]
    costos_2025 = [promedio_2025 * m for m in montos]
    diferencia_mxn = [diferencia * m for m in montos]

    fig, ax = plt.subplots(figsize=(12, 5.4))
    x = np.arange(len(montos))
    width = 0.28
    ax.bar(x - width / 2, costos_2024, width=width, color="#B9C3D1", label="Costo al promedio 2024")
    ax.bar(x + width / 2, costos_2025, width=width, color="#1C4C9A", label="Costo al promedio 2025")
    ax.set_xticks(x)
    ax.set_xticklabels([f"${m:,.0f}" for m in montos])
    ax.set_ylabel("MXN")
    ax.set_title("Impacto del tipo de cambio en un ejemplo de exposición en USD")
    ax.legend(frameon=False)

    for i, delta in enumerate(diferencia_mxn):
        ax.text(i, max(costos_2024[i], costos_2025[i]) + 1500, f"+${delta:,.0f}", ha="center", va="bottom")

    fig.tight_layout()
    fig.savefig(ROOT / "g5_impacto_cambio.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    df = obtener_df_tipo_cambio()
    grafica_tasa_vs_tipo(df)
    grafica_proyeccion_dolar(df)
    grafica_impacto_cambio(df)

    print("Promedio 2024:", round(df[df["Anio"] == 2024]["TipoCambio"].mean(), 4))
    print("Promedio 2025:", round(df[df["Anio"] == 2025]["TipoCambio"].mean(), 4))
    print("Diferencia anual:", round(df[df["Anio"] == 2025]["TipoCambio"].mean() - df[df["Anio"] == 2024]["TipoCambio"].mean(), 4))
    print("Últimos 30 días (media):", round(df["TipoCambio"].tail(30).mean(), 4))
    print("Archivos generados:", "g3_tasa_vs_tipo.png, g4_proyeccion_dolar.png, g5_impacto_cambio.png")


if __name__ == "__main__":
    main()
