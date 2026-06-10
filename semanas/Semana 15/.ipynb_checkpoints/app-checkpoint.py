import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuración de la página web
st.set_page_config(
    page_title="Dashboard Turismo y Hotelería",
    layout="wide"
)

st.title("Cuadro de Mando Integral - Turismo y Hotelería")
st.markdown("---")

# 2. Carga de datos optimizada
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_dashboard.csv")

df = cargar_datos()

# 3. Creación de las Pestañas (Tabs) por Nivel Organizacional
tab_est, tab_tac, tab_op = st.tabs([
    " Nivel Estratégico (CEO)", 
    " Nivel Táctico (Gerente)", 
    " Nivel Operacional (Supervisor)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATÉGICO
# ==========================================
with tab_est:

    st.header("Análisis Estratégico de Ciudades")
    st.caption("Objetivo: Identificar los destinos con mayores precios promedio.")

    df_est = (
        df.groupby("ciudad")["precio_noche"]
        .mean()
        .reset_index()
        .sort_values(by="precio_noche", ascending=False)
    )

    col1, col2 = st.columns([1,2])

    with col1:

        st.metric(
            "Ciudad más cara",
            df_est.iloc[0]["ciudad"]
        )

        st.metric(
            "Precio promedio",
            f"${df_est.iloc[0]['precio_noche']:,.0f}"
        )

        st.dataframe(df_est)

    with col2:

        fig, ax = plt.subplots(figsize=(8,5))

        sns.barplot(
            data=df_est.head(10),
            x="precio_noche",
            y="ciudad",
            ax=ax
        )

        ax.set_xlabel("Precio Promedio por Noche")

        st.pyplot(fig)

# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:

    st.header("Comparación de Precios por Tipo de Alojamiento")
    st.caption("Objetivo: Analizar la competitividad de precios entre tipos de alojamiento.")

    tipos = st.multiselect(
        "Selecciona tipos de alojamiento:",
        options=df["tipo_alojamiento"].dropna().unique(),
        default=df["tipo_alojamiento"].dropna().unique()
    )

    df_filtrado = df[df["tipo_alojamiento"].isin(tipos)]

    df_tac = (
        df_filtrado.groupby("tipo_alojamiento")["precio_noche"]
        .mean()
        .reset_index()
        .sort_values(by="precio_noche", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(10,5))

    sns.barplot(
        data=df_tac,
        x="tipo_alojamiento",
        y="precio_noche",
        ax=ax
    )

    plt.xticks(rotation=30)

    ax.set_xlabel("Tipo de alojamiento")
    ax.set_ylabel("Precio promedio por noche")

    st.pyplot(fig)

# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:

    st.header("Alertas de Calidad")
    st.caption("Objetivo: Detectar alojamientos con puntuación baja.")

    umbral = st.slider(
        "Puntuación mínima aceptable",
        min_value=0.0,
        max_value=10.0,
        value=8.0,
        step=0.1
    )

    df_op = df.copy()

    zona_peligro = df_op[
        df_op["puntuacion"] < umbral
    ]

    st.warning(
        f"Se detectaron {len(zona_peligro)} alojamientos bajo el umbral."
    )

    fig, ax = plt.subplots(figsize=(10,5))

    ax.scatter(
        df_op["estrellas"],
        df_op["puntuacion"],
        alpha=0.5
    )

    ax.scatter(
        zona_peligro["estrellas"],
        zona_peligro["puntuacion"],
        s=100
    )

    ax.axhline(
        y=umbral,
        linestyle="--"
    )

    ax.set_xlabel("Estrellas")
    ax.set_ylabel("Puntuación")

    st.pyplot(fig)

    if len(zona_peligro) > 0:

        st.subheader("Alojamientos con riesgo")

        st.dataframe(
            zona_peligro[
                [
                    "nombre_hotel",
                    "ciudad",
                    "estrellas",
                    "puntuacion",
                    "precio_noche"
                ]
            ]
        )