import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Always initialize session_state right after imports!
if "data" not in st.session_state:
    st.session_state["data"] = []

# Define emission factors
EMISSION_FACTORS = {
    "India": {
        "Transportation": {
            "Air (Economy)": 0.15,  # kgCO2/km
            "Air (Business)": 0.4,  # kgCO2/km
            "Train": 0.03,          # kgCO2/km
            "Car": 0.11,            # kgCO2/km
            "Bus": 0.05             # kgCO2/km
        },
        "Electricity": 0.716,      # kgCO2/kWh
        "Diet": 3.75,              # kgCO2/meal
        "Waste": 1.9375,           # kgCO2/kg
        "Clothing": 1.67,          # kgCO2/item
        "Plastic_Bottles": 0.05,   # kgCO2 per plastic bottle
        "Data_Center": 0.82,       # kgCO2/kWh
        "Methane_Food_Waste": 0.5, # kgCO2-equivalent methane per kg
        "Paper": 4.64 / 1000       # kg CO2 per sheet (converted from g to kg)
    }
}

st.set_page_config(layout="wide", page_title="🌍 Carbon Conserve")

st.title("🌍 Carbon Conserve")
st.markdown("""
Welcome to the **Carbon Conserve**!
Use this tool to calculate and track your personal carbon footprint.
Together, let's take steps toward sustainability!
""")

# Sidebar: Recommendations
st.sidebar.subheader("♻️ Recommendations")
st.sidebar.markdown("""
Here are some general recommendations to reduce your carbon footprint:
1. **Transportation**: Opt for public transport or carpooling instead of personal vehicles.
2. **Electricity**: Reduce energy consumption by switching to energy-efficient appliances or using renewable energy sources.
3. **Diet**: Choose plant-based meals and reduce food waste.
4. **Waste**: Minimize waste by recycling and composting.
5. **Clothing**: Avoid fast fashion and buy only when necessary.
6. **Plastic**: Reduce single-use plastics by using reusable alternatives.
7. **Digital Clean-Up**: Regularly delete unused files and manage digital storage to save energy.
""")

# Step 1: Enter Name and Month
st.subheader("Step 1: Enter Your Name and Month")
name = st.text_input("Enter Your Name", placeholder="Type your name here")
month = st.selectbox("Select Month", [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
])

# Button to delete existing data for the selected month
if st.button("Delete Data for Selected Month"):
    before = len(st.session_state["data"])
    st.session_state["data"] = [
        entry for entry in st.session_state["data"] if entry["Month"] != month
    ]
    after = len(st.session_state["data"])
    if before > after:
        st.success(f"Data for {month} has been deleted successfully.")
    else:
        st.info(f"No data found for {month} to delete.")

