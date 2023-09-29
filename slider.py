import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go


def bond_price(c, y, m, f, p, payments):
    # Calculate present value of coupon payments
    coupon_pv = sum([c * p / (1 + y / f) ** (i) for i in range(1, payments + 1)])

    # Calculate present value of principal
    principal_pv = p / (1 + y / f) ** payments

    return coupon_pv + principal_pv


def macaulay_duration(c, y, m, f, p, payments):
    # Calculate weighted average time to receive each cash flow
    duration = sum([i * (c * p) / (1 + y / f) ** (i) for i in range(1, payments + 1)]) + m * p / (1 + y / f) ** (payments)
    return duration / bond_price(c, y, m, f, p, payments)


def convexity(c, y, m, f, p, payments):
    convex = sum([i ** 2 * (c * p) / (1 + y / f) ** (i) for i in range(1, payments + 1)]) + m ** 2 * p / (1 + y / f) ** (
            payments)

    return convex / (bond_price(c, y, m, f, p, payments) * (1 + y / f) ** 2)


def price_estimate(c, y, dy, m, f, p, payments):
    current_price = bond_price(c, y, m, f, p, payments)
    duration = macaulay_duration(c, y, m, f, p, payments)
    convex = convexity(c, y, m, f, p, payments)

    # Explicitly breaking down price change
    price_change_due_to_duration = -duration * current_price * dy
    price_change_due_to_convexity = 0.5 * convex * current_price * dy ** 2

    total_price_change = price_change_due_to_duration + price_change_due_to_convexity
    new_price = current_price + total_price_change

    return new_price


def compute_maturity(settlement_date: datetime, end_date: datetime) -> int:
    return (end_date - settlement_date).days / 365.0  # Convert days to years


def compute_expiration_date(maturity: float) -> datetime:
    days_to_add = int(maturity * 365)  # Convert maturity in years to days
    return datetime.today() + timedelta(days=days_to_add)


