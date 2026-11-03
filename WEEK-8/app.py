import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Road Accident Dashboard",
    page_icon="🚗",
    layout="wide",
)

@st.cache_data
def load_data():
    return pd.read_csv(
        "WEEK3_cleaned (3).csv",
        compression="gzip",
        low_memory=False,
    )

df = load_data()

# Prepare date and time fields
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
df["Hour"] = pd.to_datetime(
    df["Time"].astype(str),
    format="%H:%M",
    errors="coerce",
).dt.hour
df["Month"] = df["Date"].dt.to_period("M").astype(str)

st.title("Road Accident Dashboard")
st.caption(
    "Explore accident records by date, severity, road conditions, and location."
)

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.header("Filters")

valid_dates = df["Date"].dropna()

if valid_dates.empty:
    st.error("No dates could be read from the dataset.")
    st.stop()

date_range = st.sidebar.date_input(
    "Date range",
    value=(valid_dates.min().date(), valid_dates.max().date()),
)

view = df.dropna(subset=["Date"]).copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    view = view[view["Date"].between(start_date, end_date)]

# Categorical filters. The dataset stores these fields as numeric codes.
filter_fields = {
    "Accident_Severity": "Severity code",
    "Day_of_Week": "Day-of-week code",
    "Road_Type": "Road type code",
    "Weather_Conditions": "Weather code",
    "Light_Conditions": "Light condition code",
    "Road_Surface_Conditions": "Road surface code",
    "Urban_or_Rural_Area": "Urban/rural code",
    "Local_Authority_(District)": "District code",
}

for column, label in filter_fields.items():
    if column in view.columns:
        options = sorted(view[column].dropna().unique().tolist())
        selected_options = st.sidebar.multiselect(
            label,
            options=options,
            default=options,
            key=f"filter_{column}",
        )

        # Clearing the selection means show no records for this filter.
        if not selected_options:
            view = view.iloc[0:0]
        else:
            view = view[view[column].isin(selected_options)]

# Numeric range filters
numeric_filters = [
    ("Speed_limit", "Speed limit"),
    ("Number_of_Vehicles", "Vehicles per record"),
    ("Number_of_Casualties", "Casualties per record"),
]

for column, label in numeric_filters:
    if column in view.columns and not view.empty:
        values = pd.to_numeric(view[column], errors="coerce").dropna()

        if not values.empty:
            low = int(values.min())
            high = int(values.max())

            if low < high:
                chosen_range = st.sidebar.slider(
                    f"{label} range",
                    min_value=low,
                    max_value=high,
                    value=(low, high),
                    key=f"range_{column}",
                )

                numeric_values = pd.to_numeric(view[column], errors="coerce")
                view = view[numeric_values.between(chosen_range[0], chosen_range[1])]

# Hour of day filter
if "Hour" in view.columns and not view.empty:
    hour_values = view["Hour"].dropna()

    if not hour_values.empty:
        chosen_hours = st.sidebar.slider(
            "Hour of day",
            min_value=0,
            max_value=23,
            value=(0, 23),
        )
        view = view[view["Hour"].between(chosen_hours[0], chosen_hours[1])]

# Stop gracefully if the filters leave no matching records
if view.empty:
    st.warning("No records match these filters. Try widening the date range or selecting more codes.")
    st.stop()

# -------------------------
# Summary metrics
# -------------------------
st.subheader("Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Accident records", f"{len(view):,}")
col2.metric(
    "Casualties recorded",
    f"{pd.to_numeric(view['Number_of_Casualties'], errors='coerce').sum():,.0f}",
)
col3.metric(
    "Average vehicles per record",
    f"{pd.to_numeric(view['Number_of_Vehicles'], errors='coerce').mean():.2f}",
)
col4.metric(
    "Average casualties per record",
    f"{pd.to_numeric(view['Number_of_Casualties'], errors='coerce').mean():.2f}",
)

# -------------------------
# Dashboard tabs
# -------------------------
overview_tab, time_tab, conditions_tab, location_tab, records_tab = st.tabs(
    [
        "Overview",
        "Time patterns",
        "Road and conditions",
        "Locations",
        "Records and data quality",
    ]
)

# -------------------------
# Overview tab
# -------------------------
with overview_tab:
    st.subheader("Severity and accident characteristics")

    severity_counts = (
        view["Accident_Severity"]
        .value_counts()
        .sort_index()
        .rename_axis("Severity code")
        .reset_index(name="Records")
    )

    st.plotly_chart(
        px.pie(
            severity_counts,
            names="Severity code",
            values="Records",
            hole=0.4,
            title="Share of records by severity code",
        ),
        use_container_width=True,
    )

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            px.histogram(
                view,
                x="Number_of_Vehicles",
                title="Vehicles per accident record",
                labels={"Number_of_Vehicles": "Number of vehicles"},
            ),
            use_container_width=True,
        )

    with right:
        st.plotly_chart(
            px.histogram(
                view,
                x="Number_of_Casualties",
                title="Casualties per accident record",
                labels={"Number_of_Casualties": "Number of casualties"},
            ),
            use_container_width=True,
        )

    st.plotly_chart(
        px.scatter(
            view,
            x="Number_of_Vehicles",
            y="Number_of_Casualties",
            color="Accident_Severity",
            title="Vehicles and casualties in each record",
            labels={
                "Number_of_Vehicles": "Number of vehicles",
                "Number_of_Casualties": "Number of casualties",
                "Accident_Severity": "Severity code",
            },
        ),
        use_container_width=True,
    )

