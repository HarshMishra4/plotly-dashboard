from datetime import datetime
from dash import Dash, Output, Input, html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Custom file
from data_handler import init, find_total

# Load and clean and Tranforming the DataSet
confirmed_melt_df, deaths_melt_df, recovered_melt_df = init()

# Selecting Max Date
max_date = str(confirmed_melt_df['Date'].max())

# Filter by Max Date
total_deaths_df, total_deaths = find_total(deaths_melt_df, 'Deaths', max_date)
total_confirmed_df, total_confirmed = find_total(confirmed_melt_df, 'Confirmed', max_date)
total_recovered_df, total_recovered = find_total(recovered_melt_df, 'Recovered', max_date)

total_df = total_confirmed_df.copy()
total_df['Deaths'] = total_deaths_df['Deaths']
total_df['Recovered'] = total_recovered_df['Recovered']
total_df['DeathRate'] = (total_df['Deaths'] / total_df['Confirmed'] * 100).round(2)

# Total Active Cases
total_active = total_confirmed - total_deaths - total_recovered
# Total Cases
total_cases = total_confirmed + total_deaths + total_recovered
# Superhero

# Initializing our app
app = Dash(__name__,
    external_stylesheets=[dbc.themes.SUPERHERO],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}]
)

data = {
    'label': ['Cases','Deaths','Confirmed','Active'],
    'value' : [total_cases, total_deaths, total_confirmed, total_active]
}
# ======================================
# SCATTER plot
scatter_plot_fig = px.scatter(
    total_df.sort_values(by='Confirmed', ascending=False).head(20),
    x = 'Confirmed', y = "Deaths",
    color = 'Country/Region',
    size='DeathRate',
    title= f'Cases from 2020 to {total_df["Date"].iloc[-1].date().year}',
)
scatter_plot_fig.update_layout(
    paper_bgcolor = '#1f2c56',
    plot_bgcolor = '#1f2c56',
    titlefont = {
        'color' :'white',
    },
    legend = {
        'bgcolor' : '#1f2c56',
    },
    font = {'color' : 'white'},
)

# Filter by Deaths of Top 20 Countries
B = total_df.copy()
B = B.sort_values(by='Deaths', ascending=False).head(20)

# ================================
# =====[ BAR AND LINE plot]=======
# ================================
bar_plot_fig = make_subplots(specs=[[{'secondary_y':True}]])
bar_plot_fig.add_trace(go.Bar(
    x = B['Country/Region'], y = B['Deaths'],
    text = B['Deaths'], name="Deaths",
    marker = dict(color = 'orange'),
    textposition='auto',
), secondary_y=False)
bar_plot_fig.add_trace(go.Scatter(
    x = B['Country/Region'], y = B['DeathRate'],
    text = B['DeathRate'], name="Death Rate {%}",
    mode='markers+lines',
    line= {'color' : 'red'}
), secondary_y=True)
bar_plot_fig.update_layout({
    'paper_bgcolor': '#1f2c56',
    'plot_bgcolor': '#1f2c56',
    'titlefont' : {
        'color' :'white',
    },
    'legend' : {
        'bgcolor' : '#1f2c56',
    },
    'font' : {'color' : 'white'}
},
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)

