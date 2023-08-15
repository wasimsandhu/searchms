import sys, webbrowser, ast, requests
from plots import *

from dash import Dash, html, dcc, Output, Input, State, ctx
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
                        dbc.Label("Enter mass spectrum (.msp, .json, .mgf)"),
                        dbc.InputGroup([
                            dbc.Textarea(rows=5, id="mass-spectrum-input", placeholder="Enter your mass spectrum here"),
                            dbc.FormFeedback("Looks good!", type="valid"),
                            dbc.FormFeedback("Please ensure the peak table of your mass spectrum is in one of the accepted formats.", type="invalid"),
                            dbc.Tooltip("Please enter the text string representing the mass spectrum you'd like to search against the database.", target="mass-spectrum-input"),
                        ]),
                    ]), html.Br(),
                    
                    # Plot for user-inputted mass spectrum
                    html.Div(id="plot-container", className="plot-container", style={"display": "none"}, children=[
                        dcc.Graph(id="experimental-spectrum")
                    ]),
                    
                    # Input group for loading reference library
                    # html.Div([
                    #     dbc.Label("Molecule name (optional)"),
                    #     dbc.InputGroup([
                    #         dbc.Input(id="molecule-name", placeholder="Enter molecule name, if known"),
                    #         dbc.FormFeedback("Looks good!", type="valid")
                    #     ]),
                    # ]), html.Br(),
                    
                    # Input group for loading reference library
                    html.Div([
                        dbc.Label("Load mass spectral reference library (.msp, .json, .mgf)"),
                        dbc.InputGroup([
                            dbc.Input(id="reference-library", placeholder="No file selected"),
                            dbc.Button(dcc.Upload(
                                id="load-reference-library-button",
                                accept="text/plain, .msp, .json, .mgf",
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
                            {"label": "GNPS", "value": "GNPS"},
                            {"label": "MONA", "value": "MONA"},
                            {"label": "MassBank", "value": "MassBank"},
                            {"label": "Berkeley Lab", "value": "Berkeley Lab"},
                            {"label": "CASMI", "value": "CASMI"}
                        ]),
                        dbc.FormFeedback("Looks good!", type="valid")
                    ]), html.Br(),
                    
                    html.Div(className="d-grid gap-2", children=[
                        dbc.Button("Search", id="search-button", disabled=True, color="primary")
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
            dbc.ModalBody("This process may a few seconds. Please wait...", id="loading-modal-body")
        ]),
        
        # Data
        dcc.Store(id="search-started"),
        dcc.Store(id="search-complete"),
        dcc.Store(id="search-results")
    ])

app.config.suppress_callback_exceptions = True
app.layout = serve_layout

@app.callback(Output("reference-database", "valid"),
              Input("reference-database", "value"), prevent_initial_call=True)
def database_dropdown_validation(reference_database):
    
    """
    Validates selected database
    """
    
    if reference_database is not None:
        return True
    else:
        return False


@app.callback(Output("search-button", "disabled"),
              Input("mass-spectrum-input", "valid"),
              Input("reference-database", "valid"), prevent_initial_call=True)
def validate_user_input(mass_spectrum_valid, reference_database_valid):
    
    """
    Enables search button if mass spectrum and reference library are valid
    """
    
    if mass_spectrum_valid and reference_database_valid:
        return False
    else:
        return True


@app.callback(Output("experimental-spectrum", "figure"),
              Output("plot-container", "style"),
              Output("mass-spectrum-input", "valid"),
              Output("mass-spectrum-input", "invalid"),
              Input("mass-spectrum-input", "value"), prevent_initial_call=True)
def render_user_inputted_spectrum(peak_data):
    
    """
    Renders plot for user-inputted mass spectrum
    """
    
    # Sample spectrum
    # [[67.142, 7.869], [79.134, 5.553], [91.056, 5.578], [105.039, 22.809], [115.033, 75.299], [116.993, 45.418], [130.149, 7.47], [131.984, 47.809], [133.085, 11.454], [142.064, 21.414], [143.274, 9.163], [159.734, 100.0]]
    
    try:
        # Convert string into object
        mass_spectrum = ast.literal_eval(peak_data)
        
        # Initialize DataFrame
        df_peaks = pd.DataFrame(np.array(mass_spectrum), columns=["m/z", "intensity"])
        
        # Render plot
        return render_mass_spectrum(df_peaks), {"display": "block"}, True, False
    
    except:
        return None, {"display": "none"}, False, True


