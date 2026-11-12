"""Fig. 3 — Meal nutrition and culinary recipe profiles."""


def make_figure_3():
    inputs = load_inputs("fig3")
    nutrients = inputs.city_nutrients_per_person_meal
    references = inputs.one_meal_dietary_references
    weights = normalize(inputs.city_consumption_weights)
    fig, ax = create_panels("abcde", layout="nutrition_and_radar_profiles")

    # a: Nutrient positions relative to dietary references
    national_nutrients = weighted_mean(nutrients, weights, by="system")
    positions = nutrient_reference_positions(national_nutrients, references)
    plot_nutrient_positions(ax["a"], positions, reference_bands=references)

    # b: Nutrient density per 1,000 kcal
    density = nutrients_per_1000_kcal(national_nutrients)
    density_ratio = density["OFD"] / density["Household"]
    plot_density_ratios(ax["b"], density_ratio, parity_line=1)

    # c: Mean absolute dietary-reference deviation
    deviation = percent_distance_outside_reference(
        nutrients, references,
        rules={"range": "either side", "upper_limit": "excess",
               "minimum": "shortfall"},
    )
    city_deviation = mean_across_seven_nutrients(deviation)
    plot_paired_city_points(ax["c"], city_deviation)
    add_weighted_mean_diamonds(ax["c"], city_deviation, weights)

    # d: Food-category Nutri-Score from the separate culinary references
    recipes = inputs.culinary_recipe_nutrient_profiles
    scores = apply_nutriscore_2023(recipes, separate_food_and_beverage_rules=True)
    food_scores = select_assessable_general_food_records(scores)
    summary = equal_record_mean_and_iqr(food_scores, group="food_category")
    plot_category_mean_iqr(ax["d"], summary)
    add_vertical_benchmarks(ax["d"], inputs.panel_d_system_benchmarks)

    # e: Recipe-format profiles at a common food mass
    profiles = standardize_recipe_mass(recipes, inputs.common_reference_mass_g)
    profiles = equal_record_mean(profiles, by="meal_format")
    plot_small_multiple_radars(
        ax["e"], profiles, references=references,
        overall_ofd=inputs.panel_e_overall_reference,
        labels=recipe_record_shares(recipes),
    )

    format_panels(fig, panel_labels=True, consistent_system_colors=True)
    export_figure(fig, "Fig3", formats=["pdf", "svg", "png"])
