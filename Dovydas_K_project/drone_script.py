import argparse #allows building command-line interface like --data-dir and --excel-out
import sys #allows printing to stderr and exiting with error codes
from drone_module import parse_srt_data, create_dash_app

def main():
    parser = argparse.ArgumentParser(
        description="Run drone flight dashboard from .SRT metadata"
    )
    parser.add_argument(
        "--data-dir", "-d", #define data location. Tells my script where to find the .SRT files
        default="Data", #defined folder where the .SRT files are located
        help="Folder containing your .SRT files"
    )
    parser.add_argument(
        "--excel-out", "-x", #define output location for excel file if needed
        help="Path to save extracted metadata as Excel"
    )
    parser.add_argument(
        "--port", "-p", #define port for web server (default is 8050), needed for Dash
        type=int,
        default=8050,
        help="Port for Dash web server"
    )
    args = parser.parse_args() #reads the command line arguments and stores them in args (e.g. --data-dir, --excel-out, --port)

    # 1) parse
    try: #try to parse the SRT data
        df = parse_srt_data(args.data_dir) #calls the function from drone_module.py to parse the SRT data
    except Exception as e: #if there is an error in data parsing, it goes to error
        print(f"Error parsing SRT data: {e}", file=sys.stderr)
        sys.exit(1) #if exit code is 1, it means there was an error

    if df.empty: #check if the dataframe is empty, meaning no data was found in the SRT files
        print("No data found. Check your Data folder and .SRT files.")
        sys.exit(0)

    # 2) summary
    pts   = len(df) #defines number of points in the dataframe
    files = df.source_file.nunique() #defines number of unique files in the dataframe
    dur   = df.time_adj.max() #defines duration of the flight in seconds
    print(f"Loaded {pts} points from {files} file(s).") 
    print(f"Total flight time: {dur:.1f}s")

    # 3) optional Excel
    # if I want to save the data to an excel file, when launching the script I have to write "py drone_script.py --excel-out Data/name_of_excel_file.xlsx"
    if args.excel_out: #check if the user provided an output file for excel
        try:
            df.to_excel(args.excel_out, index=False) #uses pandas built-in function to write the dataframe to an excel
            print(f"Data written to Excel: {args.excel_out}")
        except Exception as e:
            print(f"Could not write Excel: {e}", file=sys.stderr)

    # 4) launch Dash
    app = create_dash_app(df) #calls the function from drone_module.py to create the Dash app with the parsed data
    print(f"Starting Dash server on http://127.0.0.1:{args.port}, To stop the server, pless Ctrl+C")
    # <-- use app.run() instead of run_server()
    app.run(debug=True, port=args.port, use_reloader=False) #debug true allows to see errors and update the app without restarting the server


if __name__ == "__main__": #execute the main function, if the script is run directly (not imported as a module)
    main()
