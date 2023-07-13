import sys, webbrowser
from dash import Dash, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

local_stylesheet = {
    "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
    "rel": "stylesheet"
}

app = Dash(__name__, title="SearchMS", suppress_callback_exceptions=True,
    external_stylesheets=[local_stylesheet, dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

def serve_layout():

    return html.Div([
        
    ])

if __name__ == "__main__":
    
    if sys.platform == "win32":
        chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome_path))
        webbrowser.get("chrome").open("http://127.0.0.1:8050/")
    elif sys.platform == "darwin":
        webbrowser.get("chrome").open("http://127.0.0.1:8050/", new=1)
        
    app.run(debug=True)