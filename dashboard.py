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
    ### Dashboard: Space Object Impacts and Encounters

    **Goal:**  
    A comprehensive interactive dashboard analyzing objects that have entered Earth’s atmosphere or passed nearby — including meteorites, fireballs/bolides, and near-Earth asteroids (NEOs).  
    The tool provides insight into their physical properties, temporal patterns, spatial distribution, and potential threat level.

    **Data Scope:**
    - **Meteorites**: Landed meteorites categorized by year, location, mass, and classification.
    - **Bolides and Fireballs**: High-energy atmospheric events (bright meteors) analyzed by energy, speed, height, and location.
    - **NEOs (Near-Earth Objects)**: Asteroids and comets with close Earth approaches, analyzed by size, velocity, distance, and hazard level.

    **Data Sources:**
    - [NASA Open Data - Meteorite Landings Dataset](https://data.nasa.gov/dataset/meteorite-landings)
    - [NASA - Fireball and Bolide Reports (Kaggle)](https://www.kaggle.com/datasets/mexwell/nasa-fireball-and-bolide-reports/data)
    - [NASA - Nearest Earth Objects (Kaggle)](https://www.kaggle.com/datasets/sameepvani/nasa-nearest-earth-objects/data)

    **Key Indicators:**
    - **Meteorites**:
        - Number and distribution over time
        - Mass (g) and classification (`recclass`)
        - Global landing locations
    - **Bolides and Fireballs**:
        - Yearly frequency of events
        - Explosion energy (kt), entry speed (km/s), and explosion height (km)
        - Geographic location and severity
    - **NEOs**:
        - Discovery trends over time
        - Estimated size (mean diameter)
        - Relative velocity vs. miss distance
        - Potential hazard classification and brightness

    **Filters and Interactions:**
    - Year range selection for all datasets
    - Meteorite event type (Fell vs. Found)
    - Inner Impact Energy filter for bolides
    - Hazard filter for NEOs
    - Thematic tab navigation (Meteorites / Bolides / NEOs)
    - Theme switching (light/dark)

    **Technologies Used:**  
    Streamlit, Plotly, Pandas, Python
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
    year_range = st.sidebar.slider("Year range (meteorites):", int(df['year'].min()), 2025, (2000, 2024))
    fall_type = st.sidebar.multiselect("Event type:", df['fall'].unique(), default=list(df['fall'].unique()))
    df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1]) & (df['fall'].isin(fall_type))]

    st.header("🕓 Meteorites Trend per Year")
    timeline = df_filtered.groupby(["year", "fall"]).size().reset_index(name="count")
    fig_timeline = px.line(
        timeline,
        x="year",
        y="count",
        color="fall",
        markers=True,
        template=plotly_template,
        title="Meteorite Landings per Year by Event Type",
        labels={
            "year": "Year",
            "count": "Number of Meteorites",
            "fall": "Event Type"
        }
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
        df_neo_filtered.groupby(["year", "hazardous"]).size().reset_index(name="count")
    )
    fig_neo_per_year = px.line(
        neo_count_per_year,
        x="year",
        y="count",
        color="hazardous",
        markers=True,
        title="Number of NEOs Discovered per Year",
        template=plotly_template,
        labels={
            "year": "Year",
            "count": "Number of NEOs",
            "hazardous": "Potentially Hazardous"
        }
    )
    st.plotly_chart(fig_neo_per_year, use_container_width=True)

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
    fig_velocity_distance = px.density_heatmap(
        df_neo_filtered,
        x="relative_velocity",
        y="miss_distance",
        nbinsx=50,
        nbinsy=50,
        color_continuous_scale="Viridis",
        title="Velocity vs. Miss Distance of NEOs (Density)",
        template=plotly_template,
        labels={
            "relative_velocity": "Relative Velocity (km/s)",
            "miss_distance": "Miss Distance (km)"
        }
    )
    st.plotly_chart(fig_velocity_distance, use_container_width=True)

    st.header("☄️ Size vs. Absolute Magnitude")
    bins = [10, 15, 20, 25, 30, 35]
    labels = ["10-15", "15-20", "20-25", "25-30", "30-35"]
    df_neo_filtered["magnitude_group"] = pd.cut(df_neo_filtered["absolute_magnitude"], bins=bins, labels=labels)

    fig_size_brightness = px.violin(
        df_neo_filtered,
        x="magnitude_group",
        y="mean_diameter",
        color="hazardous",
        box=True,
        points=False,
        title="NEO Diameter Distribution by Absolute Magnitude Group",
        template=plotly_template,
        labels={
            "magnitude_group": "Absolute Magnitude Group",
            "mean_diameter": "Mean Diameter (m)",
            "hazardous": "Potentially Hazardous"
        }
    )
    st.plotly_chart(fig_size_brightness, use_container_width=True)

st.markdown("---")
st.markdown("NASA Datasets | Jan Kubowicz 2025")
