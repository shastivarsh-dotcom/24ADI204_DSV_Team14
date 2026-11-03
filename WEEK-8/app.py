import streamlit as st
import pandas as pd
import plotly.express as px

DATA_FILE = "WEEK3_cleaned (3).csv"
DISTRICT_COL = "Local_Authority_(District)"

# These labels follow the DfT STATS19 coding guide for this dataset's code scheme.
SEVERITY_CODES = {1: "Fatal", 2: "Serious", 3: "Slight"}
WEEKDAY_CODES = {
    1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday",
    5: "Thursday", 6: "Friday", 7: "Saturday",
}
ROAD_TYPE_CODES = {
    1: "Roundabout", 2: "One-way street", 3: "Dual carriageway",
    6: "Single carriageway", 7: "Slip road", 9: "Unknown road type",
}
WEATHER_CODES = {
    1: "Fine, no high winds", 2: "Rain, no high winds",
    3: "Snow, no high winds", 4: "Fine, high winds",
    5: "Rain, high winds", 6: "Snow, high winds",
    7: "Fog or mist", 8: "Other weather", 9: "Unknown weather",
}
LIGHT_CODES = {
    1: "Daylight, street lights present", 2: "Daylight, no street lighting",
    3: "Daylight, street lighting unknown", 4: "Dark, street lights lit",
    5: "Dark, street lights unlit", 6: "Dark, no street lighting",
    7: "Dark, street lighting unknown",
}
SURFACE_CODES = {
    1: "Dry", 2: "Wet or damp", 3: "Snow", 4: "Frost or ice",
    5: "Flood water", -1: "Missing or out of range",
}
URBAN_RURAL_CODES = {
    1: "Urban", 2: "Rural", 3: "Unallocated",
    -1: "Missing or out of range",
}
JUNCTION_DETAIL_CODES = {
    -1: "Missing or out of range", 0: "Not near a junction",
    1: "Roundabout", 2: "Mini-roundabout", 3: "T or staggered junction",
    5: "Slip road", 6: "Crossroads", 7: "Multiple junction",
    8: "Private drive or entrance", 9: "Other junction",
}
JUNCTION_CONTROL_CODES = {
    -1: "Missing or out of range", 0: "Not near a junction",
    1: "Authorised person", 2: "Traffic signal", 3: "Stop sign",
    4: "Give way or uncontrolled",
}
ROAD_CLASS_CODES = {
    -1: "Missing or out of range", 1: "Motorway", 2: "A(M) road",
    3: "A road", 4: "B road", 5: "C road", 6: "Unclassified road",
}
POLICE_FORCE_CODES = {
    1: "Metropolitan Police", 3: "Cumbria", 4: "Lancashire",
    5: "Merseyside", 6: "Greater Manchester", 7: "Cheshire",
    10: "Northumbria", 11: "Durham", 12: "North Yorkshire",
    48: "City of London Police",
}
PEDESTRIAN_CONTROL_CODES = {
    -1: "Missing or out of range", 0: "No control within 50 metres",
    1: "School crossing patrol", 2: "Other authorised person",
}
PEDESTRIAN_FACILITY_CODES = {
    -1: "Missing or out of range", 0: "No physical crossing within 50 metres",
    1: "Zebra crossing", 4: "Pelican, puffin or toucan crossing",
    5: "Pedestrian phase at signal junction", 7: "Footbridge or subway",
    8: "Central refuge",
}
SPECIAL_SITE_CODES = {
    -1: "Missing or out of range", 0: "None",
    1: "Traffic signal out", 2: "Traffic signal partly defective",
    3: "Road sign or marking defective", 4: "Roadworks",
    5: "Road surface defective", 6: "Oil or diesel", 7: "Mud",
}
CARRIAGEWAY_HAZARD_CODES = {
    -1: "Missing or out of range", 0: "None",
    1: "Dislodged vehicle load", 2: "Other object in carriageway",
    3: "Previous accident involvement", 6: "Pedestrian in carriageway",
    7: "Animal in carriageway",
}
POLICE_ATTENDANCE_CODES = {
    -1: "Missing or out of range", 1: "Yes", 2: "No", 3: "Not recorded",
}

