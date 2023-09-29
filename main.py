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


# Press the green button in the gutter to run the script.

if __name__ == '__main__':
    bond_parameters = {
        "A": {"c": 0.12, "y": 0.1, "m": 5, "f": 2, "p": 1000},
        "B": {"c": 0.12, "y": 0.1, "m": 30, "f": 2, "p": 1000},
        "C": {"c": 0.03, "y": 0.1, "m": 30, "f": 2, "p": 1000},
        "D": {"c": 0.03, "y": 0.06, "m": 30, "f": 2, "p": 1000}
    }

    # Adjust the range of yield changes from -5% to 5%
    dy_values = np.linspace(-0.05, 0.05, 100)

    # Plotting each bond
    for bond_name, params in bond_parameters.items():
        original_price = bond_price(params["c"], params["y"], params["m"], params["f"], params["p"])
        estimated_prices = [price_estimate(params["c"], params["y"], dy, params["m"], params["f"], params["p"]) for dy
                            in dy_values]

        # Calculate percent changes in bond price
        percent_changes = [(new_price - original_price) / original_price * 100 for new_price in estimated_prices]

        # Constructing a label for the legend that includes the bond's parameters
        label = (f'Bond {bond_name}: '
                 f'C={params["c"] * 100:.2f}%, YTM={params["y"] * 100:.2f}%, '
                 f'M={params["m"]}yrs, F={params["f"]}, P={params["p"]}')

        plt.plot(dy_values * 100, percent_changes, label=label)

    # Finalizing the plot

    # Adjusting the x-axis ticks to be spread apart by 1
    plt.xticks(np.arange(-5, 6, 1))  # assuming a range of -5% to 5% for dy_values
    plt.axvline(x=0, color='grey', linestyle='--')
    plt.title('% Change in Bond Price vs. Change in YTM')
    plt.xlabel('Change in YTM (%)')
    plt.ylabel('% Change in Bond Price')
    plt.legend(fontsize='small')
    plt.grid(True)
    plt.show()