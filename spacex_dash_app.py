import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # A dropdown list to enable Launch Site selection
                                dcc.Dropdown(id='site-dropdown',  
                                             options=[
                                                {'label': 'All Sites', 'value': 'ALL'},
                                                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                ],
                                                value = 'ALL',
                                                placeholder = "Choose an Option",
                                                searchable = True
                                                ),
                                html.Br(),

                                # A pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # A slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                       2500: '2500',
                                                       5000: '5000',
                                                       7500: '7500',
                                                       10000: '10000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# A callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    all_site_df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
    site_spec_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    if entered_site == 'ALL':
        fig = px.pie(all_site_df, 
        values='class', 
        names='Launch Site', 
        title="Total Successful Launches Count For All Sites")
        return fig
    else:
        svf = site_spec_df.groupby('class')['Flight Number'].count().reset_index()
        fig = px.pie(svf, 
        values='Flight Number', 
        names='class', 
        title="Success (1) vs. Failed (0) counts for {}".format(entered_site))
        return fig


# A callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
             [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, selected_payload):
    scatter_spacex_df = spacex_df[spacex_df['Payload Mass (kg)'].between(selected_payload[0], selected_payload[1])]
    site_spec_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    scatter_site_spec_df = site_spec_df[site_spec_df['Payload Mass (kg)'].between(selected_payload[0], selected_payload[1])]
    if entered_site == 'ALL':
        fig = px.scatter(scatter_spacex_df,
                        x = 'Payload Mass (kg)',
                        y = 'class',
                        color = 'Booster Version Category',
                        title = 'Correlation between Payload and Success for all Sites')
        return fig
    else:
        fig = px.scatter(scatter_site_spec_df,
                        x = 'Payload Mass (kg)',
                        y = 'class',
                        color = 'Booster Version Category',
                        title = 'Correlation between Payload and Success for {}'.format(entered_site))
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
