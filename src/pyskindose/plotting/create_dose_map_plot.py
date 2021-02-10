import numpy as np
import plotly.graph_objects as go


from pyskindose import constants as c
from pyskindose.phantom_class import Phantom
from pyskindose.settings_pyskindose import PyskindoseSettings

from ..constants import (
    DOSEMAP_COLORSCALE,
    PLOT_ASPECTMODE_PLOT_DOSEMAP,
    PLOT_EYE_BACK,
    PLOT_EYE_FRONT,
    PLOT_EYE_LEFT,
    PLOT_EYE_RIGHT,
    PLOT_FONT_FAMILY,
    PLOT_FONT_SIZE,
    PLOT_HOVERLABEL_FONT_FAMILY,
    PLOT_HOVERLABEL_FONT_SIZE,
)

from .plot_settings import (
    fetch_plot_colors,
    fetch_plot_margin,
    fetch_plot_size
    )


def create_dose_map_plot(
        patient: Phantom,
        settings: PyskindoseSettings,
        dose_map: np.ndarray) -> None:
    """Plot a map of the absorbed skindose upon the patient phantom.

    This function creates and plots an offline plotly graph of the
    skin dose distribution on the phantom. The colorscale is mapped to the
    absorbed skin dose value. Only available for phantom type: "plane",
    "cylinder" or "human"

    Parameters
    ----------
    patient : Phantom
        patient phantom
    settings : PyskindoseSettings
        Settings class for PySkinDose
    dose_map : np.ndarray
        array with dose matrix, where each element is to be mapped to the 
        corresponding skin cell of the patient.
    interactivity : bool
        Toggle for interactive mode when plotting dosemaps. If True,
        the dosemap will be plotted in a .html file with full interactivity.
        If False, the dosemap will be saved as static images. Static mode is
        provided to enable PySkinDose to run smooth on machines with limited
        RAM.

    """
    # Fix error with plotly layout for 2D plane patient.
    if patient.phantom_model == c.PHANTOM_MODEL_PLANE:
        patient = Phantom(
            phantom_model=settings.phantom.model, phantom_dim=settings.phantom.dimension
        )

    # append dosemap to patient
    patient.dose = dose_map

    COLOR_CANVAS, COLOR_PLOT_TEXT, COLOR_GRID, COLOR_ZERO_LINE = \
        fetch_plot_colors(dark_mode=settings.plot.dark_mode)

    PLOT_HEIGHT, PLOT_WIDTH = fetch_plot_size(notebook_mode=settings.plot.notebook_mode)

    PLOT_MARGINS = fetch_plot_margin(notebook_mode=settings.plot.notebook_mode)

    lat_text = [f"<b>lat:</b> {np.around(patient.r[ind, 2],2)} cm<br>"
                for ind in range(len(patient.r))]

    lon_text = [f"<b>lon:</b> {np.around(patient.r[ind, 0],2)} cm<br>"
                for ind in range(len(patient.r))]

    ver_text = [f"<b>ver:</b> {np.around(patient.r[ind, 1],2)} cm<br>"
                for ind in range(len(patient.r))]

    dose_text = [f"<b>skin dose:</b> {round(patient.dose[ind],2)} mGy"
                    for ind in range(len(patient.r))]

    hover_text = [lat_text[cell] + lon_text[cell] + ver_text[cell] +
                    dose_text[cell] for cell in range(len(patient.r))]

    # create mesh object for the phantom
    phantom_mesh = [
        go.Mesh3d(
            x=patient.r[:, 0], y=patient.r[:, 1], z=patient.r[:, 2],
            i=patient.ijk[:, 0], j=patient.ijk[:, 1], k=patient.ijk[:, 2],
            intensity=patient.dose, colorscale=DOSEMAP_COLORSCALE,
            showscale=True,
            hoverinfo='text',
            text=hover_text, name="Human",
            colorbar=dict(tickfont=dict(color=COLOR_PLOT_TEXT),
                            title="Skin dose [mGy]",
                            titlefont=dict(
                                family=PLOT_FONT_FAMILY,
                                color=COLOR_PLOT_TEXT)))]

    # Layout settings
    layout = go.Layout(
        height=PLOT_HEIGHT,
        width=PLOT_WIDTH,
        margin=PLOT_MARGINS,

        font=dict(
            family=PLOT_FONT_FAMILY,
            color=COLOR_PLOT_TEXT,
            size=PLOT_FONT_SIZE),

        hoverlabel=dict(
            font=dict(
                family=PLOT_HOVERLABEL_FONT_FAMILY,
                size=PLOT_HOVERLABEL_FONT_SIZE)),

        titlefont=dict(
            family=PLOT_FONT_FAMILY,
            size=PLOT_FONT_SIZE,
            color=COLOR_PLOT_TEXT),

        paper_bgcolor=COLOR_CANVAS,

        scene=dict(
            aspectmode=PLOT_ASPECTMODE_PLOT_DOSEMAP,
            xaxis=dict(
                title='',
                backgroundcolor=COLOR_CANVAS,
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                ),

            yaxis=dict(
                title='',
                backgroundcolor=COLOR_CANVAS,
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                ),

            zaxis=dict(
                title='',
                backgroundcolor=COLOR_CANVAS,
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                ),
                )
        )

    # create figure
    fig = go.Figure(data=phantom_mesh, layout=layout)
    fig.show()