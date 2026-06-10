import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuracion de la pagina
st.set_page_config(page_title="Dashboard Alojamientos Chile", layout="wide")

st.title("Cuadro de Mando Integral - Alojamientos en Chile")
st.markdown("**Camila Rojas** | Analisis de plataformas de hospedaje")
st.markdown("---")

# Carga de datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_alojamientos_dashboard.csv")

df = cargar_datos()

# Limpiar columnas numericas
df["precio_noche"] = pd.to_numeric(df["precio_noche"], errors="coerce")
df["puntuacion"] = pd.to_numeric(df["puntuacion"], errors="coerce")
df["estrellas"] = pd.to_numeric(df["estrellas"], errors="coerce")
df["noches"] = pd.to_numeric(df["noches"], errors="coerce")

# Tabs
tab_est, tab_tac, tab_op = st.tabs([
    "Nivel Estrategico (Direccion)",
    "Nivel Tactico (Gerente Comercial)",
    "Nivel Operacional (Analista)"
])

# ==========================================
# PESTANA 1: NIVEL ESTRATEGICO
# ==========================================
with tab_est:
    st.header("Participacion de Mercado por Plataforma")
    st.caption("Frecuencia: Mensual | Objetivo: Identificar que plataforma domina el mercado de alojamientos en Chile")

    total = len(df)
    df_est = df["plataforma"].value_counts().reset_index()
    df_est.columns = ["plataforma", "Cantidad_Alojamientos"]
    df_est["Participacion"] = (df_est["Cantidad_Alojamientos"] / total) * 100

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total Alojamientos", total)
        st.metric("Plataforma Lider", df_est["plataforma"].iloc[0],
                  delta=f"{df_est['Participacion'].iloc[0]:.1f}% del mercado")
        st.dataframe(df_est, hide_index=True)

    with col2:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(x="Participacion", y="plataforma", data=df_est,
                    hue="plataforma", palette="Blues_r", legend=False, ax=ax)
        for p in ax.patches:
            ax.annotate(f"{p.get_width():.1f}%",
                        (p.get_width() + 0.3, p.get_y() + p.get_height() / 2),
                        va="center", ha="left", fontsize=10, fontweight="bold")
        ax.set_xlabel("Participacion (%)")
        ax.set_ylabel("Plataforma")
        ax.set_title("Participacion de Mercado por Plataforma")
        sns.despine(left=True)
        st.pyplot(fig)

# ==========================================
# PESTANA 2: NIVEL TACTICO
# ==========================================
with tab_tac:
    st.header("Bandas de Precios por Zona Geografica")
    st.caption("Frecuencia: Semanal | Objetivo: Comparar competitividad de precios entre zonas y plataformas")

    zonas = st.multiselect(
        "Filtrar Zonas Geograficas:",
        options=df["zona_geografica"].dropna().unique(),
        default=df["zona_geografica"].dropna().unique()
    )

    df_filtrado = df[df["zona_geografica"].isin(zonas)]
    df_tac = df_filtrado.groupby("zona_geografica")["precio_noche"].agg(["min", "mean", "max"]).reset_index().dropna()
    df_tac = df_tac.sort_values("mean")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Precio Promedio General",
                  f"${df_filtrado['precio_noche'].mean():,.0f} CLP")
        st.metric("Zona mas cara",
                  df_tac.iloc[-1]["zona_geografica"],
                  delta=f"${df_tac.iloc[-1]['mean']:,.0f} CLP promedio")
        st.metric("Zona mas economica",
                  df_tac.iloc[0]["zona_geografica"],
                  delta=f"${df_tac.iloc[0]['mean']:,.0f} CLP promedio")

    with col2:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.vlines(x=df_tac["zona_geografica"], ymin=df_tac["min"], ymax=df_tac["max"],
                  colors="#B0BEC5", alpha=0.7, linewidth=3)
        ax.scatter(df_tac["zona_geografica"], df_tac["mean"], color="#1A237E", s=120, zorder=3, label="Promedio")
        ax.scatter(df_tac["zona_geografica"], df_tac["min"], color="#2E7D32", marker="^", s=80, zorder=3, label="Minimo")
        ax.scatter(df_tac["zona_geografica"], df_tac["max"], color="#C62828", marker="v", s=80, zorder=3, label="Maximo")
        ax.set_ylabel("Precio por Noche (CLP)")
        ax.set_xlabel("Zona Geografica")
        ax.set_title("Bandas de Precios por Zona Geografica")
        plt.xticks(rotation=30, ha="right")
        ax.legend()
        sns.despine(left=True)
        plt.tight_layout()
        st.pyplot(fig)

# ==========================================
# PESTANA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("Matriz de Alertas: Alojamientos Caros con Baja Puntuacion")
    st.caption("Frecuencia: Diario | Objetivo: Detectar alojamientos que no justifican su precio")

    precio_promedio = df["precio_noche"].mean()

    umbral_puntuacion = st.slider(
        "Umbral critico de puntuacion:",
        min_value=5.0, max_value=9.0, value=7.0, step=0.1
    )
    umbral_precio = st.slider(
        "Umbral de precio alto (CLP):",
        min_value=int(df["precio_noche"].quantile(0.25)),
        max_value=int(df["precio_noche"].quantile(0.90)),
        value=int(precio_promedio),
        step=5000
    )

    df_op = df[["nombre_hotel", "plataforma", "zona_geografica", "precio_noche", "puntuacion"]].dropna()
    zona_peligro = df_op[
        (df_op["puntuacion"] < umbral_puntuacion) &
        (df_op["precio_noche"] > umbral_precio)
    ]

    st.warning(f"Se detectaron {len(zona_peligro)} alojamientos caros con baja puntuacion.")

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(df_op["puntuacion"], df_op["precio_noche"],
                   alpha=0.4, s=60, color="#78909C", label="Alojamientos")
        if not zona_peligro.empty:
            ax.scatter(zona_peligro["puntuacion"], zona_peligro["precio_noche"],
                       color="#D32F2F", s=110, edgecolor="black", zorder=4,
                       label="ALERTA: Caro y mala calidad")
        ax.axvline(x=umbral_puntuacion, color="#C62828", linestyle="--", alpha=0.6, label=f"Umbral puntuacion ({umbral_puntuacion})")
        ax.axhline(y=umbral_precio, color="#C62828", linestyle="--", alpha=0.6, label=f"Umbral precio (${umbral_precio:,})")
        ax.set_xlabel("Puntuacion del Alojamiento")
        ax.set_ylabel("Precio por Noche (CLP)")
        ax.set_title("Alertas: Calidad vs Precio")
        ax.legend(loc="upper left", fontsize=9)
        sns.despine(left=True)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.metric("Total en zona de alerta", len(zona_peligro))
        st.metric("Precio promedio alertas",
                  f"${zona_peligro['precio_noche'].mean():,.0f} CLP" if not zona_peligro.empty else "N/A")
        st.metric("Puntuacion promedio alertas",
                  f"{zona_peligro['puntuacion'].mean():.1f}" if not zona_peligro.empty else "N/A")

    if not zona_peligro.empty:
        st.subheader("Lista de alojamientos para revisar:")
        st.dataframe(
            zona_peligro[["nombre_hotel", "plataforma", "zona_geografica", "precio_noche", "puntuacion"]]
            .sort_values("precio_noche", ascending=False),
            hide_index=True
        )
