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

nombres_cluster = {0: "Grupo 0 (precio bajo, buena puntuación)",
                   1: "Grupo 1 (precio bajo, puntuación menor)",
                   2: "Grupo 2 (precio alto)"}

st.subheader("Resumen de Indicadores Clave (KPIs)")
total_aloj = len(df)
precio_prom = df["precio_clp"].mean()
punt_prom = df["puntuacion"].mean()
ciudad_lider = df["ciudad"].value_counts().index[0]
tipo_lider = df["tipo_alojamiento"].value_counts().index[0]
pct_oportunidad = (df["prediction"] == 0).mean() * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total de alojamientos", f"{total_aloj}")
k2.metric("Precio promedio", f"${precio_prom:,.0f}")
k3.metric("Puntuación promedio", f"{punt_prom:.2f}")
k4.metric("Grupo 0 (oportunidad)", f"{pct_oportunidad:.1f}%")

tabla_kpi = df.groupby("tipo_alojamiento").agg(
    Cantidad=("precio_clp", "size"),
    Precio_Promedio=("precio_clp", "mean"),
    Puntuacion_Promedio=("puntuacion", "mean")).reset_index()
tabla_kpi["Precio_Promedio"] = tabla_kpi["Precio_Promedio"].round(0)
tabla_kpi["Puntuacion_Promedio"] = tabla_kpi["Puntuacion_Promedio"].round(2)
st.dataframe(tabla_kpi, hide_index=True)

st.markdown("---")

tab_est, tab_tac, tab_op = st.tabs([
    "Nivel Estratégico",
    "Nivel Táctico",
    "Nivel Operacional"
])

