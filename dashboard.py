import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("data/meteorite_landings.csv")

df = df.dropna(subset=['year', 'mass (g)', 'reclat', 'reclong'])
df['year'] = df['year'].astype(int)

theme = st.sidebar.selectbox("🎨 Choose theme: ", ["Light", "Dark"])
if theme == "Light":
    bg_color = "#ffffff"
    text_color = "#000000"
    card_bg = "#f0f2f6"
    plotly_template = "plotly_white"
else:
    bg_color = "#0e1117"
    text_color = "#fafafa"
    card_bg = "#262730"
    plotly_template = "plotly_dark"

st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg_color}; color: {text_color}; }}
        .block-container {{ background-color: {bg_color}; color: {text_color}; }}
    </style>
""", unsafe_allow_html=True)

with st.expander("ℹ️ README - Dashboard description"):
    st.markdown("""
    ### Dashboard: Report on Meteorites, Bolides, and Fireballs

    **Goal:** A comprehensive analysis of phenomena related to space objects entering Earth's atmosphere — both meteorites that struck Earth, and bright fireballs/bolides.  
    The dashboard allows for exploration of temporal trends, geographic locations, mass, classification, and impact energy.

    **Data Scope:**
    - **Meteorites**: Historical meteorite landings by classification and mass
    - **Bolides and Fireballs**: Extremely bright meteors that exploded in the atmosphere — including their location, energy, speed, and explosion height

    **Data Sources:**
    - [NASA Open Data - Meteorite Landings Dataset](https://data.nasa.gov/dataset/meteorite-landings)
    - [NASA JPL Fireball and Bolide Reports](https://www.kaggle.com/datasets/mexwell/nasa-fireball-and-bolide-reports/data)

    **Key Indicators (Meteorites):**
    - Number of meteorites over time
    - Meteorite mass (in grams)
    - Meteorite classification (recclass)
    - Geographic location of landings

    **Key Indicators (Bolides):**
    - Number of bolides over time
    - Impact energy (kt)
    - Entry speed (km/s)
    - Explosion height (km)
    - Event location and altitude

    **Filters and Interactions:**
    - Year range (for meteorites and bolides)
    - Event type (Fell / Found)
    - Dynamic theme switching (light / dark)
    - Thematic tab switching (meteorites / bolides)

    **Technologies Used:** Streamlit, Plotly, Pandas
    """)

tabs = st.tabs(["🌑 Meteorites", "☄️ Bolides and Fireballs"])

with tabs[0]:
    df = pd.read_csv("data/meteorite_landings.csv")
    df = df.dropna(subset=['year', 'mass (g)', 'reclat', 'reclong'])
    df['year'] = df['year'].astype(int)

    st.sidebar.header("📶 Filters - Meteorites")
    year_range = st.sidebar.slider("Year range (meteorites):", int(df['year'].min()), 2025, (2010, 2024))
    fall_type = st.sidebar.multiselect("Event type:", df['fall'].unique(), default=list(df['fall'].unique()))
    df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1]) & (df['fall'].isin(fall_type))]

    with st.expander("ℹ️ README - Meteorites"):
        st.markdown(
            """
            ### Meteorites
            Analysis and visualization of meteorites that struck Earth — by location, mass, time, and type.
            """
        )

    st.header("🕓 Meteorite trend over time")
    timeline = df_filtered.groupby("year").size().reset_index(name="count")
    fig_timeline = px.line(
        timeline,
        x="year",
        y="count",
        markers=True,
        template=plotly_template
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.header("🌍 Meteorite landing map")
    fig_map = px.scatter_geo(
        df_filtered,
        lat="reclat",
        lon="reclong",
        color="fall",
        size="mass (g)",
        hover_name="name",
        template=plotly_template
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.header("📊 Meteorite classes")
    top_classes = df_filtered['recclass'].value_counts().nlargest(10).index
    df_top = df_filtered[df_filtered['recclass'].isin(top_classes)]

    df_counts = df_top['recclass'].value_counts().reset_index()
    df_counts.columns = ['recclass', 'count']

    fig_bar = px.bar(
        df_counts,
        x="recclass",
        y="count",
        color="recclass",
        template=plotly_template,
        hover_data={"count": False}
    )

    st.plotly_chart(fig_bar, use_container_width=True)

with tabs[1]:
    df_bolides = pd.read_csv("data/fireball_and_bolide_reports.csv", sep=";")
    df_bolides["Date/Time"] = df_bolides["Date/Time"].astype(str)
    df_bolides["Date/Time"] = pd.to_datetime(df_bolides["Date/Time"], errors="coerce", utc=True)
    df_bolides["Year"] = df_bolides["Date/Time"].dt.tz_localize(None).dt.year

    st.sidebar.header("📶 Filters - Bolides and Fireballs")
    df_bolides_clean = df_bolides.dropna(subset=["Latitude (deg.)", "Longitude (deg.)"])
    year_range_bolide = st.sidebar.slider("Year range (bolides and fireballs):", int(df_bolides_clean["Year"].min()), int(df_bolides_clean["Year"].max()), (2010, 2020))
    df_bolides_filtered = df_bolides_clean[(df_bolides_clean["Year"] >= year_range_bolide[0]) & (df_bolides_clean["Year"] <= year_range_bolide[1])]

    with st.expander("ℹ️ README - Bolides and Fireballs"):
        st.markdown(
            """
            ### Bolides and Fireballs
            Analysis and visualization of bolides and fireballs — their locations, impact energy, and temporal trends.
            """
        )

    st.header("🕓 Bolide trend over time")
    df_bolides_by_year = df_bolides_filtered.dropna(subset=["Year"])
    bolides_per_year = df_bolides_by_year.groupby("Year").size().reset_index(name="Count")
    fig_year_line = px.line(
        bolides_per_year,
        x="Year",
        y="Count",
        markers=True,
        title="Number of bolide observations per year",
        template=plotly_template
    )
    st.plotly_chart(fig_year_line, use_container_width=True)

    st.header("🌍 Bolide location map")
    energy_range = st.slider(
        "⚡ Impact energy range (kt):",
        min_value=float(df_bolides_filtered["Impact energy (kt)"].min()),
        max_value=float(df_bolides_filtered["Impact energy (kt)"].max()),
        value=(
            float(df_bolides_filtered["Impact energy (kt)"].min()),
            float(df_bolides_filtered["Impact energy (kt)"].max())
        ),
        step=0.1
    )
    df_bolides_filtered_map = df_bolides_filtered[
        (df_bolides_filtered["Impact energy (kt)"] >= energy_range[0]) &
        (df_bolides_filtered["Impact energy (kt)"] <= energy_range[1])
    ]
    fig_map_bolides = px.scatter_geo(
        df_bolides_filtered_map,
        lat="Latitude (deg.)",
        lon="Longitude (deg.)",
        color="Impact energy (kt)",
        size="Radiated Energy (e10 J)",
        hover_name="Date/Time",
        template=plotly_template,
        color_continuous_scale="OrRd",
        size_max=15
    )
    st.plotly_chart(fig_map_bolides, use_container_width=True)

    st.header("💥 Impact energy")
    fig_hist_bolides = px.histogram(
        df_bolides_filtered,
        x="Impact energy (kt)",
        nbins=50,
        template=plotly_template
    )
    st.plotly_chart(fig_hist_bolides, use_container_width=True)

st.markdown("---")
st.markdown("Meteorites and Bolides | Jan Kubowicz 2025")
