"""Fig. 1 — Annual food consumption and city-level correlates ."""


def make_figure_1():
    inputs = load_inputs("fig1")
    annual_orders = inputs.annual_orders
    household_mass = inputs.annual_household_food_mass_Mt
    city = inputs.city_food_mass_and_covariates
    fig, ax = create_panels("abcd", rows=2, columns=2)

    # a–b: Annual food mass and shares
    for panel, year in [("a", 2019), ("b", 2025)]:
        ofd_mass = grams_to_megatonnes(
            annual_orders[year] * inputs.mean_food_g_per_order
        )
        masses = {"Household": household_mass[year], "OFD": ofd_mass}
        plot_bars(ax[panel], masses, ylabel="Annual food mass (Mt)")
        plot_inset_pie(ax[panel], normalize_to_shares(masses))
        set_title(ax[panel], year, projected=(year == 2025))

    # c–d: Standardized regression coefficients
    for panel, system in [("c", "OFD"), ("d", "Household")]:
        X = zscore(city[inputs.covariates_by_system[system]])
        y = zscore(city.food_mass[system])
        model = fit_stepwise_ols(X, y, intercept=True)
        beta, se = model.coefficients_without_intercept()
        plot_forest(
            ax[panel], beta,
            lower=beta - 1.96 * se, upper=beta + 1.96 * se,
            reference=0, labels=model.selected_predictors,
        )

    format_panels(fig, panel_labels=True, consistent_system_colors=True)
    export_figure(fig, "Fig1", formats=["pdf", "svg", "png"])
