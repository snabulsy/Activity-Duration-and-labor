from datetime import datetime
import pandas as pd
import streamlit as st

# === Streamlit Setup ===
st.set_page_config(page_title="PERT-Based Labor Estimation Tool", layout="wide")

st.title("🔧 Labor Duration & Requirement Estimator")
st.markdown("""
Use this tool to estimate construction **activity durations** using statistical methods and **PERT**.  
It also helps you calculate **how many laborers are needed** to meet a target completion time.
""")

# === User Input Form ===
with st.form("input_form"):
    activity_name = st.text_input("Activity Name", placeholder="e.g., Masonry")

    col1, col2 = st.columns(2)
    with col1:
        optimistic = st.number_input("Optimistic Labor/Hour (O)", min_value=0.0, step=0.1)
        median = st.number_input("Median Labor/Hour", min_value=0.0, step=0.1)
        trimmed_mean = st.number_input("Trimmed Mean Labor/Hour", min_value=0.0, step=0.1)
        mean = st.number_input("Arithmetic Mean Labor/Hour", min_value=0.0, step=0.1)
    with col2:
        most_likely = st.number_input("Most Likely Labor/Hour (M)", min_value=0.0, step=0.1)
        mode = st.number_input("Mode Labor/Hour", min_value=0.0, step=0.1)
        pessimistic = st.number_input("Pessimistic Labor/Hour (P)", min_value=0.0, step=0.1)

    st.markdown("---")
    work_quantity = st.number_input("Total Work Quantity (units)", min_value=0.0, step=0.1)
    available_labor = st.number_input("Available Laborers per Day", min_value=1)
    work_hours = st.number_input("Working Hours per Day", value=8, min_value=1)

    st.markdown("### ⏳ Optional: Target Completion")
    target_duration = st.number_input("Target Duration (Days)", min_value=0.0, step=0.1)

    submitted = st.form_submit_button("Calculate")

# === Helper Functions ===
def estimate_duration(labor_rate, laborers, hours, quantity):
    daily_output = labor_rate * laborers * hours
    if daily_output == 0:
        return 0.0, 0.0
    duration = quantity / daily_output
    return round(daily_output, 2), round(duration, 2)

def required_labor_for_target(labor_rate, hours, quantity, target_days):
    if labor_rate == 0 or hours == 0 or target_days == 0:
        return 0.0
    labor_required = quantity / (labor_rate * hours * target_days)
    return round(labor_required, 2)

# === Processing Inputs ===
if submitted:
    results = []
    labor_needed_list = []

    # PERT
    if optimistic > 0 and most_likely > 0 and pessimistic > 0:
        pert_rate = round((optimistic + 4 * most_likely + pessimistic) / 6, 2)
        pert_output, pert_duration = estimate_duration(pert_rate, available_labor, work_hours, work_quantity)
        results.append(["PERT", pert_rate, pert_output, pert_duration])
        if target_duration > 0:
            labor_needed = required_labor_for_target(pert_rate, work_hours, work_quantity, target_duration)
            labor_needed_list.append(["PERT", labor_needed])

    # Other Methods
    if median > 0:
        m_output, m_duration = estimate_duration(median, available_labor, work_hours, work_quantity)
        results.append(["Median", median, m_output, m_duration])
        if target_duration > 0:
            labor_needed_list.append(["Median", required_labor_for_target(median, work_hours, work_quantity, target_duration)])
    if mode > 0:
        mo_output, mo_duration = estimate_duration(mode, available_labor, work_hours, work_quantity)
        results.append(["Mode", mode, mo_output, mo_duration])
        if target_duration > 0:
            labor_needed_list.append(["Mode", required_labor_for_target(mode, work_hours, work_quantity, target_duration)])
    if trimmed_mean > 0:
        tm_output, tm_duration = estimate_duration(trimmed_mean, available_labor, work_hours, work_quantity)
        results.append(["Trimmed Mean", trimmed_mean, tm_output, tm_duration])
        if target_duration > 0:
            labor_needed_list.append(["Trimmed Mean", required_labor_for_target(trimmed_mean, work_hours, work_quantity, target_duration)])
    if mean > 0:
        a_output, a_duration = estimate_duration(mean, available_labor, work_hours, work_quantity)
        results.append(["Arithmetic Mean", mean, a_output, a_duration])
        if target_duration > 0:
            labor_needed_list.append(["Arithmetic Mean", required_labor_for_target(mean, work_hours, work_quantity, target_duration)])

    # === Display Results ===
    st.success(f"📋 Results for Activity: **{activity_name or 'Unnamed'}**")

    df = pd.DataFrame(results, columns=[
        "Estimation Method", "Labor/Hour", "Estimated Output per Day (units)", "Estimated Duration (days)"
    ])
    st.subheader("📊 Duration Estimates")
    st.dataframe(df, use_container_width=True)

    if target_duration > 0 and labor_needed_list:
        st.subheader(f"👷 Labor Required to Finish in **{target_duration} Days**")
        df_labor = pd.DataFrame(labor_needed_list, columns=["Estimation Method", "Required Laborers per Day"])
        st.dataframe(df_labor, use_container_width=True)

        # Compare with estimated duration
        for method, _, _, dur in results:
            if dur > target_duration:
                st.warning(f"⚠️ The **{method}** estimated duration is **{dur} days**, longer than your target.")

