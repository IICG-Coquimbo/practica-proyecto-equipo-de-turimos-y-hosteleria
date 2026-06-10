import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuracion de la pagina
st.set_page_config(
    page_title="Dashboard Turismo - G5",
    page_icon="🏨",
    layout="wide"
)

st.title("📊 Cuadro de Mando Integral - Análisis de Alojamientos en Chile")
st.markdown("**Lucas Cheuque** | Plataforma: Kayak.cl | Grupo G5_Turismo_Hoteleria")
st.markdown("---")

# Carga de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("datos_alojamientos_dashboard.csv")
    return df

try:
    df = cargar_datos()
    st.success(f"✅ Datos cargados: {len(df)} alojamientos")
except:
    st.error("❌ No se encontró el archivo datos_alojamientos_dashboard.csv")
    st.info("Ejecuta primero el notebook de Storytelling EDA (Semana 14)")
    st.stop()

# Limpiar columnas numericas
df["precio_noche"] = pd.to_numeric(df["precio_noche"], errors="coerce")
df["puntuacion"] = pd.to_numeric(df["puntuacion"], errors="coerce")
df["estrellas"] = pd.to_numeric(df["estrellas"], errors="coerce")
df["noches"] = pd.to_numeric(df["noches"], errors="coerce")

# Filtros en sidebar
st.sidebar.header("🔍 Filtros Globales")
ciudades = st.sidebar.multiselect(
    "Ciudades:",
    options=df["ciudad"].dropna().unique(),
    default=df["ciudad"].dropna().unique()[:5] if len(df["ciudad"].dropna().unique()) > 5 else df["ciudad"].dropna().unique()
)

zonas = st.sidebar.multiselect(
    "Zonas Geograficas:",
    options=df["zona_geografica"].dropna().unique(),
    default=df["zona_geografica"].dropna().unique()
)

plataformas = st.sidebar.multiselect(
    "Plataformas:",
    options=df["plataforma"].dropna().unique(),
    default=["Kayak.cl"] if "Kayak.cl" in df["plataforma"].unique() else df["plataforma"].dropna().unique()
)