# Step 2: Data Input
st.subheader("Step 2: Enter Your Data")
with st.form(key="input_form"):
    col1, col2 = st.columns(2)
    with col1:
        travel_mode = st.selectbox("🚶 Travel Mode", ["Select", "Air (Economy)", "Air (Business)", "Train", "Car", "Bus"])
        travel_distance = st.slider("🛤 Travel Distance (in km)", 0.0, 5000.0)
        electricity = st.slider("💡 Monthly electricity consumption (in kWh)", 0.0, 1000.0)
        plastic_bottles = st.number_input("🍼 Plastic bottles or cups used per month", min_value=0, step=1)

    with col2:
        clothing_items = st.number_input("🛍️ Clothing items purchased per month", min_value=0, step=1)
        meals_per_day = st.number_input("🍽 Meals per day", min_value=1, step=1)
        waste = st.slider("🗑 Weekly waste generated (in kg)", 0.0, 100.0)
        gb_deleted = st.number_input("📂 GB of unused files deleted in a month", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("Calculate CO2 Emissions")

if submitted:
    if not name:
        st.error("Please enter your name before calculating!")
    elif travel_mode == "Select":
        st.error("Please select a travel mode!")
    else:
        # Normalize inputs (calculate monthly emissions)
        waste_monthly = waste * 4  # weeks per month
        energy_saved = gb_deleted * 0.3  # kWh saved from file deletion
        co2_savings = round(energy_saved * EMISSION_FACTORS["India"]["Data_Center"] / 1000, 3)  # in tonnes!

        # Calculate carbon emissions (convert kg to tonnes for all here)
        travel_emissions = round(travel_distance * EMISSION_FACTORS["India"]["Transportation"].get(travel_mode, 0) / 1000, 3)
        electricity_emissions = round(EMISSION_FACTORS["India"]["Electricity"] * electricity / 1000, 3)
        diet_emissions = round(EMISSION_FACTORS["India"]["Diet"] * meals_per_day * 30 / 1000, 3)
        waste_emissions = round(EMISSION_FACTORS["India"]["Waste"] * waste_monthly / 1000, 3)
        clothing_emissions = round(clothing_items * EMISSION_FACTORS["India"]["Clothing"] / 1000, 3)
        plastic_emissions = round(plastic_bottles * EMISSION_FACTORS["India"]["Plastic_Bottles"] / 1000, 3)

        total_emissions = round(
            travel_emissions + electricity_emissions + diet_emissions +
            waste_emissions + clothing_emissions + plastic_emissions - co2_savings, 3
        )

        # Only allow one entry per month per user
        existing = [entry for entry in st.session_state["data"] if entry["Month"] == month and entry["Name"] == name]
        if not existing:
            st.session_state["data"].append({
                "Name": name,
                "Month": month,
                "Travel": travel_emissions,
                "Electricity": electricity_emissions,
                "Diet": diet_emissions,
                "Waste": waste_emissions,
                "Clothing": clothing_emissions,
                "Plastic": plastic_emissions,
                "Digital Clean-Up Savings": -co2_savings,
                "Total Emissions": total_emissions
            })
            st.success(f"🌍 Total Carbon Footprint for {name} in {month}: {total_emissions} tonnes CO2/month")
        else:
            st.warning(f"Data for {month} already exists for {name}. Please delete it to add new data.")

        # Emissions Breakdown
        st.subheader("Breakdown of Your Emissions")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🚶 Travel: **{travel_emissions} tonnes CO2/month**")
            st.info(f"💡 Electricity: **{electricity_emissions} tonnes CO2/month**")
            st.info(f"🍽 Diet: **{diet_emissions} tonnes CO2/month**")
            st.info(f"🗑 Waste: **{waste_emissions} tonnes CO2/month**")
        with col2:
            st.info(f"🛍️ Clothing: **{clothing_emissions} tonnes CO2/month**")
            st.info(f"🍼 Plastic Usage: **{plastic_emissions} tonnes CO2/month**")
            st.info(f"📂 Digital Clean-Up Savings: **-{co2_savings} tonnes CO2/month**")

        # Emissions Breakdown Chart
        labels = ['Travel', 'Electricity', 'Diet', 'Waste', 'Clothing', 'Plastic Usage', 'Digital Clean-Up Savings']
        values = [
            travel_emissions, electricity_emissions, diet_emissions, waste_emissions,
            clothing_emissions, plastic_emissions, -co2_savings
        ]
        fig, ax = plt.subplots()
        ax.bar(labels, values, color='skyblue')
        ax.set_ylabel("Emissions (tonnes CO2)")
        ax.set_title("Carbon Emissions Breakdown")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

# Dashboard for past data
st.subheader("📊 Your Carbon Footprint Dashboard")
if st.session_state["data"]:
    df = pd.DataFrame(st.session_state["data"])
    st.dataframe(df)

    # Only numeric columns relevant for stacked bar
    emission_cols = ['Travel', 'Electricity', 'Diet', 'Waste', 'Clothing', 'Plastic', 'Digital Clean-Up Savings']
    # Set index to Month + Name (if needed)
    if "Month" in df and "Name" in df:
        df = df.set_index(["Month", "Name"])
    elif "Month" in df:
        df = df.set_index("Month")

    fig, ax = plt.subplots(figsize=(10, 6))
    df[emission_cols].plot(kind="bar", stacked=True, ax=ax)
    plt.title("Monthly Carbon Footprint Breakdown by Category")
    plt.ylabel("Emissions (tonnes CO2/month)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("No carbon footprint data available. Please enter your data to start tracking.")
