"""Fig. 5 — Two efficiency indices and city associations."""


def calculate_cnei(carbon, nutrition, carbon_bounds, nutrition_bounds):
    c_min, c_max = carbon_bounds
    n_min, n_max = nutrition_bounds
    c = clip((carbon - c_min) / (c_max - c_min), 0, 1)
    n = clip((nutrition - n_min) / (n_max - n_min), 0, 1)
    return exp(-c - n)


def make_figure_5():
    inputs = load_inputs("fig5_retained_analysis")
    city = inputs.city_carbon_and_nutrition_burdens
    weights = normalize(inputs.city_order_weights)
    bounds = pooled_min_max(city, fields=["carbon", "dri", "nutriscore"])
    national_raw = weighted_mean(city, weights, by="system")

    # Normalize both systems with the same fixed bounds
    for metric in ["dri", "nutriscore"]:
        city["cnei_" + metric] = calculate_cnei(
            city.carbon, city[metric], bounds.carbon, bounds[metric]
        )
        national_raw["cnei_" + metric] = calculate_cnei(
            national_raw.carbon, national_raw[metric],
            bounds.carbon, bounds[metric],
        )

    fig, ax = create_panels("abcdefghi", rows=3, columns=3)

    # a–c: National indices and paired city distributions
    plot_two_index_system_bars(ax["a"], national_raw)
    for panel, metric in [("b", "dri"), ("c", "nutriscore")]:
        plot_paired_violins_and_city_points(
            ax[panel], city, value="cnei_" + metric,
            national_diamonds=national_raw, show_median_and_iqr=True,
        )

    # d–i: Descriptive quadratic fits and fitted-mean confidence bands
    predictors = ["income", "urbanization", "annual_orders_per_resident"]
    ofd = select_system(city, "OFD").join(inputs.city_context)
    for panels, metric in [("def", "dri"), ("ghi", "nutriscore")]:
        for panel, predictor in zip(panels, predictors):
            data = drop_missing(ofd, [predictor, "cnei_" + metric])
            fit = fit_quadratic_ols(data, x=predictor, y="cnei_" + metric)
            grid = prediction_grid(data[predictor])
            curve, lower, upper = fitted_mean_confidence_band(fit, grid, level=0.95)
            plot_city_scatter(ax[panel], data, color="region", labels="pinyin")
            plot_curve_and_band(ax[panel], grid, curve, lower, upper)
            annotate_spearman(ax[panel], data[predictor], data["cnei_" + metric])

    save_normalization_bounds(bounds, "fixed_bounds_for_fig6")
    format_panels(fig, panel_labels=True, higher_cnei_is_better=True)
    export_figure(fig, "Fig5", formats=["pdf", "svg", "png"])
