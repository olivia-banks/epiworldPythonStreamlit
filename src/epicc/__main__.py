import streamlit as st
from pydantic import ValidationError

from epicc.model.base import BaseSimulationModel
from epicc.model.models import get_all_models
from epicc.ui.export import (
    render_parameter_export_inline,
    render_pdf_export_button,
    trigger_print_if_requested,
)
from epicc.ui.parameters import (
    build_typed_params,
    render_sidebar_parameters,
    render_validation_error,
)
from epicc.ui.report import get_report_renderer
from epicc.ui.state import (
    has_results,
    get_run_output,
    initialize_state,
    set_run_output,
    sync_active_model,
)
from epicc.ui.styles import load_styles

# ---------------------------------------------------------------------------
# One-time setup  (set_page_config MUST be the first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(page_title="epicc Cost Calculator", layout="wide")
load_styles()
initialize_state()

# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

all_models = get_all_models()
model_registry: dict[str, BaseSimulationModel] = {m.human_name(): m for m in all_models}

# ---------------------------------------------------------------------------
# Header row: title | model selector
# ---------------------------------------------------------------------------

hdr_title, hdr_model = st.columns([3, 3])
hdr_title.title("epicc Cost Calculator")
selected_label: str = hdr_model.selectbox(  # type: ignore[assignment]
    "Model",
    list(model_registry),
    index=0,
    label_visibility="collapsed",
)
active_model = model_registry[selected_label]
params = sync_active_model(selected_label)

st.divider()

# ---------------------------------------------------------------------------
# Two-column layout: parameters (left) | results (right)
# ---------------------------------------------------------------------------

param_col, result_col = st.columns([2, 3], gap="large")

# ---------------------------------------------------------------------------
# Parameters panel
# ---------------------------------------------------------------------------

with param_col:
    params, label_overrides, model_defaults_flat, has_input_errors = render_sidebar_parameters(
        active_model, selected_label, params, container=param_col
    )

    typed_params = None
    if not has_input_errors:
        try:
            typed_params = build_typed_params(active_model, model_defaults_flat, params)
        except ValidationError as exc:
            render_validation_error(selected_label, exc, container=param_col)
            has_input_errors = True

    if typed_params is not None:
        render_parameter_export_inline(
            active_model.human_name(),
            typed_params.model_dump(),
            pydantic_model=type(typed_params),
            container=param_col,
        )

    st.divider()
    run_clicked = st.button(
        "Run Simulation", disabled=has_input_errors, use_container_width=True
    )

# ---------------------------------------------------------------------------
# Results panel
# ---------------------------------------------------------------------------

with result_col:
    trigger_print_if_requested()

    if typed_params is None:
        st.warning("Fix parameter errors to enable simulation.")
        st.stop()

    # -----------------------------------------------------------------------
    # Run
    # -----------------------------------------------------------------------

    if run_clicked:
        with st.spinner(f"Running {selected_label}..."):
            run_output = active_model.run(typed_params, label_overrides=label_overrides)
        set_run_output(run_output)
        st.rerun()

    # -----------------------------------------------------------------------
    # Render report
    # -----------------------------------------------------------------------

    renderer = get_report_renderer(active_model)
    _HINT = "This report has not been filled, since your simulation has not been run. Run the simulation to see the results here."

    if has_results():
        renderer.render(get_run_output())
    else:
        renderer.render(None, hint=_HINT)

    st.divider()
    render_pdf_export_button(container=result_col)

