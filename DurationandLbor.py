import streamlit as st

# === Set up page ===
st.set_page_config(page_title="Labor Duration Estimator", layout="centered")

# === Calculation Functions ===
def estimate_duration_by_productivity(prod_per_labor_per_day, labor_count, quantity):
    daily_output = prod_per_labor_per_day * labor_count
    duration = quantity / daily_output if daily_output else 0
    return round(daily_output, 2), round(duration, 2)

def required_labor_for_target(prod_per_labor_per_day, quantity, target_days):
    if prod_per_labor_per_day == 0 or target_days == 0:
        return 0
    required_labor = quantity / (prod_per_labor_per_day * target_days)
    return round(required_labor, 2)

# === Streamlit UI ===
st.title("🛠️ Labor Duration Estimation Tool")
st.markdown("""
Estimate how many laborers you need or how many days are required to finish a job based on productivity.

Input:
- Total work quantity
- Available labor per day
- Production per labor per day (from statistical measures)
- Optionally, a target duration
""")

with st.form("estimation_form"):
    quantity = st.number_input("📦 Total Quantity of Work (units)", min_value=0.0)
    labor_available = st.number_input("👷 Available Laborers per Day", min_value=1)
    work_hours = st.number_input("⏱️ Work Hours per Day (for reference)", value=8.0, min_value=1.0)

    st.markdown("### 📊 Production per Labor per Day (units)")
    prod_pert = st.number_input("PERT Estimate", min_value=0.0, step=0.1)
    prod_median = st.number_input("Median Estimate", min_value=0.0, step=0.1)
    prod_mode = st.number_input("Mode Estimate", min_value=0.0, step=0.1)
    prod_trimmed_mean = st.number_input("Trimmed Mean Estimate", min_value=0.0, step=0.1)
    prod_mean = st.number_input("Arithmetic Mean Estimate", min_value=0.0, step=0.1)

    st.markdown("### 🎯 Target Completion")
    target_duration = st.number_input("🎯 Target Duration to Finish (days)", min_value=0.0, step=0.5)

    submitted = st.form_submit_button("✅ Estimate")

# === Results ===
if submitted:
    st.header("📈 Results")
    estimates = {
        "PERT": prod_pert,
        "Median": prod_median,
        "Mode": prod_mode,
        "Trimmed Mean": prod_trimmed_mean,
        "Arithmetic Mean": prod_mean
    }

    for label, prod_rate in estimates.items():
        if prod_rate > 0:
            daily_output, duration = estimate_duration_by_productivity(prod_rate, labor_available, quantity)
            required_labor = required_labor_for_target(prod_rate, quantity, target_duration) if target_duration > 0 else None

            st.subheader(f"📘 {label} Estimate")
            st.write(f"🔹 **Daily Output:** {daily_output} units/day")
            st.write(f"📅 **Estimated Duration:** {duration} days")
            if required_labor:
                st.write(f"👷 **Labor Needed to Finish in {target_duration} days:** {required_labor}")
