import os
import re
import glob
import math
import pandas as pd

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

def parse_time(time_str):
    """
    Convert a time string in format HH:MM:SS,ms to total seconds.
    Example: '00:00:00,033' -> 0.033 seconds
    """
    parts = time_str.split(":")
    h = int(parts[0])
    m = int(parts[1])
    s, ms = parts[2].split(",")
    s = int(s)
    ms = int(ms)
    return h * 3600 + m * 60 + s + ms / 1000.0

def parse_srt_file(file_path, start_time_offset=0, flight_number=1):
    """
    Parse a standard .SRT file. Each block is expected to have:
      1. An index line (e.g., '1')
      2. A timecode line in the format "HH:MM:SS,mmm --> HH:MM:SS,mmm"
      3. One or more lines of text containing flight metadata

    We extract the 'end' time as the reference time and use regex to pull out
    latitude, longitude, rel_alt, and abs_alt.
    """
    data_list = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into blocks (subtitles are separated by blank lines)
    blocks = re.split(r'\n\s*\n', content.strip())
    
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 2:
            # Not enough lines to parse index + time range
            continue
        
        # First line is the index (ignored), second line is the time range
        # e.g., "00:00:00,000 --> 00:00:00,033"
        time_line = lines[1].strip()
        if "-->" not in time_line:
            continue
        
        start_time_str, end_time_str = [s.strip() for s in time_line.split("-->")]
        
        try:
            # Use the END time as reference
            end_seconds = parse_time(end_time_str)
        except Exception:
            continue
        
        cumulative_time = start_time_offset + end_seconds
        
        # Combine remaining lines (metadata) into one string
        text = " ".join(lines[2:]).strip()
        
        # Use regex to extract the metadata fields
        # [latitude: 61.708302] [longitude: 10.158810] [rel_alt: 120.000 abs_alt: 1220.922]
        lat_match = re.search(r'\[latitude:\s*([\d.\-]+)\]', text)
        lon_match = re.search(r'\[longitude:\s*([\d.\-]+)\]', text)
        alt_match = re.search(r'\[rel_alt:\s*([\d.\-]+)\s*abs_alt:\s*([\d.\-]+)\]', text)
        
        if not (lat_match and lon_match and alt_match):
            continue
        
        try:
            latitude = float(lat_match.group(1))
            longitude = float(lon_match.group(1))
            rel_alt = float(alt_match.group(1))
            abs_alt = float(alt_match.group(2))
        except Exception:
            continue
        
        data_list.append({
            "time": cumulative_time,
            "latitude": latitude,
            "longitude": longitude,
            "rel_alt": rel_alt,
            "abs_alt": abs_alt,
            "flight": flight_number
        })
    
    df = pd.DataFrame(data_list)
    return df

def process_all_srt_files(data_folder):
    """
    Scan the provided folder for .srt files, sort them by the numeric value in their filename,
    parse each file (adjusting cumulative time), and combine into one DataFrame.
    """
    srt_files = glob.glob(os.path.join(data_folder, "*.srt"))
    
    # Sort files based on the first numeric group in the filename
    def extract_number(filename):
        m = re.search(r'(\d+)', os.path.basename(filename))
        return int(m.group(1)) if m else float('inf')
    
    srt_files.sort(key=extract_number)
    
    df_all = pd.DataFrame()
    time_offset = 0.0
    flight_number = 1
    
    for srt_file in srt_files:
        df = parse_srt_file(srt_file, start_time_offset=time_offset, flight_number=flight_number)
        if not df.empty:
            df_all = pd.concat([df_all, df], ignore_index=True)
            time_offset = df["time"].max()  # Next file starts from this time
            flight_number += 1
    
    return df_all

def write_excel(df, output_path="output.xlsx"):
    """
    Write the DataFrame to an Excel file, overwriting any existing file.
    """
    df.to_excel(output_path, index=False)

def approximate_zoom_level(min_lat, max_lat, min_lon, max_lon):
    """
    Estimate a reasonable map zoom level based on the bounding box
    of the lat/lon coordinates. Adjust thresholds as needed.
    """
    lat_center = (min_lat + max_lat) / 2
    
    # ~111.32 km per degree of latitude
    lat_dist = (max_lat - min_lat) * 111.32
    # For longitude, scale by cos of the center latitude
    lon_dist = (max_lon - min_lon) * 111.32 * math.cos(math.radians(lat_center))
    max_dist = max(abs(lat_dist), abs(lon_dist))
    
    # Very rough thresholds for demonstration
    if max_dist < 1:
        return 14  # Very small area
    elif max_dist < 5:
        return 12
    elif max_dist < 20:
        return 10
    elif max_dist < 100:
        return 8
    else:
        return 4  # Very large area

