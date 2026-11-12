"""Fig. 2 — Food baskets, ingredient flows and product formats."""


def make_figure_2():
    inputs = load_inputs("fig2")
    city_weights = normalize(inputs.city_consumption_weights)
    ofd_mass = inputs.ofd_g_per_order / inputs.co_diners_per_order
    household_mass = inputs.household_g_per_capita_day / (
        3 * inputs.home_prepared_meal_fraction
    )

    # Ingredient–format mass allocation
    products = inputs.menu_products
    products.weights = reweight_sales_within_city_category(
        products, inputs.city_category_consumption_shares
    )
    products.format = predict_12_formats_with_bert_ensemble(products)
    products.format = split_fresh_fruit_within_side_dishes(products)
    format_margins = estimate_format_masses(products, inputs.recipe_profiles)
    matrix = initialize_ingredient_format_matrix(inputs.recipe_profiles, products)
    matrix = iterative_proportional_fitting(
        matrix, row_totals=inputs.ingredient_g_per_order,
        column_totals=format_margins,
        structural_zeros="non-fruit ingredients in the fresh-fruit format",
    )
    flow_per_meal = matrix / inputs.co_diners_per_order
    format_mass = sum_over_ingredients(flow_per_meal)
    fig, ax = create_panels("abcd", layout="food_basket_and_flows")

    # a–b: City food mass and mean ingredient composition
    plot_city_distributions(ax["a"], household_mass, ofd_mass)
    add_weighted_mean_diamonds(ax["a"], household_mass, ofd_mass, city_weights)
    ingredients = weighted_mean_ingredient_profiles(
        household_mass, ofd_mass, inputs.ingredient_profiles, city_weights
    )
    plot_paired_ingredient_bars(ax["b"], ingredients, difference_label_min_g=10)

    # c–d: Ingredient flows and 13-format food-mass contributions
    plot_alluvial(ax["c"], flow_per_meal, ribbon_width="ingredient mass")
    plot_ranked_bars_and_donut(
        ax["d"], format_mass, shares=format_mass / sum(format_mass)
    )
    format_panels(fig, panel_labels=True, mass_unit="g per person-meal")
    export_figure(fig, "Fig2", formats=["pdf", "svg", "png"])
