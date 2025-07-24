from datetime import datetime
import pandas as pd
import streamlit as st

# === Streamlit App Setup ===
st.set_page_config(page_title="PERT-Based Labor Estimation Tool")

st.title("🔧 Labor Duration Estimator with PERT & Required Labor")
st.markdown("""
Estimate construction activity durations using both statistical metrics (mean, median, mode, trimmed mean) and PERT methodology.  
You can also specify a target duration to calculate how much **labor** is needed to finish on time.
""")

# === User Input Form ===
with st.form("input_form"):
    activity_name = st.text_input("Activity Name", placeholder="e.g., Masonry")

    col1, col2 = st.columns(2)
    with col1:
        optimistic = st.number_input("Optimistic Labor/Hour (O)", min_value=0.0, step=0.1)
        median = st.number_input("Median Labor/Hour", min_value=0.0, step=0.1)
        trimmed_mean = st.number_input("Trimmed Mean Labor/Hour", min_value=0.0, step=0.1)
    with col2:
        most_likely = st.number_input("Most Likely Labor/Hour (M)", min_value=0.0, step=0.1)
        mode = st.number_input("Mode Labor/Hour", min_value=0.0, step=0.1)
        mean = st.number_input("Arithmetic Mean Labor/Hour", min_value=0.0, step=0.1)

    pessimistic = st.number_input("Pessimistic Labor/Hour (P)", min_value=0.0, step=0.1)

    st.markdown("---")
    work_quantity = st.number_input("Total Work Quantity (units)", min_value=0.0, step=0.1)
    labor_per_day = st.number_input("Available Laborers per Day", min_value=1)
    hours_per_day = st.number_input("Work Hours per Day", value=8, min_value=1)

    target_duration = st.number_input("Target Duration to Finish (Days)", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("Calculate")

# === Helper Function to Estimate Duration ===
def estimate_duration(labor_per_hour, labor_available, work_hours, quantity):
    labor_day = labor_per_hour * work_hours
    daily_output = labor_available / labor_day if labor_day else 0
    duration = quantity / daily_output if daily_output else 0
    return round(labor_day, 2), round(daily_output, 2), round(duration, 2)

# === Helper to Calculate Required Labor to Finish in Target Duration ===
def required_labor_for_duration(labor_per_hour, work_hours, quantity, target_days):
    if labor_per_hour == 0 or work_hours == 0 or target_days == 0:
        return 0.0
    labor_needed = (labor_per_hour * work_hours * quantity) / target_days
    return round(labor_needed, 2)

# === Calculations and Output ===
if submitted:
    results = []
    required_labor_results = []

    # PERT Estimate
    pert_labor_hour = round((optimistic + 4 * most_likely + pessimistic) / 6, 2)
    pert_day, pert_output, pert_duration = estimate_duration(pert_labor_hour, labor_per_day, hours_per_day, work_quantity)
    results.append(["PERT", pert_labor_hour, pert_day, pert_duration])
    required_labor_results.append(["PERT", required_labor_for_duration(pert_labor_hour, hours_per_day, work_quantity, target_duration)])

    # Other Estimates
    if median > 0:
        m_day, m_output, m_duration = estimate_duration(median, labor_per_day, hours_per_day, work_quantity)
        results.append(["Median", median, m_day, m_duration])
        required_labor_results.append(["Median", required_labor_for_duration(median, hours_per_day, work_quantity, target_duration)])
    if mode > 0:
        mo_day, mo_output, mo_duration = estimate_duration(mode, labor_per_day, hours_per_day, work_quantity)
        results.append(["Mode", mode, mo_day, mo_duration])
        required_labor_results.append(["Mode", required_labor_for_duration(mode, hours_per_day, work_quantity, target_duration)])
    if trimmed_mean > 0:
        tm_day, tm_output, tm_duration = estimate_duration(trimmed_mean, labor_per_day, hours_per_day, work_quantity)
        results.append(["Trimmed Mean", trimmed_mean, tm_day, tm_duration])
        required_labor_results.append(["Trimmed Mean", required_labor_for_duration(trimmed_mean, hours_per_day, work_quantity, target_duration)])
    if mean > 0:
        a_day, a_output, a_duration = estimate_duration(mean, labor_per_day, hours_per_day, work_quantity)
        results.append(["Arithmetic Mean", mean, a_day, a_duration])
        required_labor_results.append(["Arithmetic Mean", required_labor_for_duration(mean, hours_per_day, work_quantity, target_duration)])

    df = pd.DataFrame(results, columns=["Method", "Labor/Hour", "Labor/Day", "Estimated Duration (Days)"])
    df_req = pd.DataFrame(required_labor_results, columns=["Method", "Required Labor to Finish in Target Duration"])

    st.success(f"Estimation Results for Activity: **{activity_name or 'Unnamed'}**")
    st.subheader("Duration Estimates")
    st.dataframe(df, use_container_width=True)

    if target_duration > 0:
        st.subheader(f"Labor Needed to Finish in {target_duration} Days")
        st.dataframe(df_req, use_container_width=True)
