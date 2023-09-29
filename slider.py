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

    # Check if there's any state saved
    if 'bonds' not in st.session_state:
        st.session_state.bonds = []

    # Add bond section
    with st.form(key='add_bond_form'):
        st.header("Add a Bond")

        # Bond parameters inputs
        c_slider = st.slider('Coupon Rate (in %) using Slider', 0.0, 15.0, 5.0)
        c = st.number_input('Coupon Rate (in %) using Input', min_value=0.0, max_value=15.0, value=c_slider) / 100

        y_slider = st.slider('Current YTM (in %) using Slider', 0.0, 15.0, 6.0)
        y = st.number_input('Current YTM (in %) using Input', min_value=0.0, max_value=15.0, value=y_slider) / 100

        settlement_date = st.date_input("Settlement Date", datetime.today())
        end_date = st.date_input("End Date", datetime.today() + timedelta(days=5 * 365))

        # st.write(f'With the chosen dates, the effective maturity is approximately {m:.2f} years.')

        f_slider = st.slider('Payment Frequency using Slider', 1, 12, 2)
        f = st.number_input('Payment Frequency using Input', min_value=1, max_value=12, value=f_slider)

        m = compute_maturity(settlement_date, end_date)
        total_payments = int(m * f)

        # Button to add bond
        add_bond = st.form_submit_button("Add Bond")

        # Logic to add bond to session state
        if add_bond:
            st.session_state.bonds.append((c, y, m, f))
            st.write(f'With the chosen dates, the effective maturity is approximately {m:.2f} years.')
            st.write(f'Total payment periods over this maturity: {total_payments}')

    # List bonds
    st.header("Bonds:")
    for idx, (c, y, m, f) in enumerate(st.session_state.bonds, 1):
        st.write(f"Bond {idx}: Coupon={c * 100:.2f}%, YTM={y * 100:.2f}%, Maturity={m} years, Frequency={f}")

    dy_values = np.linspace(-0.05, 0.05, 100)
    # Plotting
    # fig, ax = plt.subplots()

    #
    # for idx, (c, y, m, f) in enumerate(st.session_state.bonds, 1):
    #     original_price = bond_price(c, y, m, f, 1)  # Assuming principal of 1
    #     estimated_prices = [price_estimate(c, y, dy, m, f, 1) for dy in dy_values]
    #     percent_changes = [(new_price - original_price) / original_price * 100 for new_price in estimated_prices]
    #     ax.plot(dy_values * 100, percent_changes, label=f'Bond {idx}')
    #
    # ax.axvline(x=0, color='grey', linestyle='--')
    # ax.set_title('% Change in Bond Price vs. Change in YTM')
    # ax.set_xlabel('Change in YTM (%)')
    # ax.set_ylabel('% Change in Bond Price')
    # ax.legend()
    # ax.grid(True)
    #
    # st.pyplot(fig)
    fig = go.Figure()

    # Add each bond's data to the figure
    for idx, (c, y, m, f) in enumerate(st.session_state.bonds, 1):
        original_price = bond_price(c, y, m, f, 1, total_payments)  # Assuming principal of 1
        estimated_prices = [price_estimate(c, y, dy, m, f, 1, total_payments) for dy in dy_values]
        percent_changes = [(new_price - original_price) / original_price * 100 for new_price in estimated_prices]
        fig.add_trace(go.Scatter(x=dy_values * 100, y=percent_changes, mode='lines', name=f'Bond {idx}'))

    # Set layout details
    fig.update_layout(
        title='% Change in Bond Price vs. Change in YTM',
        xaxis_title='Change in YTM (%)',
        yaxis_title='% Change in Bond Price',
        hovermode='x'  # Highlight y-values for the same x-value across all curves
    )

    # Display the plot in the Streamlit app
    st.plotly_chart(fig)


if __name__ == "__main__":
    main()