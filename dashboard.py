import streamlit as st
import pandas as pd
import plotly.express as px
import re


with st.expander("ℹ️ README - Dashboard description"):
    st.markdown("""
    ### Dashboard: Space Object Impacts and Encounters

    **Goal:**  
    A comprehensive interactive dashboard analyzing objects that have entered Earth's atmosphere or passed nearby — including meteorites, fireballs/bolides, and near-Earth asteroids (NEOs).  
    The tool provides insight into their physical properties, temporal patterns, spatial distribution, and potential threat level.

    **Data Scope:**
    - **Meteorites**: Landed meteorites categorized by year, location, mass, and classification.
    - **Bolides and Fireballs**: High-energy atmospheric events (bright meteors) analyzed by energy, speed, height, and location.
    - **NEOs (Near-Earth Objects)**: Asteroids and comets with close Earth approaches, analyzed by size, velocity, distance, and hazard level.

    **Data Sources:**
    - [NASA Open Data - Meteorite Landings Dataset](https://data.nasa.gov/dataset/meteorite-landings)
    - [NASA - Fireball and Bolide Reports (Kaggle)](https://www.kaggle.com/datasets/mexwell/nasa-fireball-and-bolide-reports/data)
    - [NASA - Nearest Earth Objects (Kaggle)](https://www.kaggle.com/datasets/sameepvani/nasa-nearest-earth-objects/data)

    **Filters and Interactions:**
    - Year range selection for all datasets
    - Meteorite event type (Fell vs. Found)
    - Hazard filter for NEOs
    - Thematic tab navigation (Meteorites / Bolides / NEOs)
    - Theme switching (light/dark)

    **Technologies Used:**  
    Streamlit, Plotly, Pandas, Python
    """)

tabs = st.tabs(["🌑 Meteorites", "☄️ Bolides and Fireballs", "🌍 Near-Earth Objects"])

