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

tabs = st.tabs(["🌑 Meteorites", "☄️ Bolides and Fireballs", "🌍 Near-Earth Objects"])

with tabs[0]:
    with st.expander("ℹ️ README - Meteorites"):
        st.markdown(
            """
            ### Meteorites
            Analysis and visualization of meteorites that struck Earth — by location, mass, time, and type.
            """
        )

    df = pd.read_csv("data/meteorite_landings.csv")
    df = df.dropna(subset=['year', 'mass (g)', 'reclat', 'reclong'])
    df['year'] = df['year'].astype(int)

    st.sidebar.header("📅 Filters - Meteorites")
    year_range = st.sidebar.slider("Year range (meteorites):", int(df['year'].min()), 2025, (2010, 2024))
    fall_type = st.sidebar.multiselect("Event type:", df['fall'].unique(), default=list(df['fall'].unique()))
    df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1]) & (df['fall'].isin(fall_type))]

    st.header("🕓 Meteorites Trend per Year")
    timeline = df_filtered.groupby("year").size().reset_index(name="count")
    fig_timeline = px.line(
        timeline,
        x="year",
        y="count",
        markers=True,
        template=plotly_template
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.header("🌍 Meteorite Landing Map")
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

    st.header("📊 Meteorite Classes")
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
    with st.expander("ℹ️ README - Bolides and Fireballs"):
        st.markdown(
            """
            ### Bolides and Fireballs
            Analysis and visualization of bolides and fireballs — their locations, impact energy, and temporal trends.
            """
        )

    df_bolides = pd.read_csv("data/fireball_and_bolide_reports.csv", sep=";")
    df_bolides["Date/Time"] = df_bolides["Date/Time"].astype(str)
    df_bolides["Date/Time"] = pd.to_datetime(df_bolides["Date/Time"], errors="coerce", utc=True)
    df_bolides["Year"] = df_bolides["Date/Time"].dt.tz_localize(None).dt.year

    st.sidebar.header("📅 Filters - Bolides and Fireballs")
    df_bolides_clean = df_bolides.dropna(subset=["Latitude (deg.)", "Longitude (deg.)"])
    year_range_bolide = st.sidebar.slider("Year range (bolides and fireballs):", int(df_bolides_clean["Year"].min()), int(df_bolides_clean["Year"].max()), (2010, 2020))
    df_bolides_filtered = df_bolides_clean[(df_bolides_clean["Year"] >= year_range_bolide[0]) & (df_bolides_clean["Year"] <= year_range_bolide[1])]

    st.header("🕓 Bolides Trend per Year")
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

    st.header("🌍 Bolide Location Map")
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

    st.header("💥 Impact Energy")
    fig_hist_bolides = px.histogram(
        df_bolides_filtered,
        x="Impact energy (kt)",
        nbins=50,
        template=plotly_template
    )
    st.plotly_chart(fig_hist_bolides, use_container_width=True)


with tabs[2]:
    with st.expander("ℹ️ README - Nearest Earth Objects (NEO)"):
        st.markdown("""
        ### NEO Analysis  
        This section analyzes near-Earth objects (asteroids) based on their physical characteristics, orbital data, and risk level.  
        The dataset includes estimated size, velocity, miss distance, brightness, and hazard status.
        """)

    df_neo = pd.read_csv("data/nearest_earth_objects.csv")
    df_neo["mean_diameter"] = (df_neo["est_diameter_min"] + df_neo["est_diameter_max"]) / 2

    import re
    def extract_year(name):
        match = re.search(r"\((19|20)\d{2}", name)
        return int(match.group(0)[1:]) if match else None

    df_neo["year"] = df_neo["name"].apply(extract_year)
    df_neo = df_neo.dropna(subset=["year"])
    df_neo["year"] = df_neo["year"].astype(int)

    st.sidebar.header("📅 Filters - NEOs")
    year_range_neo = st.sidebar.slider(
        "Year range (NEO discoveries):",
        min_value=int(df_neo["year"].min()),
        max_value=int(df_neo["year"].max()),
        value=(2010, 2020)
    )
    df_neo_filtered = df_neo[
        (df_neo["year"] >= year_range_neo[0]) & (df_neo["year"] <= year_range_neo[1])
    ]

    st.header("🕓 NEOs Discoveries per Year")
    neo_count_per_year = (
        df_neo_filtered.groupby("year").size().reset_index(name="count")
    )
    fig_neo_per_year = px.line(
        neo_count_per_year,
        x="year",
        y="count",
        title="Number of NEOs Discovered per Year",
        markers=True,
        template=plotly_template,
        labels={
            "year": "Year",
            "count": "Number of NEOs"
        }
    )
    st.plotly_chart(fig_neo_per_year, use_container_width=True)

    st.header("📏 NEO Diameter Distribution")
    fig_diameter = px.histogram(
        df_neo_filtered,
        x="mean_diameter",
        nbins=50,
        title="Distribution of NEO Diameters (meters)",
        template=plotly_template,
        labels={"mean_diameter": "Estimated Mean Diameter (m)"}
    )
    st.plotly_chart(fig_diameter, use_container_width=True)

    st.header("⚡ Velocity vs. Miss Distance")
    fig_velocity_distance = px.scatter(
        df_neo_filtered,
        x="relative_velocity",
        y="miss_distance",
        color="hazardous",
        title="Velocity vs. Miss Distance of NEOs",
        template=plotly_template,
        labels={
            "relative_velocity": "Relative Velocity (km/s)",
            "miss_distance": "Miss Distance (km)",
            "hazardous": "Potentially Hazardous"
        }
    )
    st.plotly_chart(fig_velocity_distance, use_container_width=True)

    st.header("☄️ Size vs. Absolute Magnitude")
    fig_size_brightness = px.violin(
        df_neo_filtered,
        x="hazardous",
        y="mean_diameter",
        color="hazardous",
        box=True,
        points=False,
        title="NEO Diameter Distribution by Hazardous Status",
        template=plotly_template,
        labels={
            "mean_diameter": "Mean Diameter (m)",
            "hazardous": "Potentially Hazardous"
        }
    )
    st.plotly_chart(fig_size_brightness, use_container_width=True)
    st.warning(len(df_neo_filtered))

    st.header("📊 Hazardous Object Ratio")
    hazard_counts = df_neo_filtered["hazardous"].value_counts().reset_index()
    hazard_counts.columns = ["hazardous", "count"]
    fig_hazard = px.pie(
        hazard_counts,
        names="hazardous",
        values="count",
        title="Proportion of Hazardous vs. Non-Hazardous NEOs",
        template=plotly_template
    )
    st.plotly_chart(fig_hazard, use_container_width=True)

st.markdown("---")
st.markdown("NASA Datasets | Jan Kubowicz 2025")
