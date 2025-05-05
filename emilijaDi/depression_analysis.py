import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Read the CSV file
def read_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# Create the dashboard
def create_dashboard(df):
    app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
    
    # Get numeric columns excluding IDs and other non-meaningful columns
    numeric_columns = [col for col in df.columns 
                      if df[col].dtype in ['int64', 'float64'] 
                      and not any(id_term in col.lower() for id_term in ['id', 'index', 'no', 'number'])]
    
    # Custom colors
    colors = {
        'background': '#f8f9fa',
        'text': '#2c3e50',
        'card': '#ffffff',
        'primary': '#3498db',
        'secondary': '#2ecc71'
    }
    
    # Layout
    app.layout = dbc.Container([
        # Header with gradient background
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("Student Depression Analysis Dashboard", 
                           className="text-center my-4",
                           style={'color': colors['text'], 'fontWeight': 'bold'}),
                    html.P("Interactive Analysis of Student Mental Health Data",
                          className="text-center mb-4",
                          style={'color': colors['text']})
                ], style={'background': 'linear-gradient(120deg, #3498db, #2ecc71)',
                         'padding': '20px',
                         'borderRadius': '10px',
                         'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'})
            ], width=12)
        ], className="mb-4"),
        
        # Dataset Overview Card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Dataset Overview", 
                                 className="text-center",
                                 style={'backgroundColor': colors['primary'],
                                       'color': 'white',
                                       'fontWeight': 'bold'}),
                    dbc.CardBody([
                        html.Div([
                            html.P(f"Total Students: {len(df)}", 
                                  className="mb-2",
                                  style={'fontSize': '1.1em'}),
                            html.P(f"Number of Features: {len(df.columns)}",
                                  className="mb-2",
                                  style={'fontSize': '1.1em'}),
                            html.P("Features:", 
                                  className="mb-2",
                                  style={'fontSize': '1.1em'}),
                            html.Ul([html.Li(col, style={'marginLeft': '20px'}) 
                                   for col in df.columns])
                        ])
                    ])
                ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                         'borderRadius': '10px'})
            ], width=12)
        ], className="mb-4"),
        
        # Feature Selection and Analysis Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Feature Selection", 
                                 className="text-center",
                                 style={'backgroundColor': colors['primary'],
                                       'color': 'white',
                                       'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id='column-selector',
                            options=[{'label': col, 'value': col} for col in df.columns],
                            value=df.columns[0],
                            style={'width': '100%'}
                        )
                    ])
                ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                         'borderRadius': '10px'})
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Feature Summary", 
                                 className="text-center",
                                 style={'backgroundColor': colors['primary'],
                                       'color': 'white',
                                       'fontWeight': 'bold'}),
                    dbc.CardBody([
                        html.Div(id='data-summary')
                    ])
                ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                         'borderRadius': '10px'})
            ], width=6)
        ], className="mb-4"),
        
        # Visualization Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Distribution Analysis", 
                                 className="text-center",
                                 style={'backgroundColor': colors['primary'],
                                       'color': 'white',
                                       'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(id='histogram')
                    ])
                ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                         'borderRadius': '10px'})
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Box Plot Analysis", 
                                 className="text-center",
                                 style={'backgroundColor': colors['primary'],
                                       'color': 'white',
                                       'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(id='box-plot')
                    ])
                ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                         'borderRadius': '10px'})
            ], width=6)
        ], className="mb-4"),
        
        # Correlation Analysis Card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Correlation Analysis", 
                                 className="text-center",
                                 style={'backgroundColor': colors['primary'],
                                       'color': 'white',
                                       'fontWeight': 'bold'}),
                    dbc.CardBody([
                        html.P("Note: ID columns and non-numeric columns are excluded from correlation analysis",
                              className="text-center mb-3",
                              style={'color': colors['text']}),
                        dcc.Graph(id='correlation-heatmap')
                    ])
                ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                         'borderRadius': '10px'})
            ], width=12)
        ], className="mb-4"),
        
        # Feature Distribution Card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Detailed Distribution Analysis", 
                                 className="text-center",
                                 style={'backgroundColor': colors['primary'],
                                       'color': 'white',
                                       'fontWeight': 'bold'}),
                    dbc.CardBody([
                        dcc.Graph(id='feature-distribution')
                    ])
                ], style={'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                         'borderRadius': '10px'})
            ], width=12)
        ])
    ], fluid=True, style={'backgroundColor': colors['background'],
                         'padding': '20px'})
    
    # Callbacks
    @app.callback(
        Output('data-summary', 'children'),
        Input('column-selector', 'value')
    )
    def update_summary(selected_column):
        if df[selected_column].dtype in ['int64', 'float64']:
            summary = df[selected_column].describe()
            return html.Div([
                html.P(f"Mean: {summary['mean']:.2f}", 
                      style={'fontSize': '1.1em'}),
                html.P(f"Median: {summary['50%']:.2f}",
                      style={'fontSize': '1.1em'}),
                html.P(f"Standard Deviation: {summary['std']:.2f}",
                      style={'fontSize': '1.1em'}),
                html.P(f"Min: {summary['min']:.2f}",
                      style={'fontSize': '1.1em'}),
                html.P(f"Max: {summary['max']:.2f}",
                      style={'fontSize': '1.1em'})
            ])
        else:
            value_counts = df[selected_column].value_counts()
            return html.Div([
                html.P(f"Unique Values: {len(value_counts)}",
                      style={'fontSize': '1.1em'}),
                html.P("Top 5 Values:",
                      style={'fontSize': '1.1em'}),
                html.Ul([html.Li(f"{val}: {count}",
                               style={'fontSize': '1.1em',
                                     'marginLeft': '20px'}) 
                        for val, count in value_counts.head().items()])
            ])
    
    @app.callback(
        Output('histogram', 'figure'),
        Input('column-selector', 'value')
    )
    def update_histogram(selected_column):
        if df[selected_column].dtype in ['int64', 'float64']:
            fig = px.histogram(df, x=selected_column, 
                             title=f'Distribution of {selected_column}',
                             color_discrete_sequence=[colors['primary']])
        else:
            fig = px.bar(df[selected_column].value_counts(), 
                        title=f'Distribution of {selected_column}',
                        color_discrete_sequence=[colors['primary']])
        fig.update_layout(plot_bgcolor=colors['card'],
                         paper_bgcolor=colors['card'],
                         font_color=colors['text'])
        return fig
    
    @app.callback(
        Output('box-plot', 'figure'),
        Input('column-selector', 'value')
    )
    def update_box_plot(selected_column):
        if df[selected_column].dtype in ['int64', 'float64']:
            fig = px.box(df, y=selected_column, 
                        title=f'Box Plot of {selected_column}',
                        color_discrete_sequence=[colors['primary']])
        else:
            fig = go.Figure()
            fig.add_annotation(text="Box plot not available for categorical data",
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False)
        fig.update_layout(plot_bgcolor=colors['card'],
                         paper_bgcolor=colors['card'],
                         font_color=colors['text'])
        return fig
    
    @app.callback(
        Output('correlation-heatmap', 'figure'),
        Input('column-selector', 'value')
    )
    def update_correlation_heatmap(_):
        if len(numeric_columns) > 1:
            corr_matrix = df[numeric_columns].corr()
            fig = px.imshow(corr_matrix,
                          title='Correlation Heatmap (Excluding ID columns)',
                          color_continuous_scale='RdBu',
                          labels=dict(x="Features", y="Features", color="Correlation"))
            fig.update_layout(xaxis_tickangle=45,
                            plot_bgcolor=colors['card'],
                            paper_bgcolor=colors['card'],
                            font_color=colors['text'])
        else:
            fig = go.Figure()
            fig.add_annotation(text="Not enough numeric columns for correlation heatmap",
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False)
        return fig
    
    @app.callback(
        Output('feature-distribution', 'figure'),
        Input('column-selector', 'value')
    )
    def update_feature_distribution(selected_column):
        if df[selected_column].dtype in ['int64', 'float64']:
            fig = px.violin(df, y=selected_column, 
                          title=f'Violin Plot of {selected_column}',
                          color_discrete_sequence=[colors['primary']])
        else:
            fig = px.pie(df, names=selected_column, 
                        title=f'Distribution of {selected_column}',
                        color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(plot_bgcolor=colors['card'],
                         paper_bgcolor=colors['card'],
                         font_color=colors['text'])
        return fig
    
    return app

def main():
    file_path = 'student_depression_dataset_usa.csv'
    df = read_data(file_path)
    
    if df is not None:
        app = create_dashboard(df)
        app.run(debug=True)
    else:
        print("Failed to read the CSV file. Please check the file path and format.")

if __name__ == "__main__":
    main() 
