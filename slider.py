import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

def bond_price(c, y, m, f, p):
    # Calculate present value of coupon payments
    coupon_pv = sum([c * p / (1 + y / f) ** (i) for i in range(1, m * f + 1)])

    # Calculate present value of principal
    principal_pv = p / (1 + y / f) ** (m * f)

    return coupon_pv + principal_pv


def macaulay_duration(c, y, m, f, p):
    # Calculate weighted average time to receive each cash flow
    duration = sum([i * (c * p) / (1 + y / f) ** (i) for i in range(1, m * f + 1)]) + m * p / (1 + y / f) ** (m * f)
    return duration / bond_price(c, y, m, f, p)


def convexity(c, y, m, f, p):
    convex = sum([i ** 2 * (c * p) / (1 + y / f) ** (i) for i in range(1, m * f + 1)]) + m ** 2 * p / (1 + y / f) ** (
            m * f)

    return convex / (bond_price(c, y, m, f, p) * (1 + y / f) ** 2)


def price_estimate(c, y, dy, m, f, p):
    current_price = bond_price(c, y, m, f, p)
    duration = macaulay_duration(c, y, m, f, p)
    convex = convexity(c, y, m, f, p)

    # Explicitly breaking down price change
    price_change_due_to_duration = -duration * current_price * dy
    price_change_due_to_convexity = 0.5 * convex * current_price * dy ** 2

    total_price_change = price_change_due_to_duration + price_change_due_to_convexity
    new_price = current_price + total_price_change

    return new_price

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

        m_slider = st.slider('Maturity (in years) using Slider', 1, 30, 5)
        m = st.number_input('Maturity (in years) using Input', min_value=1, max_value=30, value=m_slider)

        f_slider = st.slider('Payment Frequency using Slider', 1, 12, 2)
        f = st.number_input('Payment Frequency using Input', min_value=1, max_value=12, value=f_slider)

        # Button to add bond
        add_bond = st.form_submit_button("Add Bond")

        # Logic to add bond to session state
        if add_bond:
            st.session_state.bonds.append((c, y, m, f))

    # List bonds
    st.header("Bonds:")
    for idx, (c, y, m, f) in enumerate(st.session_state.bonds, 1):
        st.write(f"Bond {idx}: Coupon={c * 100:.2f}%, YTM={y * 100:.2f}%, Maturity={m} years, Frequency={f}")

    # Plotting
    fig, ax = plt.subplots()
    dy_values = np.linspace(-0.05, 0.05, 100)

    for idx, (c, y, m, f) in enumerate(st.session_state.bonds, 1):
        original_price = bond_price(c, y, m, f, 1)  # Assuming principal of 1
        estimated_prices = [price_estimate(c, y, dy, m, f, 1) for dy in dy_values]
        percent_changes = [(new_price - original_price) / original_price * 100 for new_price in estimated_prices]
        ax.plot(dy_values * 100, percent_changes, label=f'Bond {idx}')

    ax.axvline(x=0, color='grey', linestyle='--')
    ax.set_title('% Change in Bond Price vs. Change in YTM')
    ax.set_xlabel('Change in YTM (%)')
    ax.set_ylabel('% Change in Bond Price')
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)


if __name__ == "__main__":
    main()