# Historical DfT local-authority district codes used by the supplied file.
DISTRICT_CODES = {
    1: "Westminster", 2: "Camden", 3: "Islington", 4: "Hackney",
    5: "Tower Hamlets", 6: "Greenwich", 7: "Lewisham", 8: "Southwark",
    9: "Lambeth", 10: "Wandsworth", 11: "Hammersmith and Fulham",
    12: "Kensington and Chelsea", 13: "Waltham Forest", 14: "Redbridge",
    15: "Havering", 16: "Barking and Dagenham", 17: "Newham", 18: "Bexley",
    19: "Bromley", 20: "Croydon", 21: "Sutton", 22: "Merton",
    23: "Kingston upon Thames", 24: "Richmond upon Thames", 25: "Hounslow",
    26: "Hillingdon", 27: "Ealing", 28: "Brent", 29: "Harrow",
    30: "Barnet", 31: "Haringey", 32: "Enfield", 57: "London Airport",
    60: "Allerdale", 61: "Barrow-in-Furness", 62: "Carlisle",
    63: "Copeland", 64: "Eden", 65: "South Lakeland",
    70: "Blackburn with Darwen", 71: "Blackpool", 72: "Burnley",
    73: "Chorley", 74: "Fylde", 75: "Hyndburn", 76: "Lancaster",
    77: "Pendle", 79: "Preston", 80: "Ribble Valley", 82: "Rossendale",
    83: "South Ribble", 84: "West Lancashire", 90: "Knowsley",
    91: "Liverpool", 92: "St Helens", 93: "Sefton", 95: "Wirral",
    100: "Bolton", 101: "Bury", 102: "Manchester", 104: "Oldham",
    106: "Rochdale", 107: "Salford", 109: "Stockport", 110: "Tameside",
    112: "Trafford", 114: "Wigan", 120: "Chester", 121: "Congleton",
    122: "Crewe and Nantwich", 123: "Ellesmere Port and Neston",
    124: "Halton", 126: "Macclesfield", 127: "Vale Royal", 128: "Warrington",
    140: "Alnwick", 141: "Berwick-upon-Tweed", 142: "Blyth Valley",
    143: "Castle Morpeth", 144: "Tynedale", 145: "Wansbeck",
    146: "Gateshead", 147: "Newcastle upon Tyne", 148: "North Tyneside",
    149: "South Tyneside", 150: "Sunderland", 160: "Chester-le-Street",
    161: "Darlington", 162: "Derwentside", 163: "Durham",
    164: "Easington", 165: "Sedgefield", 166: "Teesdale",
    168: "Wear Valley", 180: "Craven", 181: "Hambleton",
    182: "Harrogate", 184: "Richmondshire", 185: "Ryedale",
    186: "Scarborough", 187: "Selby", 189: "York", 570: "City of London",
}

CODE_FIELDS = {
    "Accident_Severity": ("Severity", SEVERITY_CODES),
    "Day_of_Week": ("Day of week", WEEKDAY_CODES),
    "Road_Type": ("Road type", ROAD_TYPE_CODES),
    "Weather_Conditions": ("Weather", WEATHER_CODES),
    "Light_Conditions": ("Lighting", LIGHT_CODES),
    "Road_Surface_Conditions": ("Road surface", SURFACE_CODES),
    "Urban_or_Rural_Area": ("Area type", URBAN_RURAL_CODES),
    "Junction_Detail": ("Junction type", JUNCTION_DETAIL_CODES),
    "Junction_Control": ("Junction control", JUNCTION_CONTROL_CODES),
    "1st_Road_Class": ("First road class", ROAD_CLASS_CODES),
    "2nd_Road_Class": ("Second road class", ROAD_CLASS_CODES),
    "Police_Force": ("Police force", POLICE_FORCE_CODES),
    DISTRICT_COL: ("District", DISTRICT_CODES),
    "Pedestrian_Crossing-Human_Control": (
        "Pedestrian crossing control", PEDESTRIAN_CONTROL_CODES
    ),
    "Pedestrian_Crossing-Physical_Facilities": (
        "Pedestrian crossing facility", PEDESTRIAN_FACILITY_CODES
    ),
    "Special_Conditions_at_Site": ("Special site condition", SPECIAL_SITE_CODES),
    "Carriageway_Hazards": ("Carriageway hazard", CARRIAGEWAY_HAZARD_CODES),
    "Did_Police_Officer_Attend_Scene_of_Accident": (
        "Police attended", POLICE_ATTENDANCE_CODES
    ),
}

st.set_page_config(
    page_title="Road Accident Explorer",
    page_icon="🚦",
    layout="wide",
)


def decode_value(value, mapping):
    if pd.isna(value):
        return "Not recorded"
    try:
        code = int(float(value))
    except (TypeError, ValueError):
        return str(value)
    if code in mapping:
        if mapping is DISTRICT_CODES:
            return f"{mapping[code]} (district code {code})"
        return mapping[code]
    return f"Unmapped code {code}"