# -------------------------
# Time patterns tab
# -------------------------
with time_tab:
    st.subheader("When do accident records occur?")

    monthly_counts = (
        view.groupby("Month")
        .size()
        .reset_index(name="Records")
        .sort_values("Month")
    )

    st.plotly_chart(
        px.line(
            monthly_counts,
            x="Month",
            y="Records",
            markers=True,
            title="Accident records by month",
        ),
        use_container_width=True,
    )

    left, right = st.columns(2)

    with left:
        weekday_counts = (
            view["Day_of_Week"]
            .value_counts()
            .sort_index()
            .rename_axis("Day-of-week code")
            .reset_index(name="Records")
        )

        st.plotly_chart(
            px.bar(
                weekday_counts,
                x="Day-of-week code",
                y="Records",
                title="Records by day-of-week code",
            ),
            use_container_width=True,
        )

    with right:
        hourly_counts = (
            view.dropna(subset=["Hour"])
            .groupby("Hour")
            .size()
            .reset_index(name="Records")
            .sort_values("Hour")
        )

        st.plotly_chart(
            px.bar(
                hourly_counts,
                x="Hour",
                y="Records",
                title="Records by hour",
            ),
            use_container_width=True,
        )

    hour_severity = (
        view.dropna(subset=["Hour"])
        .groupby(["Hour", "Accident_Severity"])
        .size()
        .reset_index(name="Records")
    )

    st.plotly_chart(
        px.line(
            hour_severity,
            x="Hour",
            y="Records",
            color="Accident_Severity",
            markers=True,
            title="Hourly records by severity code",
            labels={"Accident_Severity": "Severity code"},
        ),
        use_container_width=True,
    )

# -------------------------
# Road and conditions tab
# -------------------------
with conditions_tab:
    st.subheader("Road and environmental condition codes")
    st.caption(
        "These values are numeric codes. Confirm their meanings from a data codebook "
        "before replacing the code labels with names."
    )

    condition_fields = {
        "Weather_Conditions": "Weather condition code",
        "Light_Conditions": "Light condition code",
        "Road_Surface_Conditions": "Road surface code",
        "Road_Type": "Road type code",
        "Urban_or_Rural_Area": "Urban/rural code",
    }

    for column, label in condition_fields.items():
        if column in view.columns:
            counts = (
                view[column]
                .value_counts()
                .sort_index()
                .rename_axis(label)
                .reset_index(name="Records")
            )

            st.plotly_chart(
                px.bar(
                    counts,
                    x=label,
                    y="Records",
                    title=f"Records by {label}",
                ),
                use_container_width=True,
            )

    available_conditions = [
        field
        for field in [
            "Weather_Conditions",
            "Light_Conditions",
            "Road_Surface_Conditions",
            "Road_Type",
        ]
        if field in view.columns
    ]

    if available_conditions:
        selected_condition = st.selectbox(
            "Compare a condition code with severity",
            available_conditions,
        )

        condition_severity = (
            view.groupby([selected_condition, "Accident_Severity"])
            .size()
            .reset_index(name="Records")
        )

        st.plotly_chart(
            px.bar(
                condition_severity,
                x=selected_condition,
                y="Records",
                color="Accident_Severity",
                barmode="group",
                title=f"Severity counts by {selected_condition}",
                labels={"Accident_Severity": "Severity code"},
            ),
            use_container_width=True,
        )

    correlation_fields = [
        "Number_of_Vehicles",
        "Number_of_Casualties",
        "Speed_limit",
    ]
    correlation = view[correlation_fields].corr()

    st.plotly_chart(
        px.imshow(
            correlation,
            text_auto=True,
            color_continuous_scale="Blues",
            title="Correlation between vehicles, casualties, and speed limit",
        ),
        use_container_width=True,
    )

# -------------------------
# Locations tab
# -------------------------
with location_tab:
    st.subheader("Recorded accident locations")
    st.caption("Each point represents a record with available coordinates.")

    map_data = view.dropna(subset=["latitude", "longitude"]).copy()
    st.write(f"Records with coordinates: {len(map_data):,}")

    if not map_data.empty:
        st.map(
            map_data.rename(
                columns={"latitude": "lat", "longitude": "lon"}
            )[["lat", "lon"]]
        )
    else:
        st.info("There are no records with coordinates for the selected filters.")

    district_column = "Local_Authority_(District)"

    if district_column in view.columns:
        district_counts = (
            view[district_column]
            .value_counts()
            .head(15)
            .rename_axis("District code")
            .reset_index(name="Records")
        )

        st.plotly_chart(
            px.bar(
                district_counts,
                x="District code",
                y="Records",
                title="Top 15 district codes by record count",
            ),
            use_container_width=True,
        )

# -------------------------
# Records and data quality tab
# -------------------------
with records_tab:
    st.subheader("Filtered accident records")
    st.write(f"Records matching the selected filters: {len(view):,}")

    st.download_button(
        label="Download filtered records as CSV",
        data=view.to_csv(index=False).encode("utf-8"),
        file_name="filtered_accident_records.csv",
        mime="text/csv",
    )

    st.dataframe(
        view,
        use_container_width=True,
        height=450,
    )

    st.subheader("Data quality summary")

    quality = pd.DataFrame({
        "Missing values": df.isna().sum(),
        "Missing percent": (df.isna().mean() * 100).round(2),
    })

    st.dataframe(quality, use_container_width=True)

    st.write("Exact duplicate rows:", int(df.duplicated().sum()))

    if "Accident_Index" in df.columns:
        st.write(
            "Duplicate accident IDs:",
            int(df["Accident_Index"].duplicated().sum()),
        )