# ================================
# ========[ DropDown ]============
# ================================
options = [{'label': country, 'value': country} for country in total_df['Country/Region'].unique()]
dropdown = dcc.Dropdown(
    value = 'India',
    options = options,
    id = 'place-selector',
    style = {
        'color' :'black',
    }
) 
# ================================
# =====[ Web Page Layout ]========
# ================================
app.layout = dbc.Container([
    html.H1("COVID-19 TRACK REPORT", className="text-center mt-4"),
    # Section 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.H5(f'Global {data["label"][i]}', className="text-center mb-2"),
                html.H1("{:,.0f}".format(data['value'][i]), className="text-center text-warning")
            ], className="mt-3 p-2")
        ]) for i in range(4)
    ]),
    # Section 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Container([
                    html.P("Filter By Country"),
                    dropdown,
                    html.P("Filter By Date", className="mt-3"),
                    html.Div([dcc.DatePickerSingle(
                        id='date-picker',
                        min_date_allowed=datetime(2020, 1, 22),
                        max_date_allowed=datetime(2022, 5, 18),
                        date=datetime(2022, 5, 18),
                        display_format='DD/MM/YYYY',
                    )], className="mb-3"),
                ], className = "mt-3")   
            ], style = {
                'background-color' : '#1f2c56'
            })
        ], className="col-3"),
        # Pie chart for Country based Data
        dbc.Col([
            dbc.Card([
                dcc.Graph(id='pie-plot', figure={})
            ])
        ], className="col-3"),
        dbc.Col([
            dbc.Card([
                dcc.Graph(id='line-plot', figure={})
            ])
        ])
    ], className="mt-3"),
    
    # Section 3
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='scatter-plot', figure=scatter_plot_fig)
        ]),
    ], className="mt-3"),
    # Section 4

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-plot', figure=bar_plot_fig)
        ])
    ], className="mt-3")
,
    html.Br(),
    html.Br()
])

dataset = confirmed_melt_df.copy()
dataset['Deaths'] = deaths_melt_df['Deaths']
dataset['Recovered'] = recovered_melt_df['Recovered']


@app.callback(
    Output('line-plot', 'figure'),
    Input('place-selector', 'value'),
)
def update_line_plot(country_name):
    filtered = confirmed_melt_df[confirmed_melt_df['Country/Region'] == country_name].tail(30)
    fig = px.line(filtered, x = 'Date', y = 'Confirmed')
    fig.update_layout(
        paper_bgcolor = '#1f2c56',
        plot_bgcolor = '#1f2c56',
        titlefont = {
            'color' :'white',
        },
        legend = {
            'bgcolor' : '#1f2c56',
        },
        font = {'color' : 'white'},
        title = {
            'y' : 0.93,
            'x' : 0.5,
            'xanchor' : 'center',
            'yanchor' : 'top',
            'text' : f'Last 30 days Confirmed Cases : {country_name}',
        },
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    return fig

@app.callback(
    Output('pie-plot', 'figure'),
    Input('place-selector', 'value'),
    Input('date-picker', 'date')
)
def update_pie_graph(country_name, date):
    # Fixing Date format
    date = pd.to_datetime(date)
    # Filtering the data
    df = dataset.groupby(['Date','Country/Region'])[['Confirmed', 'Deaths', 'Recovered']].sum().reset_index()
    # Filter out data based on given date and Country name
    filtered_df = df[(df['Country/Region'] == country_name) & (df['Date'] == str(date))]
    # filtered_df = df.query(f'Country/Region == {country_name} and Date == {date}')
    confirmed = filtered_df['Confirmed'].iloc[-1]
    deaths = filtered_df['Deaths'].iloc[-1]
    recovered = filtered_df['Recovered'].iloc[-1]

    labels = filtered_df.columns[2:5]
    values = [confirmed, deaths, recovered]
    pie = px.pie(labels, values = values, hole = 0.6,
        names = labels, color = labels,
        color_discrete_map = {
        'Confirmed':'orange', 
        'Recovered': 'red',
        'Death':'blue'}
    )
    pie.update_traces(
        rotation = 45,
        textinfo='label+value',
        textfont=dict(color="white")
    )
    pie.update_layout({
        # 'paper_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': '#1f2c56',
        'title' : {
            'text' : f'Total Cases : {country_name}',
            'y' : 0.93,
            'x' : 0.5,
            'xanchor' : 'center',
            'yanchor' : 'top'
        },
        'titlefont' : {
            'color' :'white',
            'size' : 20
        },
        'legend' : {
            'orientation' : 'h',
            'bgcolor' : '#1f2c56',
            'xanchor' : 'center', 'x': 0.5, 'y': -0.07
        },
        'font' : {'color' : 'white'}
    })
    return pie

if __name__ == '__main__':
    app.run_server(debug=True)