from dash import Dash, html, dcc, Input, Output, page_container
import dash_bootstrap_components as dbc # there are other 3rd party dash components, but let's stick with bootstrap for now.
from dash.exceptions import PreventUpdate

app = Dash(__name__,
           use_pages=True, # multi-page dash webapp
           external_stylesheets=[dbc.themes.CYBORG], # initialize dash app with bootstrap theme.
           suppress_callback_exceptions=True, # ticker page is dynamic, so need to suppress this kind of error
           #meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
           # may not need this "mobile friendly" tag since the design of bootstrap components is to make it mobile friendly from the core
           ) 
app.layout = page_container # simply a container for the pages

if __name__ == '__main__':
    app.run_server(debug=True)