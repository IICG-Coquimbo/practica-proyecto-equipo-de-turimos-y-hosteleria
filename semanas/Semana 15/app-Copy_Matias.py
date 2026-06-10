with tab_op:

    st.header("Matriz de Alertas de Calidad")


    umbral_rating = st.slider(
        "Rating mínimo:",
        float(df["rating"].min()),
        float(df["rating"].max()),
        4.0,
        0.1
    )


    umbral_opiniones = st.slider(
        "Opiniones mínimas:",
        0,
        int(df["opiniones"].max()),
        0
    )


    zona_peligro = df[
        (df["rating"] < umbral_rating)
        &
        (df["opiniones"] > umbral_opiniones)
    ]


    st.warning(
        f"Se encontraron {len(zona_peligro)} productos en alerta"
    )


    fig, ax = plt.subplots(figsize=(10,5))


    ax.scatter(
        df["rating"],
        df["opiniones"],
        alpha=0.5
    )


    if len(zona_peligro)>0:

        ax.scatter(
            zona_peligro["rating"],
            zona_peligro["opiniones"],
            s=120
        )


    ax.axvline(
        umbral_rating,
        linestyle="--"
    )


    ax.axhline(
        umbral_opiniones,
        linestyle="--"
    )


    ax.set_xlabel("Rating")
    ax.set_ylabel("Opiniones")


    st.pyplot(fig)



    if len(zona_peligro)>0:

        st.subheader("Lista de productos para revisar")

        st.dataframe(
            zona_peligro[
                [
                "marca",
                "precio_raw",
                "rating",
                "opiniones",
                "prediction"
                ]
            ],
            hide_index=True
        )