with tab_est:
    st.header("Concentración del mercado por ciudad")
    st.caption("Frecuencia: Mensual | Objetivo: detectar dónde hay más oferta y dónde hay menos competencia")

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
        fig, ax = plt.subplots(figsize=(8, 8))
        sns.barplot(x="Cantidad_Alojamientos", y="ciudad", data=df_est,
                    hue="ciudad", palette="crest", legend=False, ax=ax)
        sns.despine(left=True, bottom=False)
        ax.set_xlabel("Cantidad de alojamientos")
        ax.set_ylabel("")
        st.pyplot(fig)

    st.info("Lectura de negocio: el mercado está repartido de forma pareja entre las ciudades; ninguna domina la oferta. La dirección concluye que hay espacio para invertir en distintos destinos, eligiendo por atractivo y rentabilidad, no por falta de competencia.")

    st.subheader("Distribución de tipos de alojamiento en el mercado")
    df_tipos = df['tipo_alojamiento'].value_counts().reset_index()
    df_tipos.columns = ['tipo_alojamiento', 'cantidad']
    df_tipos['pct'] = (df_tipos['cantidad'] / total_aloj * 100).round(1)
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.barplot(x="cantidad", y="tipo_alojamiento", data=df_tipos,
                hue="tipo_alojamiento", palette="mako", legend=False, ax=ax2)
    sns.despine(left=True)
    ax2.set_xlabel("Cantidad de alojamientos")
    ax2.set_ylabel("")
    st.pyplot(fig2)

    tipo1 = df_tipos.iloc[0]
    tipo_menor = df_tipos.iloc[-1]
    st.info(f"Lectura de negocio: el formato más numeroso del mercado es '{tipo1['tipo_alojamiento']}' con "
            f"{tipo1['pct']}% de toda la oferta, mientras que '{tipo_menor['tipo_alojamiento']}' es el menos presente "
            f"con {tipo_menor['pct']}%. Esto le dice a un inversionista dónde está la mayor competencia (el formato "
            f"saturado) y qué formato está menos explotado y podría representar un nicho con menos rivales.")

    st.subheader("Participación de cada segmento (cluster) en el mercado")
    df_clu = df['prediction'].value_counts().sort_index().reset_index()
    df_clu.columns = ['cluster', 'cantidad']
    df_clu['nombre'] = df_clu['cluster'].map(nombres_cluster)
    df_clu['pct'] = (df_clu['cantidad'] / total_aloj * 100).round(1)
    fig5, ax5 = plt.subplots(figsize=(8, 4))
    sns.barplot(x="cantidad", y="nombre", data=df_clu,
                hue="nombre", palette="flare", legend=False, ax=ax5)
    sns.despine(left=True)
    ax5.set_xlabel("Cantidad de alojamientos")
    ax5.set_ylabel("")
    st.pyplot(fig5)

    pct_g0 = df_clu[df_clu['cluster']==0]['pct'].values[0]
    pct_g2 = df_clu[df_clu['cluster']==2]['pct'].values[0]
    st.info(f"Lectura de negocio: el mercado se divide en tres segmentos hallados por el análisis de clustering. "
            f"El Grupo 0 (precio bajo y buena puntuación) es el más grande con {pct_g0}% de los alojamientos, "
            f"mientras que el Grupo 2 (precio alto) es el más pequeño con {pct_g2}%. Para la dirección, el tamaño "
            f"del Grupo 0 muestra que la mayor parte del mercado ofrece buena calidad a precios accesibles: ahí está "
            f"el grueso de la demanda y por lo tanto el segmento más relevante para una estrategia de inversión.")

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

        tipo_caro = df_tac.iloc[-1]
        tipo_barato = df_tac.iloc[0]
        st.info(f"Lectura de negocio: '{tipo_caro['tipo_alojamiento']}' es el tipo más caro (promedio ${tipo_caro['mean']:,.0f}) y '{tipo_barato['tipo_alojamiento']}' el más económico (promedio ${tipo_barato['mean']:,.0f}). La gerencia aprovecha esta dispersión para fijar precios donde haya menos competencia y mejor margen.")

        st.subheader("Precio promedio por ciudad")
        df_ciudad_precio = df_filtrado.groupby('ciudad')['precio_clp'].mean().reset_index().sort_values(by='precio_clp', ascending=False)
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.barplot(x="precio_clp", y="ciudad", data=df_ciudad_precio,
                    hue="ciudad", palette="rocket", legend=False, ax=ax3)
        sns.despine(left=True)
        ax3.set_xlabel("Precio promedio (CLP)")
        ax3.set_ylabel("")
        st.pyplot(fig3)

        c_cara = df_ciudad_precio.iloc[0]
        c_barata = df_ciudad_precio.iloc[-1]
        st.info(f"Lectura de negocio: la ciudad con precio promedio más alto es {c_cara['ciudad']} "
                f"(${c_cara['precio_clp']:,.0f}) y la más económica es {c_barata['ciudad']} "
                f"(${c_barata['precio_clp']:,.0f}). Un inversionista que busca tarifas altas miraría las ciudades "
                f"caras; uno que busca entrar con precios competitivos y captar volumen miraría las más económicas.")

        st.subheader("Precio promedio por segmento (cluster)")
        df_clu_precio = df_filtrado.groupby('prediction')['precio_clp'].mean().reset_index()
        df_clu_precio['nombre'] = df_clu_precio['prediction'].map(nombres_cluster)
        fig6, ax6 = plt.subplots(figsize=(9, 4))
        sns.barplot(x="precio_clp", y="nombre", data=df_clu_precio,
                    hue="nombre", palette="crest", legend=False, ax=ax6)
        sns.despine(left=True)
        ax6.set_xlabel("Precio promedio (CLP)")
        ax6.set_ylabel("")
        st.pyplot(fig6)

        st.info("Lectura de negocio: este gráfico confirma la diferencia de precio entre los tres segmentos. "
                "El Grupo 2 cobra bastante más que los Grupos 0 y 1. Como el Grupo 0 mantiene buena puntuación "
                "cobrando poco, el gerente puede definir una estrategia de precios competitivos sin sacrificar calidad.")
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

    st.info(f"Lectura de negocio: la calidad general es alta (puntuación promedio {punt_prom:.2f}; la mayoría en niveles Bueno y Excelente). La supervisión enfoca su atención en los alojamientos bajo el umbral de alerta para corregir su menor desempeño.")

    st.subheader("Distribución de puntuaciones por tipo de alojamiento")
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    sns.boxplot(x="tipo_alojamiento", y="puntuacion", data=df,
                hue="tipo_alojamiento", palette="Set2", legend=False, ax=ax4)
    sns.despine(left=True)
    ax4.set_xlabel("Tipo de alojamiento")
    ax4.set_ylabel("Puntuación")
    plt.xticks(rotation=25, ha='right')
    st.pyplot(fig4)

    st.info("Lectura de negocio: cada caja muestra cómo se reparten las puntuaciones dentro de un tipo. "
            "La línea del medio es la puntuación típica y el alto de la caja indica cuánta variación hay. "
            "Un tipo con caja alta y compacta es una apuesta más segura en calidad; uno con caja larga tiene "
            "experiencias muy dispares, lo que implica más riesgo para el inversionista que entre ahí.")

    st.subheader("Cantidad de alertas por ciudad")
    if len(zona_alerta) > 0:
        alertas_ciudad = zona_alerta['ciudad'].value_counts().reset_index()
        alertas_ciudad.columns = ['ciudad', 'alertas']
        fig7, ax7 = plt.subplots(figsize=(10, 6))
        sns.barplot(x="alertas", y="ciudad", data=alertas_ciudad,
                    hue="ciudad", palette="rocket_r", legend=False, ax=ax7)
        sns.despine(left=True)
        ax7.set_xlabel("Cantidad de alojamientos en alerta")
        ax7.set_ylabel("")
        st.pyplot(fig7)

        ciudad_mas_alertas = alertas_ciudad.iloc[0]
        st.info(f"Lectura de negocio: la ciudad con más alojamientos bajo el umbral es "
                f"{ciudad_mas_alertas['ciudad']} ({ciudad_mas_alertas['alertas']} en alerta). Esto le dice al "
                f"supervisor en qué ciudad concentrar la revisión de calidad. Para un inversionista, una ciudad con "
                f"muchas alertas puede significar competencia débil en calidad: una oportunidad para entrar con un "
                f"alojamiento bien evaluado y destacar.")

    if len(zona_alerta) > 0:
        st.subheader("Alojamientos con menor puntuación:")
        st.dataframe(
            zona_alerta[['nombre_hotel', 'ciudad', 'tipo_alojamiento', 'precio_clp', 'puntuacion']]
            .sort_values(by='puntuacion').head(20),
            hide_index=True)