@st.cache_data
def load_data(path):
    data = pd.read_csv(path, compression="gzip", low_memory=False)
    data["Date"] = pd.to_datetime(data["Date"], dayfirst=True, errors="coerce")
    data["Hour"] = pd.to_datetime(
        data["Time"].astype(str), format="%H:%M", errors="coerce"
    ).dt.hour
    data["Month"] = data["Date"].dt.to_period("M").astype(str)

    for source, (label_column, mapping) in CODE_FIELDS.items():
        if source in data.columns:
            data[label_column] = data[source].map(
                lambda value: decode_value(value, mapping)
            )
    data["Hour label"] = data["Hour"].map(
        lambda value: f"{int(value):02d}:00" if pd.notna(value) else "Time not recorded"
    )
    return data


def counts_by_label(data, label_column):
    return (
        data[label_column]
        .fillna("Not recorded")
        .value_counts()
        .rename_axis(label_column)
        .reset_index(name="Accident records")
    )


def show_overview(data):
    st.title("Road Accident Dashboard")
    st.write(
        "Use the pages above to explore accident records by time, location, "
        "road conditions, and recorded impact."
    )

    total_casualties = pd.to_numeric(
        data["Number_of_Casualties"], errors="coerce"
    ).sum()
    avg_vehicles = pd.to_numeric(
        data["Number_of_Vehicles"], errors="coerce"
    ).mean()
    avg_casualties = pd.to_numeric(
        data["Number_of_Casualties"], errors="coerce"
    ).mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accident records", f"{len(data):,}")
    c2.metric("Casualties recorded", f"{total_casualties:,.0f}")
    c3.metric("Average vehicles per record", f"{avg_vehicles:.2f}")
    c4.metric("Average casualties per record", f"{avg_casualties:.2f}")

    left, right = st.columns(2)
    with left:
        monthly = data.groupby("Month").size().reset_index(name="Accident records")
        st.plotly_chart(
            px.line(
                monthly, x="Month", y="Accident records", markers=True,
                title="Accident records over time",
            ), use_container_width=True,
        )
    with right:
        severity = counts_by_label(data, "Severity")
        st.plotly_chart(
            px.bar(
                severity, x="Severity", y="Accident records",
                title="Records by severity",
            ), use_container_width=True,
        )

    st.subheader("Questions to explore")
    st.markdown(
        "- **When** are records most common?\n"
        "- **Where** are the recorded locations and districts?\n"
        "- **Which conditions** appear in the selected records?\n"
        "- **How many vehicles and casualties** are recorded per accident?"
    )


def show_time(data):
    st.title("When do accident records occur?")
    days = sorted(data["Day of week"].dropna().unique().tolist())
    selected_days = st.multiselect("Days of week", days, default=days)
    time_data = data[data["Day of week"].isin(selected_days)].copy()

    hours = time_data["Hour"].dropna()
    if not hours.empty:
        hour_range = st.slider("Hour of day", 0, 23, (0, 23))
        time_data = time_data[time_data["Hour"].between(*hour_range)]
    if time_data.empty:
        st.warning("No records match these time selections.")
        return

    monthly = time_data.groupby("Month").size().reset_index(name="Accident records")
    st.plotly_chart(
        px.line(
            monthly, x="Month", y="Accident records", markers=True,
            title="Monthly accident-record trend",
        ), use_container_width=True,
    )

    left, right = st.columns(2)
    with left:
        day_counts = counts_by_label(time_data, "Day of week")
        st.plotly_chart(
            px.bar(day_counts, x="Day of week", y="Accident records",
                   title="Records by day of week"),
            use_container_width=True,
        )
    with right:
        hour_counts = (
            time_data.dropna(subset=["Hour"])
            .groupby("Hour").size().reset_index(name="Accident records")
        )
        st.plotly_chart(
            px.bar(hour_counts, x="Hour", y="Accident records",
                   title="Records by hour of day"),
            use_container_width=True,
        )

    heat = (
        time_data.dropna(subset=["Hour", "Day of week"])
        .groupby(["Day of week", "Hour"]).size()
        .reset_index(name="Accident records")
    )
    st.plotly_chart(
        px.density_heatmap(
            heat, x="Hour", y="Day of week", z="Accident records",
            histfunc="sum", title="Records by weekday and hour",
        ), use_container_width=True,
    )


