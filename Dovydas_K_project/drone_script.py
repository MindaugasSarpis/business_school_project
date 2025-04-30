import os
from drone_module import process_all_srt_files, write_excel, create_dash_app

def main():
    # 1) Define the folder containing SRT files (assuming a subfolder named "Data")
    data_folder = os.path.join(os.getcwd(), "Data")
    
    # 2) Process all .srt files in the Data folder.
    df = process_all_srt_files(data_folder)
    
    # 3) Write the extracted data to an Excel file (this overwrites any existing file).
    write_excel(df, output_path="output.xlsx")
    print("Excel file 'output.xlsx' written successfully.")

    # 4) Launch the Dash app for interactive visualization.
    app = create_dash_app(df)

    print("All good, app is running. Reminder to myself -> to stop app from running press Ctrl+C")
    # The app will run at http://127.0.0.1:8050/ by default.
    app.run_server(debug=True)

if __name__ == "__main__":
    main()
