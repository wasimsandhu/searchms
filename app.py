import sys, webbrowser, time, json, ast
from plots import *

from dash import Dash, html, dcc, Output, Input, State, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import matchms as ms

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
                    
                    # Plot for user-inputted mass spectrum
                    html.Div(id="plot-container", className="plot-container", style={"display": "none"}, children=[
                        dcc.Graph(id="experimental-spectrum")
                    ]),
                    
                    # Input group for loading reference library
                    html.Div([
                        dbc.Label("Molecule name (optional)"),
                        dbc.InputGroup([
                            dbc.Input(id="molecule-name", placeholder="Enter molecule name, if known"),
                            dbc.FormFeedback("Looks good!", type="valid")
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
                    
                    html.Div(className="d-grid gap-2", children=[
                        dbc.Button("Search", id="search-button", color="primary")
                    ]),
                ]),
                
                # Panel for search results
                dbc.Col(width=8, children=[
                    html.Div(id="results-container", className="results-container", children=[
                        # Dynamically populated with search results...
                    ])
                ])
            ])
        ]),
        
        # Modals
        dbc.Modal(id="loading-modal", size="md", centered=True, is_open=False, scrollable=True, keyboard=False, backdrop="static", children=[
            dbc.ModalHeader(close_button=False, children=[
                dbc.ModalTitle(html.Div([
                    html.Div(children=[dbc.Spinner(color="primary"), " Searching..."])
                ]))
            ]),
            dbc.ModalBody("This process may take 30-60 seconds. Please wait...", id="loading-modal-body")
        ]),
        
        # Data
        dcc.Store(id="search-started"),
        dcc.Store(id="search-complete"),
        dcc.Store(id="search-results"),
        dcc.Store(id="test")
    ])

app.config.suppress_callback_exceptions = True
app.layout = serve_layout

@app.callback(Output("experimental-spectrum", "figure"),
              Output("plot-container", "style"),
              Input("mass-spectrum-input", "value"), prevent_initial_call=True)
def render_user_inputted_spectrum(peak_data):
    
    """
    Renders plot for user-inputted mass spectrum
    """
    
    try:
        # Convert string into object
        mass_spectrum = ast.literal_eval(peak_data)
        
        # Initialize DataFrame
        df_peaks = pd.DataFrame(np.array(mass_spectrum), columns=["m/z", "intensity"])
        
        # Render plot
        return render_mass_spectrum(df_peaks), {"display": "block"}
    
    except:
        return None, {"display": "none"}


@app.callback(Output("search-started", "data"),
              Input("search-button", "n_clicks"),
              Input("loading-modal", "is_open"), prevent_initial_call=True, suppress_callback_exceptions=True)
def flag_search_started(button_click, test):
    
    return True


@app.callback(Output("loading-modal", "is_open"),
              Input("search-started", "data"),
              Input("search-complete", "data"), prevent_initial_call=True, suppress_callback_exceptions=True)
def toggle_loading_modal(search_started, search_complete):
    
    trigger = ctx.triggered_id
    
    if trigger == "search-started":
        return True
    elif trigger == "search-complete":
        return False


@app.callback(Output("results-container", "children"),
              Input("search-started", "data"), prevent_initial_call=True)
def search_libraries(search_started):
    
    """
    Performs library search to generate ranked list of spectral matches
    """
    
    # Load spectral library
    library = ms.importing.load_from_json("libraries/reference_library.json")
    
    # Apply filters to clean and enhance each spectrum
    spectra = []
    for spectrum in library:
        spectrum = ms.filtering.default_filters(spectrum)
        spectrum = ms.filtering.normalize_intensities(spectrum)
        spectra.append(spectrum)
        
    scores = ms.calculate_scores(
        references=spectra, 
        queries=spectra, 
        similarity_function=ms.similarity.CosineGreedy()
    )

    # Query library for user-inputted spectrum
    query = spectra[15]
    best_matches = scores.scores_by_query(query, 'CosineGreedy_score', sort=True)
    
    results = []
    
    for x in range(0, 10):
        
        result = dbc.Card(className="mb-3", children=[
            dbc.CardBody([
                "Molecule " + str(x)
            ]),
        ])
        
        results.append(result)
    
    time.sleep(5)
    return results


@app.callback(Output("search-complete", "data"),
              Input("results-container", "children"), prevent_initial_call=True)
def flag_search_complete(results):
    
    return True


if __name__ == "__main__":
    
    # if sys.platform == "win32":
    #     chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    #     webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_path))
    #     webbrowser.get("chrome").open("http://localhost:8050/")
    # elif sys.platform == "darwin":
    #     webbrowser.get("chrome").open("http://localhost:8050/", new=1)
        
    app.run(debug=True)