with tabs[0]:
    df_meteorites = pd.read_csv("data/meteorite_landings.csv")
    df_meteorites = df_meteorites.dropna(subset=['year', 'mass (g)', 'reclat', 'reclong'])
    df_meteorites['year'] = pd.to_numeric(df_meteorites['year'], errors='coerce')
    df_meteorites = df_meteorites[df_meteorites['year'].notna()]
    df_meteorites = df_meteorites[df_meteorites['year'] <= 2020]
    df_meteorites['Date/Time'] = pd.to_datetime(df_meteorites['year'], format='%Y', errors='coerce')
    df_meteorites = df_meteorites[df_meteorites['mass (g)'] > 0].copy()

    with st.expander("ℹ️ README - Meteorites"):
        total_entries = len(df_meteorites)
        complete_entries = len(df_meteorites.dropna(subset=['Date/Time', 'mass (g)', 'reclat', 'reclong']))
        min_year = int(df_meteorites['Date/Time'].dt.year.min())
        max_year = int(df_meteorites['Date/Time'].dt.year.max())

        st.markdown(
            f"""
            ### Meteorites

            This dashboard presents an interactive analysis and visualization of meteorites that have fallen or been found on Earth. 
            It allows you to explore global meteorite events by time, mass, location, and classification. 
            Filters and visual tools help uncover trends in meteorite activity over the years.
            The data is based on public records and includes both confirmed meteorite falls and finds.

            **Data Source:** NASA's Meteroites Landings

            #### Dataset Overview
            **Base Info:** 
            - **Total entries**: {total_entries:,}
            - **Year range**: {min_year} - {max_year}
            
            **Metrics Included:**  
            - `name`: Name of the meteorite
            - `id`: Unique identifier
            - `nametype`: Type of name (usually 'Valid')
            - `recclass`: Classification of the meteorite
            - `mass (g)`: Mass in grams
            - `fall`: Whether the meteorite was 'Fell' or 'Found'
            - `Date/Time`: Year of the event (datetime)
            - `reclat`, `reclong`: Geographic coordinates
            - `GeoLocation`: String representation of location

            #### Charts Overview
            **Features and Visualizations:**
            - **Meteorites Trend Over Years:** Line chart showing the number of meteorite events per year, categorized by event type (`Fell` or `Found`).
            - **Event Type Ratio:** Pie chart comparing proportions of meteorites that were found vs. those that fell.
            - **Meteorites Class Ratio (Top 10):** Pie chart showing the top 10 most frequent meteorite classes by count.
            - **Meteorites Class Distribution (Top 10):** Bar chart of top 10 meteorite classes by occurrence.
            - **Meteorites Landing Map:** Geospatial scatter plot showing where meteorites landed or were discovered, sized by mass and colored by type.
            - **Meteorites Mass Distribution:** Box plot comparing mass distributions between `Fell` and `Found` meteorites (log scale).
            - **Average Meteorites Mass:** Line plot showing the average mass of meteorites per year.
            - **Top 10 Heaviest Meteorites:** Data table listing the heaviest meteorites by mass with their names, year, and event type.

            #### Filters Overview
            Use the **sidebar filters** to narrow the analysis by year range, event type and meteroit classess.  
            All visualizations update dynamically based on your selection.
            """
        )

    st.sidebar.header("📅 Filters - Meteorites")
    year_range = st.sidebar.slider(
        "Year range (meteorites):",
        int(df_meteorites['Date/Time'].dt.year.min()),
        int(df_meteorites['Date/Time'].dt.year.max()),
        (2000, 2013)
    )

    fall_type = st.sidebar.multiselect("Event type:", df_meteorites['fall'].unique(), default=list(df_meteorites['fall'].unique()))

    classes = st.sidebar.multiselect(
        "Meteorite classes:",
        df_meteorites['recclass'].unique(),
        default=df_meteorites['recclass'].value_counts().nlargest(10).index
    )

    df_meteorites_filtered = df_meteorites[
        df_meteorites['Date/Time'].dt.year.between(*year_range) &
        df_meteorites['fall'].isin(fall_type) &
        df_meteorites['recclass'].isin(classes)
    ].copy()

    st.header("Meteorites Trend Over Years")
    timeline = (
        df_meteorites_filtered
        .groupby([pd.Grouper(key='Date/Time', freq='Y'), 'fall'])
        .size()
        .reset_index(name='count')
    )
    fig_timeline = px.line(
        timeline,
        x="Date/Time",
        y="count",
        color="fall",
        markers=True,
        labels={"Date/Time": "Year", "count": "Number of Meteorites", "fall": "Event Type"}
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.header("Event Type Ratio")
    fall_pie = df_meteorites_filtered['fall'].value_counts().reset_index()
    fall_pie.columns = ['fall', 'count']
    fig_fall_pie = px.pie(
        fall_pie,
        names='fall',
        values='count',
    )
    st.plotly_chart(fig_fall_pie, use_container_width=True)

    st.header("Meteorites Class Ratio (Top 10)")
    class_pie = df_meteorites_filtered['recclass'].value_counts().nlargest(10).reset_index()
    class_pie.columns = ['recclass', 'count']
    fig_class_pie = px.pie(
        class_pie,
        names='recclass',
        values='count',
    )
    st.plotly_chart(fig_class_pie, use_container_width=True)

    st.header("Meteorites Class Distribution (Top 10)")
    top_classes = df_meteorites_filtered['recclass'].value_counts().nlargest(10).index
    df_top = df_meteorites_filtered[df_meteorites_filtered['recclass'].isin(top_classes)].copy()
    df_counts = df_top['recclass'].value_counts().reset_index()
    df_counts.columns = ['recclass', 'count']
    fig_bar = px.bar(
        df_counts,
        x="recclass",
        y="count",
        color="recclass",
        hover_data={"count": False}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.header("Meteorites Landing Map")
    fig_map = px.scatter_geo(
        df_meteorites_filtered,
        lat="reclat",
        lon="reclong",
        color="fall",
        size="mass (g)",
        hover_name="name",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.header("Meteorites Mass Distribution")
    fig_mass = px.histogram(
        df_meteorites_filtered,
        x="mass (g)",
        color="fall",
        nbins=100,
        log_y=True,
        barmode="overlay",
        labels={
            "mass (g)": "Mass (g)",
            "fall": "Event Type"
        }
    )
    st.plotly_chart(fig_mass, use_container_width=True)

    st.header("Average Meteorites Mass")
    avg_mass_by_type = (
        df_meteorites_filtered
        .groupby([pd.Grouper(key='Date/Time', freq='Y'), 'fall'])["mass (g)"]
        .mean()
        .reset_index()
    )
    fig_avg_mass_type = px.bar(
        avg_mass_by_type,
        x="Date/Time",
        y="mass (g)",
        color="fall",
        barmode="group",
        labels={
            "Date/Time": "Year",
            "mass (g)": "Average Mass (g)",
            "fall": "Event Type"
        }
    )
    st.plotly_chart(fig_avg_mass_type, use_container_width=True)

    st.header("Top 10 Heaviest Meteorites")
    top_heavy = df_meteorites_filtered.nlargest(10, 'mass (g)')[['id', 'name', 'mass (g)', 'Date/Time', 'fall']].copy()
    top_heavy['Year'] = top_heavy['Date/Time'].dt.year
    st.dataframe(top_heavy.drop(columns=['Date/Time']))


with tabs[1]:
    df_bolides = pd.read_csv("data/fireball_and_bolide_reports.csv", sep=";")
    df_bolides["Date/Time"] = pd.to_datetime(df_bolides["Date/Time"].astype(str), errors="coerce", utc=True)
    df_bolides["Year"] = df_bolides["Date/Time"].dt.tz_localize(None).dt.year

    with st.expander("ℹ️ README - Bolides and Fireballs"):
        total_entries = len(df_bolides)
        complete_entries = df_bolides.dropna(subset=["Latitude (deg.)", "Longitude (deg.)", "Date/Time"]).shape[0]
        min_year = int(df_bolides["Date/Time"].dt.year.min())
        max_year = int(df_bolides["Date/Time"].dt.year.max())

        st.markdown(
            f"""
            ### Bolides and Fireballs Dashboard

            This dashboard provides an interactive analysis of **bolides** and **fireballs** — extremely bright meteors that often explode in the atmosphere.

            **Data Source:** [NASA's Fireballs and Bolides Report](https://data.nasa.gov/dataset/meteorite-landings)

            #### Dataset Overview
            **Base Info:** 
            - **Total entries:** {total_entries:,}
            - **Year range:** {min_year} - {max_year}

            **Metrics Included:**  
            - `Date/Time`: Timestamp of atmospheric entry
            - `Latitude (deg.)`, `Longitude (deg.)`: Geographic coordinates of the event
            - `Impact energy (kt)`: Kinetic energy released during atmospheric entry (kilotons of TNT)
            - `Radiated Energy (e10 J)`: Energy radiated in 10¹⁰ Joules
            - `Velocity (km/s)`: Entry velocity of the bolide
            - `Altitude (km)`: Estimated altitude of the explosion
            - `Calculated Total Impact Energy (kt)`: Total calculated energy in kilotons

            #### Charts Overview
            **Features and Visualizations:**
            - **Bolides Trend Over Years:** Timeline of events per year, month and weekday.
            - **Monthly Event Distribution:** Heatmap to detect seasonal trends and event clustering.
            - **Bolides Location Map:** Global geospatial scatter map of fireball events with energy scaling.
            - **Bolides Metrics Over Years:** Aggregated impact, radiated energy, and velocity over time (monthly/yearly).
            - **Top 10 Bolides by Various Metrics:** Top 10 events by radiated energy with impact and velocity shown.
            - **Velocity Distribution:** Histogram of fireball entry speeds.
            - **Velocity vs. Impact Energy:** Bubble plot with energy-to-speed correlation.
            - **Cumulative Energy:** Line chart showing cumulative radiated energy growth over time.
            
            #### Filters Overview
            Use the **sidebar filters** to narrow the analysis by year range.  
            All visualizations update dynamically based on your selection.
            """
        )

    st.sidebar.header("📅 Filters - Bolides and Fireballs")
    df_bolides_clean = df_bolides.dropna(subset=["Latitude (deg.)", "Longitude (deg.)"])
    year_range_bolide = st.sidebar.slider("Year range (bolides and fireballs):", int(df_bolides_clean["Year"].min()), int(df_bolides_clean["Year"].max()), (2010, 2020))
    df_bolides_filtered = df_bolides_clean[(df_bolides_clean["Year"] >= year_range_bolide[0]) & (df_bolides_clean["Year"] <= year_range_bolide[1])]

    st.header("Bolides Trend Over Years")
    df_bolides_filtered["Date/Time"] = pd.to_datetime(df_bolides_filtered["Date/Time"], errors="coerce", utc=True)
    df_yearly = df_bolides_filtered.set_index("Date/Time").resample("Y").size().reset_index(name="Count")
    fig_year_datetime = px.line(
        df_yearly,
        x="Date/Time",
        y="Count",
        markers=True,
        labels={"Date/Time": "Year", "Count": "Count"},
        title="Yearly Bolides Distribution"
    )
    st.plotly_chart(fig_year_datetime, use_container_width=True)
    df_bolides_filtered["Month"] = df_bolides_filtered["Date/Time"].dt.month
    df_bolides_filtered["DayOfWeek"] = df_bolides_filtered["Date/Time"].dt.day_name()
    col1, col2 = st.columns(2)
    with col1:
        fig_month = px.histogram(
            df_bolides_filtered, 
            x="Month", nbins=12,
            title="Monthly Bolids Distribution",
            labels={"Month": "Month", "count": "Event Count"}
        )
        st.plotly_chart(fig_month, use_container_width=True)
    with col2:
        fig_day = px.histogram(
            df_bolides_filtered,
            x="DayOfWeek",
            category_orders={"DayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
            title="Day of Week Bolids Distribution",
            labels={"DayOfWeek": "Day of Week", "count": "Event Count"}
        )
        st.plotly_chart(fig_day, use_container_width=True)

    st.header("Monthly Event Distribution")
    df_heat = df_bolides_filtered.copy()
    df_heat["Month"] = df_heat["Date/Time"].dt.month
    df_heat["Year"] = df_heat["Date/Time"].dt.year
    heatmap_data = df_heat.groupby(["Year", "Month"]).size().unstack(fill_value=0)
    fig_heatmap = px.imshow(
        heatmap_data,
        labels=dict(x="Month", y="Year", color="Event Count"),
        x=list(range(1, 13)),
        y=heatmap_data.index,
        color_continuous_scale="Blues",
        aspect="auto"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.header("Bolides Location Map")
    energy_range = st.slider("⚡ Impact energy range (kt):", float(df_bolides_filtered["Impact energy (kt)"].min()), float(df_bolides_filtered["Impact energy (kt)"].max()), step=0.1, value=(float(df_bolides_filtered["Impact energy (kt)"].min()), float(df_bolides_filtered["Impact energy (kt)"].max())))
    df_bolides_filtered_map = df_bolides_filtered[(df_bolides_filtered["Impact energy (kt)"] >= energy_range[0]) & (df_bolides_filtered["Impact energy (kt)"] <= energy_range[1])]
    fig_map_bolides = px.scatter_geo(
        df_bolides_filtered_map,
        lat="Latitude (deg.)",
        lon="Longitude (deg.)",
        color="Impact energy (kt)",
        size="Radiated Energy (e10 J)",
        hover_name="Date/Time",
        color_continuous_scale="OrRd",
        size_max=15
    )
    st.plotly_chart(fig_map_bolides, use_container_width=True)

    st.header("Bolides Metrics Over Years")
    resample_freq = st.radio("Select aggregation frequency:", options=["Yearly", "Monthly"], index=0, horizontal=True)
    selected_metrics = st.multiselect("Select metrics to display:", options=["Impact energy (kt)", "Radiated Energy (e10 J)", "Velocity (km/s)"], default=["Impact energy (kt)", "Radiated Energy (e10 J)", "Velocity (km/s)"])
    df_multi = df_bolides_filtered.dropna(subset=["Date/Time"] + selected_metrics).copy()
    df_multi = df_multi[(df_multi["Date/Time"].dt.year >= year_range_bolide[0]) & (df_multi["Date/Time"].dt.year <= year_range_bolide[1])]
    rule = "M" if resample_freq == "Monthly" else "Y"
    df_multi = df_multi.set_index("Date/Time").resample(rule).sum(numeric_only=True).reset_index()
    df_melted = df_multi.melt(id_vars=["Date/Time"], value_vars=selected_metrics, var_name="Metric", value_name="Value")
    fig_multi_bar = px.bar(
        df_melted, 
        x="Date/Time",
        y="Value",
        color="Metric",
        barmode="group",
        labels={"Date/Time": "Date", "Value": "Value"}
    )
    st.plotly_chart(fig_multi_bar, use_container_width=True)

    st.header("Top 10 Bolides by Various Metrics")
    top_radiated = df_bolides.dropna(subset=["Radiated Energy (e10 J)"]).sort_values("Radiated Energy (e10 J)", ascending=False).head(10)
    st.dataframe(top_radiated[["Date/Time", "Radiated Energy (e10 J)", "Impact energy (kt)", "Velocity (km/s)"]])

    st.header("Velocity Distribution")
    fig_velocity = px.histogram(
        df_bolides_filtered,
        x="Velocity (km/s)",
        nbins=30,
        labels={"Velocity (km/s)": "Velocity (km/s)"}
    )
    st.plotly_chart(fig_velocity, use_container_width=True)

    st.header("Velocity vs. Impact Energy")
    df_scatter = df_bolides_filtered.dropna(subset=["Velocity (km/s)", "Impact energy (kt)"])
    fig_scatter = px.scatter(
        df_scatter,
        x="Velocity (km/s)",
        y="Impact energy (kt)",
        size="Radiated Energy (e10 J)",
        color="Radiated Energy (e10 J)",
        labels={"Velocity (km/s)": "Velocity (km/s)", "Impact energy (kt)": "Impact Energy (kt)"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.header("Cumulative Radiated Energy Over Time")
    df_cumulative = df_bolides_filtered.sort_values("Date/Time").copy()
    df_cumulative["Cumulative Energy"] = df_cumulative["Radiated Energy (e10 J)"].cumsum()
    fig_cumulative = px.line(
        df_cumulative,
        x="Date/Time",
        y="Cumulative Energy",
        labels={"Date/Time": "Year", "Cumulative Energy": "Cumulative Energy"}
    )
    st.plotly_chart(fig_cumulative, use_container_width=True)


with tabs[2]:
    df_neo = pd.read_csv("data/nearest_earth_objects.csv")
    df_neo["mean_diameter"] = (df_neo["est_diameter_min"] + df_neo["est_diameter_max"]) / 2

    def extract_year(name):
        match = re.search(r"\((19|20)\d{2}", name)
        return int(match.group(0)[1:]) if match else None

    df_neo["year"] = df_neo["name"].apply(extract_year)
    df_neo = df_neo.dropna(subset=["year"])
    df_neo["year"] = df_neo["year"].astype(int)

    with st.expander("ℹ️ README - Nearest Earth Objects (NEOs)"):
        st.markdown(f"""
        ### NEO Analysis  
        This section analyzes near-Earth objects (asteroids) based on their physical characteristics, orbital data, and risk level.  
                    
        **Data Source:** [NASA's Nearest Earth Objects (NEOs) Report](https://www.kaggle.com/datasets/sameepvani/nasa-nearest-earth-objects/data)
                    
        #### Dataset Overview
        **Base Info:**  
        - **Total entries:** {len(df_neo):,}  
        - **Entries with complete coordinates:** {df_neo.dropna(subset=['orbiting_body', 'relative_velocity', 'miss_distance']).shape[0]:,}
        - **Year range in dataset:** {df_neo['year'].min()} - {df_neo['year'].max()}

        **Metrics Included:**  
        - `name`: Name of the NEO (usually includes year of discovery)
        - `year`: Parsed year of observation or discovery
        - `est_diameter_min`, `est_diameter_max`: Estimated size range (m)
        - `relative_velocity`: Approach speed (km/s)
        - `miss_distance`: Distance from Earth at closest approach (km)
        - `absolute_magnitude`: Brightness magnitude (H)
        - `hazardous`: Boolean flag indicating if the object is potentially hazardous

        #### Charts Overview
        **Features and Visualizations:**
        - **NEOs Trend Over Years:** Line chart showing yearly discoveries grouped by hazard status
        - **Hazardous Object Ratio:** Pie chart showing proportion of hazardous vs. non-hazardous objects
        - **NEOs Diameters Distribution:** Histogram (log scale) of mean diameters
        - **Velocity vs. Miss Distance:** Density heatmap showing speed vs. closest distance
        - **Brightness vs. Diameter:** Scatterplot highlighting hazardous objects
        - **Cumulative NEOs Discoveries:** Line chart showing total discoveries over time
        - **Velocity Distribution:** Histogram of NEO relative velocities
        - **Miss Distance:** Box plot showing distribution of closest approaches by hazard class
        - **Top 10 Closest Approaches:** Table of nearest NEO encounters with full metrics

        #### Filters Overview
        Use the **sidebar filters** to narrow the analysis by year range and hazardous type.  
        All visualizations update dynamically based on your selection.
        """)

    st.sidebar.header("📅 Filters - NEOs")
    year_range_neo = st.sidebar.slider(
        "Year range (NEO discoveries):",
        min_value=int(df_neo["year"].min()),
        max_value=int(df_neo["year"].max()),
        value=(2010, 2020)
    )
    hazardous_type = st.sidebar.multiselect('Hazardous type:', df_neo['hazardous'].unique(), default=list(df_neo['hazardous'].unique()))
    df_neo_filtered = df_neo[
        (df_neo['year'] >= year_range_neo[0]) & (df_neo['year'] <= year_range_neo[1]) & df_neo['hazardous'].isin(hazardous_type)
    ]

    st.header("NEOs Trend Over Years")
    neo_count_per_year = (
        df_neo_filtered.groupby(["year", "hazardous"]).size().reset_index(name="count")
    )
    fig_neo_per_year = px.line(
        neo_count_per_year,
        x="year",
        y="count",
        color="hazardous",
        markers=True,
        labels={
            "year": "Year",
            "count": "Number of NEOs",
            "hazardous": "Potentially Hazardous"
        }
    )
    st.plotly_chart(fig_neo_per_year, use_container_width=True)

    st.header("Hazardous Object Ratio")
    hazard_counts = df_neo_filtered["hazardous"].value_counts().reset_index()
    hazard_counts.columns = ["hazardous", "count"]
    fig_hazard = px.pie(
        hazard_counts,
        names="hazardous",
        values="count",
    )
    st.plotly_chart(fig_hazard, use_container_width=True)

    st.header("NEOs Diameters Distribution")
    fig_diameter = px.histogram(
        df_neo_filtered,
        x="mean_diameter",
        nbins=50,
        log_y=True,
        labels={"mean_diameter": "Estimated Mean Diameter (m)"}
    )
    st.plotly_chart(fig_diameter, use_container_width=True)

    st.header("Velocity vs. Miss Distance")
    fig_velocity_distance = px.density_heatmap(
        df_neo_filtered,
        x="relative_velocity",
        y="miss_distance",
        nbinsx=50,
        nbinsy=50,
        color_continuous_scale="Viridis",
        labels={
            "relative_velocity": "Relative Velocity (km/s)",
            "miss_distance": "Miss Distance (km)"
        }
    )
    st.plotly_chart(fig_velocity_distance, use_container_width=True)

    st.header("Brightness vs. Diameter")
    fig_brightness = px.scatter(
        df_neo_filtered,
        x="absolute_magnitude",
        y="mean_diameter",
        color="hazardous",
        labels={
            "absolute_magnitude": "Absolute Magnitude (H)",
            "mean_diameter": "Mean Diameter (m)",
            "hazardous": "Potentially Hazardous"
        }
    )
    st.plotly_chart(fig_brightness, use_container_width=True)

    st.header("Cumulative NEOs Discoveries")
    df_cumulative = (
        df_neo_filtered.groupby("year").size().cumsum().reset_index(name="cumulative_count")
    )
    fig_cumulative = px.line(
        df_cumulative,
        x="year",
        y="cumulative_count",
        labels={"year": "Year", "cumulative_count": "Cumulative Count"}
    )
    st.plotly_chart(fig_cumulative, use_container_width=True)

    st.header("Velocity Distribution")
    fig_velocity_hist = px.histogram(
        df_neo_filtered,
        x="relative_velocity",
        nbins=50,
        labels={"relative_velocity": "Relative Velocity (km/s)"}
    )
    st.plotly_chart(fig_velocity_hist, use_container_width=True)

    st.header("Miss Distance")
    fig_miss_box = px.box(
        df_neo_filtered,
        x="hazardous",
        y="miss_distance",
        log_y=True,
        color='hazardous',
        labels={
            "hazardous": "Potentially Hazardous",
            "miss_distance": "Miss Distance (km)"
        }
    )
    st.plotly_chart(fig_miss_box, use_container_width=True)

    st.header("Top 10 Closest Approaches")
    closest_neo = df_neo_filtered.nsmallest(10, "miss_distance")[
        ["name", "miss_distance", "relative_velocity", "absolute_magnitude", "mean_diameter", "hazardous"]
    ]
    closest_neo.columns = ["Name", "Miss Distance (km)", "Velocity (km/s)", "Absolute Magnitude (H)", "Mean Diameter (m)", "Hazardous"]
    st.dataframe(closest_neo)


st.markdown("---")
st.markdown("NASA Datasets | Jan Kubowicz 2025")