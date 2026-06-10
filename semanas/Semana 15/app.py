import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# Configuracion de la pagina
st.set_page_config(page_title="Dashboard Alojamientos Chile - Bastian Bravo", layout="wide")

st.title("🏨 Cuadro de Mando Integral - Alojamientos en Chile")
# Se actualiza el autor a Bastian Bravo
st.markdown("**Bastián Bravo** | Análisis de plataformas de hospedaje | Rama: `feature/bastian-bravo`")
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
    "📈 Nivel Estratégico (Dirección)",
    "📊 Nivel Táctico (Gerente Comercial)",
    "🚨 Nivel Operacional (Analista)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATÉGICO
# ==========================================
with tab_est:
    st.header("Participación de Mercado por Plataforma")
    st.caption("Frecuencia: Mensual | Objetivo: Identificar qué plataforma domina el mercado de alojamientos en Chile")

    total = len(df)
    df_est = df["plataforma"].value_counts().reset_index()
    df_est.columns = ["plataforma", "Cantidad_Alojamientos"]
    df_est["Participacion"] = (df_est["Cantidad_Alojamientos"] / total) * 100

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total Alojamientos", f"{total:,}".replace(",", "."))
        st.metric("Plataforma Líder", df_est["plataforma"].iloc[0],
                  delta=f"{df_est['Participacion'].iloc[0]:.1f}% del mercado")
        st.dataframe(df_est, hide_index=True)

    with col2:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        # Se cambia a paleta 'viridis' para diferenciarlo estéticamente
        sns.barplot(x="Participacion", y="plataforma", data=df_est,
                    hue="plataforma", palette="viridis", legend=False, ax=ax)
        for p in ax.patches:
            ax.annotate(f"{p.get_width():.1f}%",
                        (p.get_width() + 0.3, p.get_y() + p.get_height() / 2),
                        va="center", ha="left", fontsize=10, fontweight="bold")
        ax.set_xlabel("Participación (%)")
        ax.set_ylabel("Plataforma")
        ax.set_title("Participación de Mercado por Plataforma - Vista Estratégica")
        sns.despine(left=True)
        st.pyplot(fig)

# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:
    st.header("Bandas de Precios por Zona Geográfica")
    st.caption("Frecuencia: Semanal | Objetivo: Comparar competitividad de precios entre zonas y plataformas")

    zonas = st.multiselect(
        "Filtrar Zonas Geográficas:",
        options=df["zona_geografica"].dropna().unique(),
        default=df["zona_geografica"].dropna().unique()
    )

    df_filtrado = df[df["zona_geografica"].isin(zonas)]
    df_tac = df_filtrado.groupby("zona_geografica")["precio_noche"].agg(["min", "mean", "max"]).reset_index().dropna()
    df_tac = df_tac.sort_values("mean")

    col1, col2 = st.columns([1, 2])
    with col1:
        # MEJORA 1: Formateo explícito de miles con puntos para la moneda chilena en st.metric
        precio_prom_formateado = f"${df_filtrado['precio_noche'].mean():,.0f}".replace(",", ".")
        zona_cara_formateado = f"${df_tac.iloc[-1]['mean']:,.0f}".replace(",", ".")
        zona_eco_formateado = f"${df_tac.iloc[0]['mean']:,.0f}".replace(",", ".")

        st.metric("Precio Promedio General", precio_prom_formateado)
        st.metric("Zona más cara", df_tac.iloc[-1]["zona_geografica"], delta=f"{zona_cara_formateado} promedio")
        st.metric("Zona más económica", df_tac.iloc[0]["zona_geografica"], delta=f"{zona_eco_formateado} promedio")

    with col2:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.vlines(x=df_tac["zona_geografica"], ymin=df_tac["min"], ymax=df_tac["max"],
                  colors="#B0BEC5", alpha=0.7, linewidth=3)
        ax.scatter(df_tac["zona_geografica"], df_tac["mean"], color="#1A237E", s=120, zorder=3, label="Promedio")
        ax.scatter(df_tac["zona_geografica"], df_tac["min"], color="#2E7D32", marker="^", s=80, zorder=3, label="Mínimo")
        ax.scatter(df_tac["zona_geografica"], df_tac["max"], color="#C62828", marker="v", s=80, zorder=3, label="Máximo")
        
        # MEJORA 2: Etiquetas de texto flotantes sobre cada bastón para leer el promedio exacto sin adivinar
        for i, row in df_tac.iterrows():
            ax.text(row["zona_geografica"], row["mean"] + (df_tac["max"].max() * 0.02), 
                     f"${row['mean']:,.0f}".replace(",", "."), 
                     ha="center", va="bottom", fontsize=8, fontweight="bold", color="#1A237E")

        # MEJORA 3: Formatear el eje Y con separadores de miles adecuados para CLP ($100.000)
        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: f"${x:,.0f}".replace(",", ".")))
        
        ax.set_ylabel("Precio por Noche (CLP)")
        ax.set_xlabel("Zona Geográfica")
        ax.set_title("Bandas de Precios por Zona Geográfica - Vista Táctica")
        plt.xticks(rotation=30, ha="right")
        ax.legend()
        sns.despine(left=True)
        plt.tight_layout()
        st.pyplot(fig)

# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("Matriz de Alertas: Alojamientos Caros con Baja Puntuación")
    st.caption("Frecuencia: Diario | Objetivo: Detectar alojamientos que no justifican su precio")

    precio_promedio = df["precio_noche"].mean()

    umbral_puntuacion = st.slider(
        "Umbral crítico de puntuación:",
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

    st.warning(f"Se detectaron {len(zona_peligro)} alojamientos caros con baja puntuación.")

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(df_op["puntuacion"], df_op["precio_noche"],
                   alpha=0.4, s=60, color="#78909C", label="Alojamientos")
        if not zona_peligro.empty:
            ax.scatter(zona_peligro["puntuacion"], zona_peligro["precio_noche"],
                       color="#D32F2F", s=110, edgecolor="black", zorder=4,
                       label="ALERTA: Caro y mala calidad")
        
        ax.axvline(x=umbral_puntuacion, color="#C62828", linestyle="--", alpha=0.6, label=f"Umbral puntuación ({umbral_puntuacion})")
        ax.axhline(y=umbral_precio, color="#C62828", linestyle="--", alpha=0.6, label=f"Umbral precio (${umbral_precio:,})")
        
        # Sombreado analítico suave para destacar visualmente el cuadrante operacional de peligro
        ax.axhspan(ymin=umbral_precio, ymax=df_op["precio_noche"].max() * 1.05, 
                   xmin=0, xmax=(umbral_puntuacion - ax.get_xlim()[0]) / (ax.get_xlim()[1] - ax.get_xlim()[0]), 
                   color="crimson", alpha=0.05, zorder=1)

        # Aplicar formateo de miles con puntos al eje Y de este gráfico
        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: f"${x:,.0f}".replace(",", ".")))

        ax.set_xlabel("Puntuación del Alojamiento")
        ax.set_ylabel("Precio por Noche (CLP)")
        ax.set_title("Alertas de Calidad vs Precio - Vista Operacional")
        ax.legend(loc="upper left", fontsize=9)
        sns.despine(left=True)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        # Formateo de las tarjetas de métricas operacionales de alerta
        alerta_precio_formato = f"${zona_peligro['precio_noche'].mean():,.0f}".replace(",", ".") if not zona_peligro.empty else "N/A"
        alerta_punt_formato = f"{zona_peligro['puntuacion'].mean():.1f}" if not zona_peligro.empty else "N/A"

        st.metric("Total en zona de alerta", len(zona_peligro))
        st.metric("Precio promedio alertas", alerta_precio_formato)
        st.metric("Puntuación promedio alertas", alerta_punt_formato)

    if not zona_peligro.empty:
        st.subheader("Lista de alojamientos para revisar:")
        st.dataframe(
            zona_peligro[["nombre_hotel", "plataforma", "zona_geografica", "precio_noche", "puntuacion"]]
            .sort_values("precio_noche", ascending=False),
            hide_index=True
        )

