"""Fig. 6 — Order growth and carbon–nutrition pathways."""


def make_figure_6():
    inputs = load_inputs("fig6_retained_baseline_and_scenarios")
    history = inputs.historical_orders_and_frequencies
    years = inputs.projection_years

    # Order projection: population × urbanization × ordering frequency
    K, r, t0 = fit_bounded_logistic(history.year, history.orders_per_urban_resident)
    frequency = K / (1 + exp(-r * (years - t0)))
    population, urbanization = anchor_demographic_projections(inputs.demographics)
    orders = population * urbanization * frequency

    # Carbon interventions change only their specified components
    baseline = inputs.retained_ofd_baseline
    component_changes = intervention_endpoint_minus_baseline(
        inputs.interventions,
        components=["cooking", "waste", "packaging", "delivery"],
    )
    carbon_endpoints = single_and_integrated_carbon_endpoints(
        baseline.carbon, component_changes, combine="additive"
    )
    score_endpoint = guided_choice_within_format_weighted_quartiles(
        inputs.product_scores, inputs.choice_shift_settings,
        anchor=baseline.nutriscore,
    )
    endpoints = build_carbon_nutrition_scenarios(
        baseline, carbon_endpoints,
        nutrition_targets={"dri": 0, "nutriscore": score_endpoint},
        pathways=["BAU", "carbon_only", "nutrition_only", "joint"],
    )

    # Linear phase-in; convert person-meal footprints to annual emissions
    phase = clip((years - inputs.start_year) / (inputs.end_year - inputs.start_year), 0, 1)
    trajectories = empty_scenario_table()
    for scenario, endpoint in endpoints.items():
        carbon = baseline.carbon + phase * (endpoint.carbon - baseline.carbon)
        dri = baseline.dri + phase * (endpoint.dri - baseline.dri)
        score = baseline.nutriscore + phase * (endpoint.nutriscore - baseline.nutriscore)
        annual_Mt = orders * inputs.co_diners_per_order * carbon / 1e9
        trajectories[scenario] = table(years, carbon, dri, score, annual_Mt)
    savings = trajectories["BAU"].annual_Mt - trajectories.annual_Mt

    # a–c: Order growth, emission pathways and endpoint-year savings
    fig, ax = create_panels("abcde", layout="ab/cc/de")
    plot_historical_and_projected_orders(ax["a"], history, years, orders)
    plot_carbon_scenario_lines(ax["b"], trajectories)
    shade_avoided_emissions(ax["b"], trajectories["BAU"], trajectories["integrated_carbon"])
    plot_intervention_savings(ax["c"], select_year(savings, inputs.end_year))

    # d–e: Carbon versus the two separate nutrition burdens
    for panel, metric in [("d", "dri"), ("e", "nutriscore")]:
        plot_carbon_nutrition_endpoints(
            ax[panel], endpoints, x="carbon", y=metric,
            household_benchmark=inputs.retained_household_benchmark,
            show_pathway_arrows=True,
        )

    format_panels(fig, panel_labels=True, consistent_scenario_colors=True)
    export_figure(fig, "Fig6", formats=["pdf", "svg", "png"])