def main():
    st.title('Bond Price Change vs. YTM')
    if 'bonds' not in st.session_state:
        st.session_state.bonds = []

    options = ["No Selection", "New Bond"]
    if st.session_state.bonds:
        options.extend(["Modify Existing Bond", "Add Variation of Existing Bond"])
    bond_selection = st.selectbox("Select an option: ", options)

    ready = False
    if bond_selection == 'New Bond':
        c = st.number_input('Coupon Rate (in %)', min_value=0.0, max_value=15.0, value=5.0) / 100
        y = st.number_input('Current YTM (in %)', min_value=0.0, max_value=15.0, value=10.0) / 100
        settlement_date = st.date_input("Settlement Date", datetime.today())
        end_date = st.date_input(
            "End Date",
            datetime.today() + timedelta(days=30 * 365),
            max_value=datetime.today() + timedelta(days=50 * 365)  # Extend up to 50 years from now
        )
        f = st.number_input('Payment Frequency', min_value=1, max_value=12, value = 2)
        m = compute_maturity(settlement_date, end_date)
        total_payments = int(m * f)

        if st.button("Add Bond"):
            st.write(f'With the chosen dates, the effective maturity is approximately {m:.2f} years.')
            st.write(f'Total payment periods over this maturity: {total_payments}')
            st.session_state.bonds.append((c, y, m, f, settlement_date, end_date))
            ready = True
    elif bond_selection == 'Modify Existing Bond':
        chosen_bond = st.selectbox("Select a bond", [f"Bond {i + 1}" for i in range(len(st.session_state.bonds))])
        bond = int(chosen_bond.split(" ")[-1]) - 1
        c = st.slider('Coupon Rate (in %)', 0.0, 15.0, st.session_state.bonds[bond][0]*100) / 100.0
        y = st.slider('Current YTM (in %)', 0.0, 15.0, st.session_state.bonds[bond][1]*100) / 100.0
        settlement_date = st.date_input("Settlement Date", st.session_state.bonds[bond][4])
        end_date = st.date_input("End Date", st.session_state.bonds[bond][5])
        f = st.slider('Payment Frequency', 1, 12, st.session_state.bonds[bond][3])
        m = compute_maturity(settlement_date, end_date)
        total_payments = int(m * f)

        if st.button("Update Bond"):
            st.write(f'With the chosen dates, the effective maturity is approximately {m:.2f} years.')
            st.write(f'Total payment periods over this maturity: {total_payments}')
            st.session_state.bonds[bond] = (c, y, m, f, settlement_date, end_date)
            ready = True
    elif bond_selection == 'Add Variation of Existing Bond':
        chosen_bond = st.selectbox("Select a bond", [f"Bond {i + 1}" for i in range(len(st.session_state.bonds))])
        if chosen_bond:
            bond = int(chosen_bond.split(" ")[-1]) - 1
        c = st.slider('Coupon Rate (in %)', 0.0, 15.0, st.session_state.bonds[bond][0]*100) / 100.0
        y = st.slider('Current YTM (in %)', 0.0, 15.0, st.session_state.bonds[bond][1]*100) / 100.0
        settlement_date = st.date_input("Settlement Date", st.session_state.bonds[bond][4])
        end_date = st.date_input("End Date", st.session_state.bonds[bond][5])
        f = st.slider('Payment Frequency', 1, 12, st.session_state.bonds[bond][3])
        m = compute_maturity(settlement_date, end_date)
        total_payments = int(m * f)

        if st.button("Add Variation"):
            st.write(f'With the chosen dates, the effective maturity is approximately {m:.2f} years.')
            st.write(f'Total payment periods over this maturity: {total_payments}')
            st.session_state.bonds.append((c, y, m, f, settlement_date, end_date))
            ready = False

    # List bonds
    if bond_selection in ["New Bond", "Modify Existing Bond", "Add Variation of Existing Bond"]:
        if st.button("Refresh Dropdown"):
            st.experimental_rerun()
    st.header("Bonds:")
    for idx, (c, y, m, f, start_date, end_date) in enumerate(st.session_state.bonds, 1):
        st.write(f"Bond {idx}: Coupon={c * 100:.2f}%, YTM={y * 100:.2f}%, Maturity={m:.2f} years, Frequency={f}")

    dy_values = np.linspace(-0.05, 0.05, 100)
    fig = go.Figure()

    # Add each bond's data to the figure
    for idx, (c, y, m, f, start_date, end_date) in enumerate(st.session_state.bonds, 1):
        total_payments = int(m*f)
        original_price = bond_price(c, y, m, f, 1, total_payments)  # Assuming principal of 1
        estimated_prices = [price_estimate(c, y, dy, m, f, 1, total_payments) for dy in dy_values]
        percent_changes = [(new_price - original_price) / original_price * 100 for new_price in estimated_prices]
        fig.add_trace(go.Scatter(x=dy_values * 100, y=percent_changes, mode='lines', name=f'Bond {idx}'))

    # Set layout details
    all_percent_changes = []
    for idx, (c, y, m, f, start_date, end_date) in enumerate(st.session_state.bonds, 1):
        original_price = bond_price(c, y, m, f, 1, total_payments)
        estimated_prices = [price_estimate(c, y, dy, m, f, 1, total_payments) for dy in dy_values]
        percent_changes = [(new_price - original_price) / original_price * 100 for new_price in estimated_prices]
        all_percent_changes.extend(percent_changes)

    if not all_percent_changes:
        y_min = -10
        y_max = 10
    else:
        y_min = min(all_percent_changes) - 5  # a little margin for clarity
        y_max = max(all_percent_changes) + 5  # a little margin for clarity

    # Add vertical line at x=0
    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=y_min,
        y1=y_max,
        line=dict(color="grey", width=2, dash="dash")
    )
    fig.add_shape(
        type="line",
        x0=min(dy_values) * 100 - 10,
        x1=max(dy_values) * 100 + 10,
        y0=0,
        y1=0,
        line=dict(color="grey", width=2, dash="dash")
    )
    x_min = min(dy_values) * 100
    x_max = max(dy_values) * 100

    # Ensure the range is at least from -5 to 5 by default.
    x_min = -5 if x_min > -5 else x_min
    x_max = 5 if x_max < 5 else x_max

    fig.update_layout(
        title='% Change in Bond Price vs. Change in YTM',
        xaxis_title='Change in YTM (%)',
        xaxis=dict(range=[x_min, x_max]),  # Set x-axis range dynamically
        yaxis_title='% Change in Bond Price',
        hovermode='x'  # Highlight y-values for the same x-value across all curves
    )

    # Display the plot in the Streamlit app
    st.plotly_chart(fig)


    # Bond parameters inputs
    # c = st.slider('Coupon Rate (in %)', 0.0, 15.0, 5.0) / 100.0
    # y = st.slider('Current YTM (in %)', 0.0, 15.0, 6.0) / 100.0
    # settlement_date = st.date_input("Settlement Date", datetime.today())
    # end_date = st.date_input("End Date", datetime.today() + timedelta(days=5 * 365))
    # f = st.slider('Payment Frequency', 1, 12, 2)
    #
    # m = compute_maturity(settlement_date, end_date)
    # total_payments = int(m * f)
    #
    # if bond_selection == "New Bond":
    #     if st.button("Add Bond"):
    #         st.session_state.bonds.append((c, y, m, f))
    # else:
    #     if st.button("Add Variation"):
    #         st.session_state.bonds.append((c, y, m, f))  # Add this variation as a new bond
    #
    # # List bonds
    # st.header("Bonds:")
    # for idx, (c, y, m, f) in enumerate(st.session_state.bonds, 1):
    #     st.write(f"Bond {idx}: Coupon={c * 100:.2f}%, YTM={y * 100:.2f}%, Maturity={m} years, Frequency={f}")
    #
    # dy_values = np.linspace(-0.05, 0.05, 100)
    # fig = go.Figure()
    #
    # # Add each bond's data to the figure
    # for idx, (c, y, m, f) in enumerate(st.session_state.bonds, 1):
    #     original_price = bond_price(c, y, m, f, 1, total_payments)  # Assuming principal of 1
    #     estimated_prices = [price_estimate(c, y, dy, m, f, 1, total_payments) for dy in dy_values]
    #     percent_changes = [(new_price - original_price) / original_price * 100 for new_price in estimated_prices]
    #     fig.add_trace(go.Scatter(x=dy_values * 100, y=percent_changes, mode='lines', name=f'Bond {idx}'))
    #
    # # Set layout details
    # fig.update_layout(
    #     title='% Change in Bond Price vs. Change in YTM',
    #     xaxis_title='Change in YTM (%)',
    #     yaxis_title='% Change in Bond Price',
    #     hovermode='x'  # Highlight y-values for the same x-value across all curves
    # )
    #
    # # Display the plot in the Streamlit app
    # st.plotly_chart(fig)


if __name__ == "__main__":
    main()