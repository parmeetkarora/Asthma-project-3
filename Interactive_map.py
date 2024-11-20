from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import us
import os
app = Flask(__name__)



# Get the directory where APP.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the CSV file
csv_path = os.path.join(current_dir, 'US chronic Asthma.csv')

# Load the asthma dataset
asthma_data = pd.read_csv(csv_path)

# Load the asthma dataset
#asthma_data = pd.read_csv(r'US chronic Asthma.csv')

# Filter for 2021 data
data_2021 = asthma_data[asthma_data['YearStart'] == 2021]

# Extract specific data
flu_data = data_2021[data_2021['Question'] == 'Influenza vaccination among noninstitutionalized adults aged 18-64 years with asthma']
pneumo_data = data_2021[data_2021['Question'] == 'Pneumococcal vaccination among noninstitutionalized adults aged 18-64 years with asthma']
prevalence_data = data_2021[data_2021['Question'] == 'Current asthma prevalence among adults aged >= 18 years']

# Aggregate data by location
flu_agg = flu_data.groupby('LocationDesc').agg({'DataValue': 'mean'}).reset_index()
pneumo_agg = pneumo_data.groupby('LocationDesc').agg({'DataValue': 'mean'}).reset_index()
prevalence_agg = prevalence_data.groupby('LocationDesc').agg({'DataValue': 'mean'}).reset_index()

# Ensure state abbreviations are used
flu_agg['LocationDesc'] = flu_agg['LocationDesc'].map(lambda x: us.states.lookup(x).abbr if us.states.lookup(x) else None)
pneumo_agg['LocationDesc'] = pneumo_agg['LocationDesc'].map(lambda x: us.states.lookup(x).abbr if us.states.lookup(x) else None)
prevalence_agg['LocationDesc'] = prevalence_agg['LocationDesc'].map(lambda x: us.states.lookup(x).abbr if us.states.lookup(x) else None)

# Drop rows with missing or invalid state abbreviations
flu_agg.dropna(subset=['LocationDesc'], inplace=True)
pneumo_agg.dropna(subset=['LocationDesc'], inplace=True)
prevalence_agg.dropna(subset=['LocationDesc'], inplace=True)

# Function to add state abbreviations to the choropleth map
def add_state_abbreviations(fig, data):
    fig.add_trace(
        go.Scattergeo(
            locations=data['LocationDesc'],
            locationmode="USA-states",
            text=data['LocationDesc'],
            mode='text',
            textposition='top center',
            showlegend=False,
            textfont=dict(size=10, color='black')
        )
    )
    return fig

# Flask route for homepage
@app.route('/')
def index():
    # Influenza Vaccination Map
    flu_fig = px.choropleth(
        flu_agg,
        locations='LocationDesc',
        locationmode="USA-states",
        color='DataValue',
        scope="usa",
        color_continuous_scale='Blues',
        range_color=(flu_agg['DataValue'].min(), flu_agg['DataValue'].max()),
        labels={'DataValue': 'Flu Vaccination Rate (%)'},
        title='Influenza Vaccination among Adults with Asthma (2021)'
    )
    flu_fig.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    flu_fig = add_state_abbreviations(flu_fig, flu_agg)
    
    # Pneumococcal Vaccination Map
    pneumo_fig = px.choropleth(
        pneumo_agg,
        locations='LocationDesc',
        locationmode="USA-states",
        color='DataValue',
        scope="usa",
        color_continuous_scale='Greens',
        range_color=(pneumo_agg['DataValue'].min(), pneumo_agg['DataValue'].max()),
        labels={'DataValue': 'Pneumococcal Vaccination Rate (%)'},
        title='Pneumococcal Vaccination among Adults with Asthma (2021)'
    )
    pneumo_fig.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    pneumo_fig = add_state_abbreviations(pneumo_fig, pneumo_agg)
    
    # Asthma Prevalence Map
    asthma_fig = px.choropleth(
        prevalence_agg,
        locations='LocationDesc',
        locationmode="USA-states",
        color='DataValue',
        scope="usa",
        color_continuous_scale='Oranges',
        range_color=(prevalence_agg['DataValue'].min(), prevalence_agg['DataValue'].max()),
        labels={'DataValue': 'Asthma Prevalence (%)'},
        title='Current Asthma Prevalence among Adults (2021)'
    )
    asthma_fig.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    asthma_fig = add_state_abbreviations(asthma_fig, prevalence_agg)

    # Convert plots to HTML
    flu_map_html = pio.to_html(flu_fig, full_html=False)
    pneumo_map_html = pio.to_html(pneumo_fig, full_html=False)
    asthma_map_html = pio.to_html(asthma_fig, full_html=False)
    
    return render_template('index.html', flu_map_html=flu_map_html, pneumo_map_html=pneumo_map_html, asthma_map_html=asthma_map_html)

if __name__ == '__main__':
    app.run(debug=True)