def create_dash_app(df):
    """
    Create a Dash app that shows:
      - A map with the flight path (a continuous line) and a marker for the current position.
      - A slider to select the time (in seconds) along the flight.
      - An altitude graph below the slider highlighting the current rel_alt.
      - The map is initially zoomed to fit the entire flight path, and it stays that way
        each time the slider updates (so you don't have to zoom in again).
    """
    app = dash.Dash(__name__)
    
    # If no data is available, show a simple message.
    if df.empty:
        app.layout = html.Div([
            html.H1("Drone Flight Visualization"),
            html.P("No flight data available to display.")
        ])
        return app
    
    # Compute bounding box of entire flight path
    min_lat = df["latitude"].min()
    max_lat = df["latitude"].max()
    min_lon = df["longitude"].min()
    max_lon = df["longitude"].max()
    
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    zoom_level = approximate_zoom_level(min_lat, max_lat, min_lon, max_lon)
    
    max_time = df["time"].max()
    
    # Create initial altitude figure
    altitude_fig = go.Figure()
    altitude_fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["rel_alt"],
        mode='lines',
        name='Altitude'
    ))
    init_idx = (df["time"] - 0).abs().idxmin()
    altitude_fig.add_trace(go.Scatter(
        x=[df["time"].iloc[init_idx]],
        y=[df["rel_alt"].iloc[init_idx]],
        mode='markers',
        marker=dict(color='red', size=10),
        name=f'Current (Flight {df["flight"].iloc[init_idx]})'
    ))
    altitude_fig.update_layout(
        title="Altitude vs Time",
        xaxis_title="Time (s)",
        yaxis_title="Rel Altitude"
    )
    
    # Create initial map figure: show only data up to time=0, but keep bounding box in mind
    df_map = df[df["time"] <= 0]
    if df_map.empty:
        df_map = df.iloc[[0]]  # fallback to first row if there's no data at time=0
    
    map_fig = px.scatter_mapbox(
        df_map,
        lat="latitude",
        lon="longitude",
        center={"lat": center_lat, "lon": center_lon},
        zoom=zoom_level,
        height=500,
        title="Flight Path"
    )
    map_fig.update_layout(mapbox_style="open-street-map")
    
    if len(df_map) > 1:
        map_fig.add_trace(go.Scattermapbox(
            lat=df_map["latitude"],
            lon=df_map["longitude"],
            mode='lines',
            line=dict(width=2, color='blue'),
            name='Path'
        ))
    
    map_fig.add_trace(go.Scattermapbox(
        lat=df_map["latitude"],
        lon=df_map["longitude"],
        mode='markers',
        marker=dict(size=10, color='red'),
        name='Current Position'
    ))
    
    # Build the layout
    app.layout = html.Div([
        html.H1("Drone Flight Visualization"),
        dcc.Graph(id='map-graph', figure=map_fig),
        dcc.Slider(
            id='time-slider',
            min=0,
            max=max_time,
            step=0.1,
            value=0,
            marks={int(t): str(int(t)) for t in range(0, int(max_time) + 1, max(1, int(max_time / 10)))}
        ),
        dcc.Graph(id='altitude-graph', figure=altitude_fig)
    ])
    
    @app.callback(
        [Output('map-graph', 'figure'),
         Output('altitude-graph', 'figure')],
        [Input('time-slider', 'value')]
    )
    def update_graphs(selected_time):
        # Filter data up to selected_time
        df_filtered = df[df["time"] <= selected_time]
        if df_filtered.empty:
            df_filtered = df.iloc[[0]]
        
        # Rebuild the map figure but keep the same center and zoom
        map_fig_updated = px.scatter_mapbox(
            df_filtered,
            lat="latitude",
            lon="longitude",
            center={"lat": center_lat, "lon": center_lon},
            zoom=zoom_level,
            height=500,
            title="Flight Path"
        )
        map_fig_updated.update_layout(mapbox_style="open-street-map")
        
        # Add flight path line
        if len(df_filtered) > 1:
            map_fig_updated.add_trace(go.Scattermapbox(
                lat=df_filtered["latitude"],
                lon=df_filtered["longitude"],
                mode='lines',
                line=dict(width=2, color='blue'),
                name='Path'
            ))
        
        # Mark the current position
        idx = (df["time"] - selected_time).abs().idxmin()
        current_point = df.iloc[idx]
        map_fig_updated.add_trace(go.Scattermapbox(
            lat=[current_point["latitude"]],
            lon=[current_point["longitude"]],
            mode='markers',
            marker=dict(size=10, color='red'),
            name=f'Current Position (Flight {current_point["flight"]})'
        ))
        
        # Update altitude figure
        altitude_fig_updated = go.Figure()
        altitude_fig_updated.add_trace(go.Scatter(
            x=df["time"],
            y=df["rel_alt"],
            mode='lines',
            name='Altitude'
        ))
        altitude_fig_updated.add_trace(go.Scatter(
            x=[current_point["time"]],
            y=[current_point["rel_alt"]],
            mode='markers',
            marker=dict(color='red', size=10),
            name=f'Current Altitude (Flight {current_point["flight"]})'
        ))
        altitude_fig_updated.update_layout(
            title="Altitude vs Time",
            xaxis_title="Time (s)",
            yaxis_title="Rel Altitude"
        )
        
        return map_fig_updated, altitude_fig_updated
    
    return app