@app.callback(Output("search-started", "data"),
              Input("search-button", "n_clicks"),
              Input("loading-modal", "is_open"), prevent_initial_call=True, suppress_callback_exceptions=True)
def flag_search_started(button_click, modal_is_open):
    
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
              Input("search-started", "data"), 
              State("mass-spectrum-input", "value"), prevent_initial_call=True)
def search_libraries(search_started, peak_data):
    
    """
    Searches user-inputted spectrum against library / database to generate ranked list of spectral matches
    """
    
    # Sample spectrum
    # [[67.142, 7.869], [79.134, 5.553], [91.056, 5.578], [105.039, 22.809], [115.033, 75.299], [116.993, 45.418], [130.149, 7.47], [131.984, 47.809], [133.085, 11.454], [142.064, 21.414], [143.274, 9.163], [159.734, 100.0]]
    
    # Load mass spectrum
    peak_data = ast.literal_eval(peak_data)
    
    experimental_spectrum = ms.Spectrum(
        mz=np.array(peak_data)[:, 0],
        intensities=np.array(peak_data)[:, 1],
        metadata={}
    )
    
    mz_range = [experimental_spectrum.mz.min() - 10, experimental_spectrum.mz.max() + 10]
    
    # Load spectral library
    library = ms.importing.load_from_json("libraries/reference_library.json")
    
    # Apply filters to clean and enhance each spectrum
    reference_spectra = []
    for spectrum in library:
        spectrum = ms.filtering.default_filters(spectrum)
        spectrum = ms.filtering.normalize_intensities(spectrum)
        reference_spectra.append(spectrum)
    
    # Calculate similarity scores against library
    scores = ms.calculate_scores(
        references=reference_spectra,
        queries=[experimental_spectrum],
        similarity_function=ms.similarity.CosineGreedy()
    )

    # Query library for user-inputted spectrum
    best_matches = scores.scores_by_query(experimental_spectrum, 'CosineGreedy_score', sort=True)[0:15]
    results = []

    for (reference, score) in best_matches:
        df_peaks = pd.DataFrame({"m/z": reference.peaks.mz, "intensity": reference.peaks.intensities})
        
        try:
            # CS 361 microservice: Query PubChem for molecule information
            compound_name = reference.metadata["compound_name"]
            molecule_data = requests.get(f"http://127.0.0.1:3000/query/{compound_name}").json()
            
            result = dbc.Card(className="mb-3", children=[
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(width=4, children=[
                            html.H3(compound_name),
                            html.H4(f"Similarity score: {score[0]:.4f}"),
                            html.P(molecule_data["description"]),
                        ]),
                        dbc.Col(width=8, children=[
                            dcc.Graph(figure=render_mass_spectrum(df_peaks, title="Reference Spectrum", range=mz_range))
                        ]),
                    ]),
                    dbc.Row([
                        dbc.Accordion(start_collapsed=True, children=[
                            dbc.AccordionItem(title="Metadata", children=[
                                dbc.ListGroup([
                                    dbc.ListGroupItem(f'Molecular formula: {molecule_data["molecular_formula"]}'),
                                    dbc.ListGroupItem(f'Molecular weight: {molecule_data["molecular_weight"]}'),
                                    dbc.ListGroupItem(f'Monoisotopic mass: {molecule_data["monoisotopic_mass"]}'),
                                    dbc.ListGroupItem(f'Precursor mass: {reference.metadata["precursor_mz"]}'),
                                    dbc.ListGroupItem(f'INCHIKEY: {reference.metadata["precursor_mz"]}'),
                                    dbc.ListGroupItem(f'Charge: {molecule_data["inchikey"]}'),
                                    dbc.ListGroupItem(f'Ion mode: {reference.metadata["ionmode"]}'),
                                    dbc.ListGroupItem(f'Instrument: {reference.metadata["instrument"]}'),
                                ])
                            ])
                        ])
                    ])
                ]),
            ])
            results.append(result)
            
        except Exception as error:
            print(error)
    
    return results


@app.callback(Output("search-complete", "data"),
              Input("results-container", "children"), prevent_initial_call=True)
def flag_search_complete(results):
    
    return True


if __name__ == "__main__":
    
    if sys.platform == "win32":
        chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_path))
        webbrowser.get("chrome").open("http://localhost:8050/")
    elif sys.platform == "darwin":
        webbrowser.get("chrome").open("http://localhost:8050/", new=1)
        
    app.run(debug=False)