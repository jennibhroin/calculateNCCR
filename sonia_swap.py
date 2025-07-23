import pandas as pd
from datetime import datetime, timedelta

# Parameters
START_DATE = datetime(2019, 2, 1)
END_DATE = datetime(2019, 5, 1)
NOTIONAL = 1_000_000
RESET_LAG = 5  # days

# Load SONIA rates (CSV with columns: date, rate)
sonia = pd.read_csv('sonia_rates.csv', parse_dates=['date'])
sonia.set_index('date', inplace=True)

# Generate schedule of accrual dates (business days)
dates = pd.date_range(START_DATE, END_DATE, freq='B')

# Calculate compounded rate
compounded = 1.0
prev_date = dates[0]
for curr_date in dates[1:]:
    # Apply reset lag
    fixing_date = curr_date - pd.tseries.offsets.BDay(RESET_LAG)
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
coupon = NOTIONAL * compounded_rate

print(f"Compounded SONIA rate: {compounded_rate:.6%}")
print(f"Coupon amount: £{coupon:,.2f}")