def show_location(data):
    st.title("Where are accident records located?")
    st.warning(
        "District numbers are translated using the DfT local-authority code list. "
        "The supplied coordinates fall in India while the district and highway "
        "codes match Great Britain, so confirm the file's location data before "
        "using this map as a geographic finding."
    )

    map_data = data.dropna(subset=["latitude", "longitude"])
    st.metric("Records with coordinates", f"{len(map_data):,}")
    if not map_data.empty:
        st.subheader("Coordinates as supplied (geography needs checking)")
        st.map(
            map_data.rename(columns={"latitude": "lat", "longitude": "lon"})[
                ["lat", "lon"]
            ]
        )

    if "District" in data.columns:
        district_counts = counts_by_label(data, "District")
        district_counts = district_counts.nlargest(15, "Accident records")
        district_counts = district_counts.sort_values("Accident records")
        st.plotly_chart(
            px.bar(
                district_counts, x="Accident records", y="District",
                orientation="h", title="Districts with the most records",
            ), use_container_width=True,
        )


def show_conditions(data):
    st.title("Road and environmental conditions")
    fields = {
        "Road type": "Road type",
        "Weather": "Weather",
        "Lighting": "Lighting",
        "Road surface": "Road surface",
        "Area type": "Urban or rural area",
        "Junction type": "Junction type",
        "Junction control": "Junction control",
    }
    available = {label: column for column, label in fields.items()
                 if label in data.columns}
    selected_label = st.selectbox("Choose a condition", list(available))
    selected_column = available[selected_label]

    condition_counts = counts_by_label(data, selected_column)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            px.bar(
                condition_counts, x=selected_column, y="Accident records",
                title=f"Records by {selected_label.lower()}",
            ), use_container_width=True,
        )
    with right:
        comparison = data[[selected_column, "Severity"]].dropna().copy()
        shares = (
            pd.crosstab(
                comparison[selected_column], comparison["Severity"],
                normalize="index",
            )
            .reset_index()
            .melt(
                id_vars=selected_column, var_name="Severity",
                value_name="Share of records",
            )
        )
        st.plotly_chart(
            px.bar(
                shares, x=selected_column, y="Share of records",
                color="Severity", barmode="stack",
                title=f"Severity mix by {selected_label.lower()}",
            ), use_container_width=True,
        )

    st.caption(
        "The stacked chart compares the severity mix among recorded accidents. "
        "It does not show risk per trip or prove that a condition caused an accident."
    )


def show_impact(data):
    st.title("Vehicles and casualties")

    vehicle_values = pd.to_numeric(
        data["Number_of_Vehicles"], errors="coerce"
    ).dropna()
    casualty_values = pd.to_numeric(
        data["Number_of_Casualties"], errors="coerce"
    ).dropna()
    if vehicle_values.empty or casualty_values.empty:
        st.warning("Vehicle or casualty counts are unavailable for these filters.")
        return

    a, b = st.columns(2)
    vehicle_range = a.slider(
        "Vehicles in an accident", int(vehicle_values.min()),
        int(vehicle_values.max()),
        (int(vehicle_values.min()), int(vehicle_values.max())),
    )
    casualty_range = b.slider(
        "Casualties in an accident", int(casualty_values.min()),
        int(casualty_values.max()),
        (int(casualty_values.min()), int(casualty_values.max())),
    )

    impact = data.copy()
    impact["Number_of_Vehicles"] = pd.to_numeric(
        impact["Number_of_Vehicles"], errors="coerce"
    )
    impact["Number_of_Casualties"] = pd.to_numeric(
        impact["Number_of_Casualties"], errors="coerce"
    )
    impact = impact[
        impact["Number_of_Vehicles"].between(*vehicle_range)
        & impact["Number_of_Casualties"].between(*casualty_range)
    ].copy()
    if impact.empty:
        st.warning("No records match these vehicle and casualty ranges.")
        return

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            px.box(
                impact, x="Severity", y="Number_of_Casualties",
                points="outliers", title="Casualties per accident by severity",
            ), use_container_width=True,
        )
    with right:
        st.plotly_chart(
            px.scatter(
                impact, x="Number_of_Vehicles", y="Number_of_Casualties",
                color="Severity", title="Vehicles and casualties per accident",
            ), use_container_width=True,
        )


