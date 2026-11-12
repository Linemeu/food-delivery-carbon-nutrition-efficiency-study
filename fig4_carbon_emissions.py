"""Fig. 4 — Carbon components and emission shifts."""


def make_figure_4():
    inputs = load_inputs("fig4")
    weights = normalize(inputs.city_consumption_weights)
    factors = inputs.emission_factors
    activity = inputs.activity_per_actual_person_meal
    components = empty_component_table()

    # Seven components, using consistent person-meal boundaries
    for system in ["Household", "OFD"]:
        a = activity[system]
        components[system] = {
            "Food production": sum_food_groups(a.food_kg * factors.production),
            "Postharvest": sum_food_groups(a.food_kg * factors.postharvest),
            "Cooking": a.total_food_kg * a.cooking_kgCO2e_per_kg,
            "Waste treatment": sum_treatments(a.waste_kg * factors.treatment),
            "Packaging": a.packaging_proxy_kgCO2e,
            "Transport": a.delivery_or_procurement_kgCO2e,
            "Platform": a.platform_kgCO2e if system == "OFD" else 0,
        }

    city_total = sum_components(components)
    national = weighted_mean(components, weights, by="system")
    shift = national["OFD"] - national["Household"]
    fig, ax = create_panels("abcde", layout="ab/cc/de")

    # a–c: OFD decomposition, city ranking and component variation
    plot_stacked_components(ax["a"], national["OFD"])
    plot_ranked_city_bars(
        ax["b"], sort_descending(city_total["OFD"]),
        mean_line=sum(national["OFD"]),
    )
    component_order = rank_components_by_mean(national["OFD"])
    plot_component_boxplots_with_city_points(
        ax["c"], components["OFD"], order=component_order,
        mean_labels=national["OFD"],
    )

    # d–e: System comparison and OFD-minus-household shifts
    plot_system_stacked_bars(ax["d"], national)
    annotate_ratio(ax["d"], sum(national["OFD"]) / sum(national["Household"]))
    plot_diverging_component_bars(ax["e"], shift, zero_line=True)

    format_panels(fig, panel_labels=True, carbon_unit="kg CO2e per person-meal")
    export_figure(fig, "Fig4", formats=["pdf", "svg", "png"])
