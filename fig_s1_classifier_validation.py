"""Fig. S1 — Internal product-format classifier validation ."""


def make_figure_s1():
    inputs = load_inputs("fig_s1_internal_test_predictions")
    labels = inputs.original_12_format_labels

    # Ensemble weights are selected on the development set
    probabilities = (
        inputs.title_weight * inputs.title_model_probabilities
        + inputs.multifield_weight * inputs.multifield_model_probabilities
    )
    predicted = labels[argmax(probabilities, axis="class")]
    counts = confusion_matrix(inputs.reference_labels, predicted, labels=labels)
    row_percent = 100 * counts / row_sum(counts, keepdims=True)
    accuracy = classification_accuracy(inputs.reference_labels, predicted)
    macro_f1 = mean_class_f1(inputs.reference_labels, predicted, labels=labels)

    # Counts in cells; shading shows within-reference-format percentages
    fig, ax = create_single_panel()
    plot_heatmap(ax, row_percent, cell_labels=counts, color_limits=(0, 100))
    set_axis_labels(ax, x="Predicted format", y="Reference format", ticks=labels)
    annotate_metrics(ax, accuracy=accuracy, macro_f1=macro_f1)
    export_figure(fig, "FigS1", formats=["pdf", "svg", "png"])
