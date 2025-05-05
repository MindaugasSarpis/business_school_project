import re #we use re to define patterns and extract (parse) latitude, longitude, timestamps, etc., from the text in your .SRT files.
import os #We use functions like os.path.join, os.listdir, or os.path.exists to locate and manage file paths in a cross-platform way.
from pathlib import Path #The pathlib module provides an object-oriented way to handle file paths (the Path class).
import pandas as pd #We collect all parsed metadata into a DataFrame, which makes it easy to sort, filter, compute elapsed time, and (optionally) write out to Excel.

import dash #The core Dash framework for building interactive web apps in pure Python
from dash import dcc, html, Input, Output #dcc (“Dash Core Components”) — pre-built components like sliders and graphs. html — functions for HTML tags (e.g. html.Div, html.H1). Input, Output — decorators that wire up callbacks (so when the slider moves, Dash knows which function to run).
import plotly.express as px #Plotly Express, a high-level API for quickly drawing common chart types (scatter plots, line charts, mapbox maps, etc.). In this case, base map with minimal code.
import plotly.graph_objects as go #Plotly’s lower-level ­“graph objects” API, which gives you full control over traces and layouts. In this case e combine go.Scattermapbox and go.Scatter to layer custom lines and markers on the map and altitude plot.
import math #Built-in math library. Used math.cos and math.radians (and basic arithmetic) to estimate a reasonable map zoom level from your GPS bounding box.

def parse_srt_data(data_dir: str) -> pd.DataFrame: #def - funcion | name of funcion | data_dir is defining location of my data and "str" defines it as string (text) | data frame - way of defining table
    """
    Read all .SRT files in `data_dir` and extract:
      - timestamp (datetime)
      - time (float seconds since start)
      - latitude, longitude
      - rel_alt, abs_alt
      - source_file
    Returns a DataFrame with those columns.
    """
    data_dir = Path(data_dir) #Path is directory string, which allows simplified identification of file paths. (it knows what is "parent", "name", or "suffix" on it's own)
    patterns = { #dictionary of regex (regular expression) patterns to search for in the SRT files
        'timestamp': re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})'),
        'latitude':  re.compile(r'latitude\s*:\s*([-\d.]+)'), #looks for literal world "latitute", \s* any whitespace for any lenght(*), "-" allows for negative numbers, but still allows positives, \d any digit 0-9, "." litteral dot (in this case decimal point), "+" - one or more of those characters in a row.
        'longitude': re.compile(r'longitude\s*:\s*([-\d.]+)'),
        'rel_alt':   re.compile(r'rel_alt\s*:\s*([-\d.]+)'),
        'abs_alt':   re.compile(r'abs_alt\s*:\s*([-\d.]+)')
    }
    all_data = [] #define empty list to store all data
    for srt_file in data_dir.glob("*.SRT"): #loop through all files in the data_dir that end with .SRT | glob - function that returns all files in the directory that match the pattern
        with srt_file.open(encoding='utf-8') as f: #with allows to open the file and then automatically close it when done | srt_file - file object | encoding - utf-8 is a common text encoding that supports many characters
            lines = f.readlines() #in previous line we opened file "f" and now we read all lines in the file and store them in the list "lines".
        entry = {} #can hold only one entry at a time, so we clear it for each file, while "all_data" holds all entries from all files.
        for line in lines:
            text = line.strip() #strip removes leading and trailing whitespace (spaces, tabs, newlines) from the line.
            for key, pat in patterns.items(): # key looks for dictionary keys (timestamp, latitude, etc.) and pat looks for the regex pattern in the dictionary "patterns".
                m = pat.search(text) #search - looks for the pattern (re.compile(XXX)) in the text. If we find it - we store location information in "m".
                if m: #if m is not None (meaning we found a match in previous line)
                    val = m.group(1) #group(1) - returns the capturing group from the match object (m). This is the part of the text that matched the regex pattern in parentheses (žr. line 24).
                    if key in ('latitude','longitude','rel_alt','abs_alt'):
                        val = float(val) #we conver string value to float (decimal number).
                    entry[key] = val #store the value in the entry dictionary with the idenfitication key (timestamp, latitude, etc.).
            # once we have a full set, record it
            if all(k in entry for k in ('timestamp','latitude','longitude','rel_alt','abs_alt')): # all check if key (k) exists (TURE/FALSE) in entry ("in" checks if key is in dictionary). Then loop through all keys in the entry dictionary and check if they are in the list of keys we want to extract.
                entry['source_file'] = srt_file.name #we add to entry dictionary the name of the file we are currently processing.
                all_data.append(entry.copy()) #we add entry to the all_data list. Each loop we add all 5 values we have and and each loop (or entry) is seperated using new line.
                entry.clear() # we clear the entry dictionary for the next file.

    df = pd.DataFrame(all_data) #turing collected list of records into a Pandas table (data frame). Dict keys become column names and dict values become rows.
    if df.empty:
        return df #if no data was found, we return empty data frame.

    # parse times, sort, compute seconds since start
    df['timestamp'] = pd.to_datetime(df['timestamp']) #orverwrite the timestamp column with the parsed datetime object (convert string to datetime).
    df = df.sort_values('timestamp').reset_index(drop=True) #sort the data frame by timestamp and reset the index (drop=True means we don't want to keep the old index).
    t0 = df['timestamp'].iloc[0] #defining t0 as the first timestamp in the data frame. iloc is used to access the first row (not index) of the data frame.
    df['time'] = (df['timestamp'] - t0).dt.total_seconds() #compute (and add new column) the time since the start of the flight (t0). We subtract t0 from each timestamp and convert it to seconds using dt.total_seconds().

    # 1) Compute the raw inter‐frame deltas
    df['dt'] = df['time'].diff().fillna(0)
    # 2) Treat any big gap (here > 5 s) as no gap at all
    GAP_THRESH = 5.0  # seconds — tune to your flights’ expected idle-time
    df.loc[df['dt'] > GAP_THRESH, 'dt'] = 0
    # 3) Cumulate those deltas to get an “adjusted” time axis
    df['time_adj'] = df['dt'].cumsum()
    # 4) (Optional) drop the helper column if you like
    df.drop(columns=['dt'], inplace=True)

    return df #return the data frame with all the data we collected and parsed.

