import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard Alojamientos Chile", layout="wide")

st.title("Cuadro de Mando - Inteligencia de Mercado de Alojamientos en Chile")
st.markdown("---")

@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_alojamientos_dashboard.csv")

df = cargar_datos()

tab_est, tab_tac, tab_op = st.tabs([
    "Nivel Estratégico",
    "Nivel Táctico",
    "Nivel Operacional"
])

with tab_est:
    st.header("Concentración del mercado por ciudad")
    st.caption("Frecuencia: Mensual | Objetivo: detectar dónde hay más oferta y dónde hay menos competencia")

    total_aloj = len(df)
    df_est = df['ciudad'].value_counts().reset_index()
    df_est.columns = ['ciudad', 'Cantidad_Alojamientos']
    df_est['Participacion'] = (df_est['Cantidad_Alojamientos'] / total_aloj) * 100

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Total de alojamientos", value=total_aloj)
        st.metric(label="Ciudad con más oferta",
                  value=df_est['ciudad'].iloc[0],
                  delta=f"{df_est['Participacion'].iloc[0]:.1f}% del total")
        st.dataframe(df_est, hide_index=True)

    with col2:
        df_top = df_est.head(15)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(x="Cantidad_Alojamientos", y="ciudad", data=df_top,
                    hue="ciudad", palette="crest", legend=False, ax=ax)
        sns.despine(left=True, bottom=False)
        ax.set_xlabel("Cantidad de alojamientos")
        ax.set_ylabel("")
        st.pyplot(fig)

with tab_tac:
    st.header("Rango y dispersión de precios por tipo de alojamiento")
    st.caption("Frecuencia: Semanal | Objetivo: comparar precios entre tipos y definir estrategia")

    tipos_seleccionados = st.multiselect(
        "Filtrar tipos de alojamiento:",
        options=df['tipo_alojamiento'].unique(),
        default=list(df['tipo_alojamiento'].unique()))

    df_filtrado = df[df['tipo_alojamiento'].isin(tipos_seleccionados)]

    if len(df_filtrado) > 0:
        df_tac = df_filtrado.groupby('tipo_alojamiento')['precio_clp'] \
            .agg(['min', 'mean', 'max']).reset_index().sort_values(by='mean')

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.vlines(x=df_tac['tipo_alojamiento'], ymin=df_tac['min'], ymax=df_tac['max'],
                  colors='#B0BEC5', alpha=0.7, linewidth=3)
        ax.scatter(df_tac['tipo_alojamiento'], df_tac['mean'], color='#1A237E', s=120, zorder=3, label="Promedio")
        ax.scatter(df_tac['tipo_alojamiento'], df_tac['min'], color='#2E7D32', marker='^', s=80, zorder=3, label="Mínimo")
        ax.scatter(df_tac['tipo_alojamiento'], df_tac['max'], color='#C62828', marker='v', s=80, zorder=3, label="Máximo")
        ax.set_ylabel("Precio (CLP)")
        plt.xticks(rotation=25, ha='right')
        ax.legend()
        sns.despine(left=True)
        st.pyplot(fig)
    else:
        st.info("Selecciona al menos un tipo de alojamiento.")

with tab_op:
    st.header("Salud de la reputación")
    st.caption("Frecuencia: Diario | Objetivo: identificar alojamientos con menor calidad percibida")

    umbral_punt = st.slider("Ajustar umbral de puntuación de alerta:",
                            min_value=7.0, max_value=9.0, value=7.5, step=0.1)

    zona_alerta = df[df['puntuacion'] < umbral_punt]

    st.warning(f"Se detectaron {len(zona_alerta)} alojamientos con puntuación bajo {umbral_punt}.")

    rangos = [7.0, 8.0, 8.5, 9.0, 10.01]
    etiquetas = ["Baja (7.0-7.9)", "Media (8.0-8.4)", "Buena (8.5-8.9)", "Excelente (9.0-10)"]
    df_niveles = df.copy()
    df_niveles["rango"] = pd.cut(df_niveles["puntuacion"], bins=rangos, labels=etiquetas, right=False)
    conteo = df_niveles["rango"].value_counts().sort_index()

    cortes = {"Baja (7.0-7.9)": 7.9, "Media (8.0-8.4)": 8.4, "Buena (8.5-8.9)": 8.9, "Excelente (9.0-10)": 10.0}
    colores = []
    for etiqueta in conteo.index:
        if cortes[etiqueta] < umbral_punt:
            colores.append("#D32F2F")
        else:
            colores.append("#43A047")

    fig, ax = plt.subplots(figsize=(10, 5))
    barras = ax.bar(conteo.index.astype(str), conteo.values, color=colores, edgecolor="black", linewidth=0.5)
    for barra in barras:
        altura = barra.get_height()
        ax.text(barra.get_x() + barra.get_width()/2, altura, f"{int(altura)}",
                ha="center", va="bottom", fontsize=11)
    ax.set_xlabel("Nivel de puntuación")
    ax.set_ylabel("Cantidad de alojamientos")
    sns.despine(left=True)
    st.pyplot(fig)

    if len(zona_alerta) > 0:
        st.subheader("Alojamientos con menor puntuación:")
        st.dataframe(
            zona_alerta[['nombre_hotel', 'ciudad', 'tipo_alojamiento', 'precio_clp', 'puntuacion']]
            .sort_values(by='puntuacion').head(20),
            hide_index=True)
