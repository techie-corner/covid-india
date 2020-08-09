import dash
import dash_bootstrap_components as dbc

# bootstrap theme
# [dbc.themes.BOOTSTRAP]
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__,title="Covid in India", external_stylesheets=external_stylesheets)

server = app.server
app.config.suppress_callback_exceptions = True