def approximate_zoom_level(min_lat, max_lat, min_lon, max_lon): #calculates zoom, values are passed from function create_dash_app
    """Rough zoom based on bounding box size."""
    lat_center = (min_lat + max_lat)/2 #calculating center of the bounding box (average of min and max latitude).
    lat_dist = (max_lat - min_lat) * 111.32 #calculating distance in km between min and max latitude. 111.32 is the approximate number of km per degree of latitude.
    lon_dist = (max_lon - min_lon) * 111.32 * math.cos(math.radians(lat_center)) #earth lines of longtidue converge as you move away from equator. So we use cosine of the latitude to calculate the distance in km between min and max longitude. We convert latitude to radians using math.radians.
    d = max(abs(lat_dist), abs(lon_dist)) #the largest distance between min and max latitude or longitude. we use d to calculate zoom level.
    if d < 1:   return 15
    if d < 5:   return 13
    if d < 20:  return 11
    if d < 100: return 9
    return 4 #if else return 4 (zoom out).

def create_dash_app(df: pd.DataFrame) -> dash.Dash:
    """
    Build and return a Dash app that shows:
      - A map of the full flight path plus a moving red marker.
      - A slider for 'time' in seconds.
      - An altitude vs time plot with a moving red dot.
    """
    app = dash.Dash(__name__) #dash.Dash - creates a new Dash app instance like hosting web application. __name__ - name of the module (current file). This is used to identify the app and its resources.
    if df.empty:
        app.layout = html.Div([
            html.H1("Drone Flight Visualization by Dovydas for Artificial Intelligence and Data Analytics"), #title of the app
            html.P("No data found in .SRT files.") #some paragraph if no data is found in the SRT files.
        ])
        return app

    # bounding box + zoom
    min_lat, max_lat = df.latitude.min(), df.latitude.max() #calculating min and max latitude and longitude from the data frame.
    min_lon, max_lon = df.longitude.min(), df.longitude.max() #calculating min and max longitude from the data frame.
    center = {"lat": (min_lat+max_lat)/2, "lon": (min_lon+max_lon)/2} #calculating center of the bounding box (average of min and max latitude and longitude).
    zoom = approximate_zoom_level(min_lat, max_lat, min_lon, max_lon) #calculating zoom level using the function we defined above.

    # initial figures at time=0
    max_time = df['time_adj'].max() #calculating and defining max time from the data frame.
    initial_time = 0

    # Layout
    app.layout = html.Div([
        html.H1("Drone Flight Visualization by Dovydas K. for Artificial Intelligence and Data Analytics"), #title of the app (same as used when df is empty).
        dcc.Graph(id='map-graph'), #map graph (empty at the beginning), but when referred to in the callback, it would update this component.
        dcc.Slider(
            id='time-slider',
            min=0, max=max_time, step=0.1, value=initial_time, #from 0 to max_time, step is 0.1 seconds, initial value is 0 as defined above.
            marks={int(t): str(int(t)) for t in range(0, int(max_time)+1, max(1,int(max_time/10)))} #these are numbers that are below the map identifying time in seconds.
        ),
        dcc.Graph(id='altitude-graph')
    ])

    @app.callback(
        [Output('map-graph','figure'),
         Output('altitude-graph','figure')],
        [Input('time-slider','value')] #this is the input for the callback, when we move the slider, it will trigger the function update_figures and it will update output (map and altitude graphs mentioned above). It also tracts person movement of the slider on which other shown data depends
    )
    def update_figures(selected_time): #this function is called when the slider is moved. It takes the selected time from the slider as input and updates the map and altitude graphs.
        # filter up to selected time
        df_f = df[df['time_adj'] <= selected_time] #takes all data from data frame that is less or equal to selected time (not one entry, but all entries from start until selected time).
        if df_f.empty:
            df_f = df.iloc[[0]] #if no data is found, we take the first row (not first index) of the data frame.

        # map: full path grey + path up to now blue + current marker
        map_fig = go.Figure()
        map_fig.add_trace(go.Scattermapbox( #single trace draws one continuous grey line through every GPS point from the very start to the very end.
            lat=df.latitude, lon=df.longitude,
            mode='lines', line=dict(color='lightgrey', width=2),
            name='Full Path'
        ))
        map_fig.add_trace(go.Scattermapbox( #second trace draws a blue line from the start to the selected time (up to now).
            lat=df_f.latitude, lon=df_f.longitude,
            mode='lines', line=dict(color='blue', width=3),
            name='Progress'
        ))
        map_fig.add_trace(go.Scattermapbox( #third trace draws a red dot at the current position of the drone (last point in the data frame).
            lat=[df_f.latitude.iloc[-1]], lon=[df_f.longitude.iloc[-1]], #iloc[-1] - last row of the data frame.
            mode='markers', marker=dict(size=12, color='red'),
            name='Current'
        ))
        map_fig.update_layout(
            mapbox_style='open-street-map',
            mapbox=dict(center=center, zoom=zoom),
            margin=dict(l=0,r=0,t=30,b=0)
        )

        # altitude plot: full line + current dot
        alt_fig = go.Figure()
        alt_fig.add_trace(go.Scatter(
            x=df['time_adj'], y=df['rel_alt'],
            mode='lines', name='Altitude'
        ))
        alt_fig.add_trace(go.Scatter(
            x=[selected_time],
            y=[df_f['rel_alt'].iloc[-1]], 
            #y=[df.loc[df['time'].sub(selected_time).abs().idxmin(), 'rel_alt']],
            mode='markers', marker=dict(size=10, color='red'),
            name='Current Alt'  
        ))
        alt_fig.update_layout(
            xaxis_title='Time (s)',
            yaxis_title='Rel Altitude (m)',
            margin=dict(l=40,r=20,t=30,b=40)
        )

        return map_fig, alt_fig

    return app
