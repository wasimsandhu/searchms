import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def render_mass_spectrum(df_peaks):
    
    """
    Renders plot of mass spectrum.
    
    Args:
        df_peaks (pd.DataFrame): User-provided peak table
    
    Returns:
        plotly.Figure: Mass spectrum
    """
    
    min_mz = df_peaks["m/z"].min() - 10
    max_mz = df_peaks["m/z"].max() + 10
    
    plot = px.bar(df_peaks, title="Experimental Spectrum", x="m/z", y="intensity", height=400)
    plot.update_layout(showlegend=False, transition_duration=500, clickmode="event", margin=dict(t=75, b=75, l=0, r=0))
    plot.update_xaxes(title="", range=[min_mz, max_mz], side="bottom")
    plot.update_yaxes(title="")
    plot.update_traces(textposition="outside", hovertemplate="m/z: %{x}<br>Intensity: %{y}<br>")
    
    return plot
    

def render_head_to_tail(df_head, df_tail):

    """
    Renders head-to-tail plot for spectral comparison
    
    Args:
        df_head (DataFrame): Experimental spectrum
        df_tail (DataFrame): Reference spectrum from library / database
    
    Returns:
        plotly.Figure: Head-to-tail spectral comparison plot
    """

    min_mz = min(df_head["m/z"].min(), df_tail["m/z"].min()) - 10
    max_mz = max(df_head["m/z"].max(), df_tail["m/z"].max()) + 10

    plot = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0)

    plot.append_trace(go.Bar(x=df_head["m/z"], y=df_head["Intensity"], marker=dict(color="rgb(0, 123, 255)")), row=1, col=1)
    plot.append_trace(go.Bar(x=df_tail["m/z"], y=df_tail["Intensity"], marker=dict(color="rgb(220, 53, 69)")), row=2, col=1)

    plot.update_xaxes(range=[min_mz, max_mz])
    plot.update_xaxes(showticklabels=True, row=1, col=1)
    
    plot.update_xaxes(title="Experimental", row=1, col=1)
    plot.update_xaxes(title="Reference", row=2, col=1)
    plot.update_yaxes(autorange="reversed", row=2, col=1)

    plot.update_traces(width=1, hovertemplate="m/z: %{x}<br>Intensity: %{y}<br>")
    plot.update_layout(height=height, showlegend=False, margin=dict(t=0, b=0, l=0, r=0), xaxis={'side': 'top'})

    return plot