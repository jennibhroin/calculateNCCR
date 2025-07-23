import pandas as pd
from datetime import datetime
import streamlit as st

# Streamlit UI
st.title("SONIA Swap Compounded Rate & Coupon Calculator")

# User inputs
notional = st.number_input("Notional (£)", min_value=1, value=1_000_000, step=1_000)
start_date = st.date_input("Start Date", value=datetime(2019, 2, 1))
end_date = st.date_input("End Date", value=datetime(2019, 5, 1))
reset_lag = st.number_input("Reset Lag (business days)", min_value=0, value=5, step=1)

# Load SONIA rates (CSV with columns: date, rate)
@st.cache_data
def load_sonia():
    sonia = pd.read_csv('sonia_rates.csv', parse_dates=['date'])
    sonia.set_index('date', inplace=True)
    return sonia

sonia = load_sonia()

if st.button("Calculate"):
    # Generate schedule of accrual dates (business days)
    dates = pd.date_range(start_date, end_date, freq='B')
    if len(dates) < 2:
        st.error("Please select a valid period with at least two business days.")
    else:
        compounded = 1.0
        prev_date = dates[0]
        for curr_date in dates[1:]:
            # Apply reset lag
            fixing_date = curr_date - pd.tseries.offsets.BDay(reset_lag)
            # Get SONIA rate for fixing date
            try:
                rate = sonia.loc[fixing_date]['rate']
            except KeyError:
                # If missing, try previous available date
                rate = sonia.loc[:fixing_date].iloc[-1]['rate']
            # Day count fraction (ACT/365)
            dcf = (curr_date - prev_date).days / 365
            compounded *= (1 + rate * dcf)
            prev_date = curr_date

        compounded_rate = compounded - 1
        coupon = notional * compounded_rate

        st.success(f"Compounded SONIA rate: {compounded_rate:.6%}")
        st.success(f"Coupon amount: £{coupon:,.2f}")