def show_data(data, full_data):
    st.title("Records and data quality")
    st.write(f"Records matching the current filters: {len(data):,}")

    quality = pd.DataFrame({
        "Missing values": full_data.isna().sum(),
        "Missing percent": (full_data.isna().mean() * 100).round(2),
    }).sort_values("Missing values", ascending=False)
    st.subheader("Data quality for the full file")
    st.dataframe(quality, use_container_width=True)
    st.write("Exact duplicate rows:", int(full_data.duplicated().sum()))
    if "Accident_Index" in full_data.columns:
        st.write(
            "Duplicate accident IDs:",
            int(full_data["Accident_Index"].duplicated().sum()),
        )

    st.subheader("Filtered records with readable category labels")
    display = data.copy()
    for source, (label_column, _) in CODE_FIELDS.items():
        if source in display.columns and label_column in display.columns:
            display[source] = display[label_column]
            display = display.drop(columns=[label_column])
    display = display.rename(columns={
        "Accident_Severity": "Severity",
        "Day_of_Week": "Day of week",
        "Road_Type": "Road type",
        "Weather_Conditions": "Weather",
        "Light_Conditions": "Lighting",
        "Road_Surface_Conditions": "Road surface",
        "Urban_or_Rural_Area": "Area type",
        "Local_Authority_(District)": "District",
        "Police_Force": "Police force",
        "Junction_Detail": "Junction type",
        "Junction_Control": "Junction control",
        "1st_Road_Class": "First road class",
        "2nd_Road_Class": "Second road class",
        "Pedestrian_Crossing-Human_Control": "Pedestrian crossing control",
        "Pedestrian_Crossing-Physical_Facilities": "Pedestrian crossing facility",
        "Special_Conditions_at_Site": "Special site condition",
        "Carriageway_Hazards": "Carriageway hazard",
        "Did_Police_Officer_Attend_Scene_of_Accident": "Police attended",
    })
    display = display.drop(columns=["Hour label"], errors="ignore")

    st.download_button(
        "Download filtered records with readable labels",
        data=display.to_csv(index=False).encode("utf-8"),
        file_name="filtered_accident_records_readable.csv",
        mime="text/csv",
    )
    st.dataframe(display, use_container_width=True, height=450)


try:
    df = load_data(DATA_FILE)
except FileNotFoundError:
    st.error(
        f"Could not find {DATA_FILE}. Put app.py and the CSV file in the same "
        "folder, then run Streamlit from that folder."
    )
    st.stop()
except Exception as error:
    st.error(f"Could not read the dataset: {error}")
    st.stop()

required_columns = {
    "Date", "Time", "Accident_Severity", "Number_of_Vehicles",
    "Number_of_Casualties", "Day_of_Week", "latitude", "longitude",
}
missing_columns = required_columns - set(df.columns)
if missing_columns:
    st.error("The dataset is missing required columns: " + ", ".join(sorted(missing_columns)))
    st.stop()

# Filters are organized by what the user wants to compare.
st.sidebar.title("Filter the accident records")
st.sidebar.caption("Date, severity, police area, and district apply to every page.")
valid_dates = df["Date"].dropna()
if valid_dates.empty:
    st.error("No valid dates were found in the dataset.")
    st.stop()

date_range = st.sidebar.date_input(
    "Accident date range",
    value=(valid_dates.min().date(), valid_dates.max().date()),
    key="global_date_range",
)
filtered = df.dropna(subset=["Date"]).copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    filtered = filtered[filtered["Date"].between(start_date, end_date)]

severity_options = sorted(filtered["Severity"].dropna().unique().tolist())
selected_severity = st.sidebar.multiselect(
    "Severity",
    options=severity_options,
    default=severity_options,
    key="global_severity",
)
filtered = filtered[filtered["Severity"].isin(selected_severity)]

if "Police force" in filtered.columns:
    police_options = sorted(filtered["Police force"].dropna().unique().tolist())
    selected_police = st.sidebar.selectbox(
        "Police area", ["All police areas"] + police_options,
        key="global_police_area",
    )
    if selected_police != "All police areas":
        filtered = filtered[filtered["Police force"] == selected_police]

if "District" in filtered.columns:
    district_options = sorted(filtered["District"].dropna().unique().tolist())
    selected_district = st.sidebar.selectbox(
        "Local authority district",
        ["All districts"] + district_options,
        key="global_district",
    )
    if selected_district != "All districts":
        filtered = filtered[filtered["District"] == selected_district]

if filtered.empty:
    st.warning("No records match the current filters. Change a selection in the sidebar.")
    st.stop()

pages = [
    st.Page(lambda: show_overview(filtered), title="Overview", url_path="overview", icon="🏠", default=True),
    st.Page(lambda: show_time(filtered), title="When?", url_path="when", icon="🕒"),
    st.Page(lambda: show_location(filtered), title="Where?", url_path="where", icon="📍"),
    st.Page(lambda: show_conditions(filtered), title="Road & conditions", url_path="conditions", icon="🛣️"),
    st.Page(lambda: show_impact(filtered), title="Vehicles & casualties", url_path="impact", icon="👥"),
    st.Page(lambda: show_data(filtered, df), title="Data quality", url_path="data-quality", icon="📋"),
]

current_page = st.navigation(pages, position="top")
current_page.run()
