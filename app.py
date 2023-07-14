import sys, webbrowser, ast

from dash import Dash, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import matchms
from plots import *

local_stylesheet = {
    "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
    "rel": "stylesheet"
}

app = Dash(__name__, title="SearchMS", suppress_callback_exceptions=True,
    external_stylesheets=[local_stylesheet, dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

def serve_layout():

    return html.Div([
        
        # Navigation bar
        dbc.Navbar(color="dark", dark=True, children=[
            dbc.Container(style={"height": "50px"}, children=[
                html.A(
                    dbc.Row([
                        dbc.Col(align="center", className="g-0", children=[
                            dbc.NavbarBrand(id="header", children="SearchMS", className="ms-2")
                        ])
                    ]), href="https://localhost:8050", style={"textDecoration": "none"}
                )
            ])
        ]),
        
        # App layout
        html.Div(className="app-layout", children=[
            dbc.Row(justify="center", children=[
                
                # Panel for search input
                dbc.Col(width=4, children=[
                    
                    # Input group for loading mass spectrum
                    html.Div([
                        dbc.Label("Mass spectrum (.msp, .json, .mgf)"),
                        dbc.InputGroup([
                            dbc.Textarea(rows=5, id="mass-spectrum-input", placeholder="Enter your mass spectrum here"),
                            dbc.FormFeedback("Looks good!", type="valid"),
                            dbc.FormFeedback("Please ensure the peak table of your mass spectrum is in one of the accepted formats.", type="invalid"),
                        ]),
                    ]), html.Br(),
                    
                    # Input group for loading reference library
                    html.Div([
                        dbc.Label("Load mass spectral reference library (.msp, .json, .mgf)"),
                        dbc.InputGroup([
                            dbc.Input(id="reference-library", placeholder="No file selected"),
                            dbc.Button(dcc.Upload(
                                id="load-reference-library-button",
                                accept="text/plain, .msp",
                                children=[html.A("Browse Files")]),
                                color="secondary"),
                            dbc.FormFeedback("Looks good!", type="valid"),
                            dbc.FormFeedback("Please ensure your spectral library is in one of the accepted formats.", type="invalid"),
                        ]),
                    ]), html.Br(),
                    
                    html.H6("or", style={"text-align": "center"}),
                    
                    # Input group for choosing a mass spectrometry database
                    html.Div([
                        dbc.Label("Search against public databases"),
                        dbc.Select(id="reference-database", placeholder="Choose public database...", options=[
                            {"label": "", "value": ""},
                            {"label": "GNPS", "value": "GNPS"},
                            {"label": "MONA", "value": "MONA"},
                            {"label": "MassBank", "value": "MassBank"},
                            {"label": "Berkeley Lab", "value": "Berkeley Lab"},
                            {"label": "CASMI", "value": "CASMI"}
                        ]),
                        dbc.FormFeedback("Looks good!", type="valid")
                    ]), html.Br(),
                    
                    # Plot for user-inputted mass spectrum
                    html.Div(className="plot-container", children=[
                        dcc.Graph(id="experimental-spectrum"),
                    ])
                ]),
                
                # Panel for search results
                dbc.Col(width=8, children=[
                    
                ])
            ])
        ])
    ])

app.layout = serve_layout

@app.callback(Output("experimental-spectrum", "figure"),
              Input("mass-spectrum-input", "value"), prevent_initial_call=True)
def render_user_inputted_spectrum(peak_data):
    
    """
    Renders plot for user-inputted mass spectrum.
    """
    
    # Convert string into object
    mass_spectrum = ast.literal_eval(peak_data)
    
    # Initialize DataFrame
    df_peaks = pd.DataFrame(np.array(mass_spectrum), columns=["m/z", "intensity"])
    
    # Render plot
    return render_mass_spectrum(df_peaks)


if __name__ == "__main__":
    
    # if sys.platform == "win32":
    #     chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    #     webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_path))
    #     webbrowser.get("chrome").open("http://localhost:8050/")
    # elif sys.platform == "darwin":
    #     webbrowser.get("chrome").open("http://localhost:8050/", new=1)
        
    app.run(debug=True)