# Aplicar filtros
df_filtrado = df[
    df["ciudad"].isin(ciudades) &
    df["zona_geografica"].isin(zonas) &
    df["plataforma"].isin(plataformas)
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Mostrando {len(df_filtrado)} de {len(df)} alojamientos")

# Tabs por nivel organizacional
tab_est, tab_tac, tab_op = st.tabs([
    "🏢 Nivel Estratégico (CEO/Director)",
    "📈 Nivel Táctico (Gerente Comercial)",
    "⚠️ Nivel Operacional (Supervisor/Analista)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATEGICO
# ==========================================
with tab_est:
    st.header("Concentración del Mercado por Plataforma")
    st.caption("Frecuencia: Mensual | Objetivo: Identificar qué plataforma domina el mercado de alojamientos en Chile")
    
    total = len(df_filtrado)
    df_est = df_filtrado["plataforma"].value_counts().reset_index()
    df_est.columns = ["plataforma", "cantidad"]
    df_est["participacion"] = (df_est["cantidad"] / total) * 100
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total Alojamientos", f"{total:,}")
        if len(df_est) > 0:
            st.metric("Plataforma Líder", df_est["plataforma"].iloc[0],
                      delta=f"{df_est['participacion'].iloc[0]:.1f}% del mercado")
        st.dataframe(df_est, hide_index=True)
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(x="participacion", y="plataforma", data=df_est,
                    hue="plataforma", palette="Blues_r", legend=False, ax=ax)
        for p in ax.patches:
            ax.annotate(f"{p.get_width():.1f}%",
                        (p.get_width() + 0.5, p.get_y() + p.get_height() / 2),
                        va="center", ha="left", fontsize=10, fontweight="bold")
        ax.set_xlabel("Participación en el Catálogo (%)")
        ax.set_ylabel("Plataforma")
        ax.set_title("Participación de Mercado por Plataforma")
        sns.despine(left=True)
        st.pyplot(fig)

# ==========================================
# PESTAÑA 2: NIVEL TACTICO
# ==========================================
with tab_tac:
    st.header("Bandas de Precios por Zona Geográfica")
    st.caption("Frecuencia: Semanal | Objetivo: Analizar competitividad de precios entre zonas")
    
    df_tac = df_filtrado.groupby("zona_geografica")["precio_noche"].agg(["min", "mean", "max"]).reset_index().dropna()
    df_tac = df_tac.sort_values("mean")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Precio Promedio General",
                  f"${df_filtrado['precio_noche'].mean():,.0f} CLP")
        if len(df_tac) > 0:
            st.metric("Zona más cara", df_tac.iloc[-1]["zona_geografica"],
                      delta=f"${df_tac.iloc[-1]['mean']:,.0f} CLP promedio")
            st.metric("Zona más económica", df_tac.iloc[0]["zona_geografica"],
                      delta=f"${df_tac.iloc[0]['mean']:,.0f} CLP promedio")
    
    with col2:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.vlines(x=df_tac["zona_geografica"], ymin=df_tac["min"], ymax=df_tac["max"],
                  colors="#B0BEC5", alpha=0.7, linewidth=3)
        ax.scatter(df_tac["zona_geografica"], df_tac["mean"], color="#1A237E", s=120, zorder=3, label="Precio Promedio")
        ax.scatter(df_tac["zona_geografica"], df_tac["min"], color="#2E7D32", marker="^", s=80, zorder=3, label="Precio Mínimo")
        ax.scatter(df_tac["zona_geografica"], df_tac["max"], color="#C62828", marker="v", s=80, zorder=3, label="Precio Máximo")
        ax.set_ylabel("Precio por Noche (CLP)")
        ax.set_xlabel("Zona Geográfica")
        ax.set_title("Bandas de Precios por Zona Geográfica")
        plt.xticks(rotation=30, ha="right")
        ax.legend()
        sns.despine(left=True)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Gráfico adicional: Precio por tipo de alojamiento
    st.subheader("Precio Promedio por Tipo de Alojamiento")
    df_tipo = df_filtrado.groupby("tipo_alojamiento")["precio_noche"].mean().reset_index().sort_values("precio_noche", ascending=False)
    
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.barplot(x="tipo_alojamiento", y="precio_noche", data=df_tipo,
                hue="tipo_alojamiento", palette="viridis", legend=False, ax=ax2)
    ax2.set_ylabel("Precio Promedio (CLP)")
    ax2.set_xlabel("Tipo de Alojamiento")
    ax2.set_title("Precio Promedio por Tipo de Alojamiento")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig2)

# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("Matriz de Alertas: Alojamientos Caros con Baja Puntuación")
    st.caption("Frecuencia: Diario | Objetivo: Detectar alojamientos que no justifican su precio")
    
    precio_promedio = df_filtrado["precio_noche"].mean()
    
    col1, col2 = st.columns(2)
    with col1:
        umbral_puntuacion = st.slider(
            "Umbral crítico de puntuación (0-10):",
            min_value=5.0, max_value=9.0, value=7.0, step=0.1
        )
    with col2:
        umbral_precio = st.slider(
            "Umbral de precio alto (CLP):",
            min_value=int(df_filtrado["precio_noche"].quantile(0.25)) if not df_filtrado.empty else 50000,
            max_value=int(df_filtrado["precio_noche"].quantile(0.90)) if not df_filtrado.empty else 200000,
            value=int(precio_promedio) if not np.isnan(precio_promedio) else 100000,
            step=5000
        )
    
    df_op = df_filtrado[["nombre_hotel", "plataforma", "zona_geografica", "precio_noche", "puntuacion", "ciudad"]].dropna()
    zona_peligro = df_op[
        (df_op["puntuacion"] < umbral_puntuacion) &
        (df_op["precio_noche"] > umbral_precio)
    ]
    
    st.warning(f"🚨 Se detectaron **{len(zona_peligro)}** alojamientos en zona de alerta (caros y con baja puntuación)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total en zona de alerta", len(zona_peligro))
    with col2:
        if not zona_peligro.empty:
            st.metric("Precio promedio alertas",
                      f"${zona_peligro['precio_noche'].mean():,.0f} CLP")
        else:
            st.metric("Precio promedio alertas", "N/A")
    with col3:
        if not zona_peligro.empty:
            st.metric("Puntuación promedio alertas",
                      f"{zona_peligro['puntuacion'].mean():.1f}")
        else:
            st.metric("Puntuación promedio alertas", "N/A")
    
    # Gráfico de dispersión
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(df_op["puntuacion"], df_op["precio_noche"],
               alpha=0.4, s=60, color="#78909C", label="Alojamientos")
    if not zona_peligro.empty:
        ax.scatter(zona_peligro["puntuacion"], zona_peligro["precio_noche"],
                   color="#D32F2F", s=110, edgecolor="black", zorder=4,
                   label=f"ALERTAS ({len(zona_peligro)} alojamientos)")
    ax.axvline(x=umbral_puntuacion, color="#C62828", linestyle="--", alpha=0.6,
               label=f"Umbral puntuación ({umbral_puntuacion})")
    ax.axhline(y=umbral_precio, color="#C62828", linestyle="--", alpha=0.6,
               label=f"Umbral precio (${umbral_precio:,} CLP)")
    ax.set_xlabel("Puntuación del Alojamiento (0-10)", fontsize=12)
    ax.set_ylabel("Precio por Noche (CLP)", fontsize=12)
    ax.set_title("Matriz de Alertas: Calidad vs Precio por Noche", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    sns.despine(left=True)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Tabla de alertas
    if not zona_peligro.empty:
        st.subheader("📋 Lista de Alojamientos para Revisión Inmediata:")
        st.dataframe(
            zona_peligro[["nombre_hotel", "ciudad", "zona_geografica", "plataforma", "precio_noche", "puntuacion"]]
            .sort_values("precio_noche", ascending=False),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("✅ No hay alojamientos en zona de alerta con los umbrales seleccionados")

# Footer
st.markdown("---")
st.caption("Dashboard desarrollado por Lucas Cheuque - G5 Turismo y Hotelería")
st.caption("Big Data para la Toma de Decisiones - IICG 2026")