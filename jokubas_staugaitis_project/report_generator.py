import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import win32com.client
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")
import datetime as dt
import tempfile
import threading
import io
from PIL import Image as PILImage
from PIL import ImageTk

class TruckAccidentReporter:
    def __init__(self, root):
        self.root = root
        self.root.title("Truck Accident Report Generator")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Set application style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', background='#4a7abc', foreground='black', font=('Helvetica', 10))
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 11))
        self.style.configure('Header.TLabel', background='#f0f0f0', font=('Helvetica', 14, 'bold'))
        
        # Variables
        self.data = None
        self.report_path = None
        self.preview_images = []
        
        # Main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Truck Accident Report Generator", 
                                style='Header.TLabel')
        title_label.pack(pady=10)
        
        # File selection frame
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_path_var = tk.StringVar()
        file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(file_frame, text="Browse Excel File", command=self.browse_file)
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_label = ttk.Label(progress_frame, text="Status: Ready")
        self.progress_label.pack(side=tk.TOP, anchor=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, length=400)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        generate_button = ttk.Button(button_frame, text="Generate Report", command=self.generate_report)
        generate_button.pack(side=tk.LEFT, padx=5)
        
        self.preview_button = ttk.Button(button_frame, text="Preview Report", 
                                        command=self.preview_report, state=tk.DISABLED)
        self.preview_button.pack(side=tk.LEFT, padx=5)
        
        self.email_button = ttk.Button(button_frame, text="Send Email", 
                                      command=self.show_email_dialog, state=tk.DISABLED)
        self.email_button.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_button = ttk.Button(button_frame, text="Close", command=self.on_close)
        close_button.pack(side=tk.RIGHT, padx=5)
        
        # Preview area
        preview_label = ttk.Label(main_frame, text="Report Preview:", style='Header.TLabel')
        preview_label.pack(anchor=tk.W, pady=(20, 10))
        
        self.preview_frame = ttk.Frame(main_frame, borderwidth=2, relief=tk.GROOVE)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.preview_frame.configure(height=300)
        
        # Canvas for preview with both scrollbars
        self.canvas_frame = ttk.Frame(self.preview_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars for preview
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical")
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient="horizontal")
        
        self.preview_canvas = tk.Canvas(self.canvas_frame, 
                                      yscrollcommand=self.v_scrollbar.set,
                                      xscrollcommand=self.h_scrollbar.set,
                                      bg='white', height=250)
        
        self.v_scrollbar.config(command=self.preview_canvas.yview)
        self.h_scrollbar.config(command=self.preview_canvas.xview)
        
        # Grid layout for canvas and scrollbars
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_file(self):
        """Open file dialog to select Excel file"""
        filepath = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")]
        )
        if filepath:
            self.file_path_var.set(filepath)
            self.status_var.set(f"Selected file: {os.path.basename(filepath)}")

    def update_progress(self, value, message):
        """Update progress bar and message"""
        self.progress_var.set(value)
        self.progress_label.config(text=f"Status: {message}")
        self.root.update_idletasks()

    def generate_report(self):
        """Generate the truck accident report"""
        file_path = self.file_path_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid Excel file")
            return
        
        # Start processing in a separate thread to avoid UI freezing
        threading.Thread(target=self._process_report, daemon=True).start()

    def _process_report(self):
        """Process the report in a background thread"""
        try:
            self.update_progress(10, "Loading data...")
            # Load data with proper encoding for Lithuanian characters
            self.data = pd.read_excel(self.file_path_var.get(), engine='openpyxl')
            
            # Validate required columns
            required_columns = ['Truck type', 'Licence plate number', 'Driver', 'Date', 
                               'Fault', 'Type', 'Description']
            missing_columns = [col for col in required_columns if col not in self.data.columns]
            if missing_columns:
                messagebox.showerror("Error", f"Missing required columns: {', '.join(missing_columns)}")
                self.update_progress(0, "Error: Missing columns")
                return
            
            # Convert Date column to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(self.data['Date']):
                self.data['Date'] = pd.to_datetime(self.data['Date'], errors='coerce')
            
            self.update_progress(30, "Processing data...")
            
            # Create report PDF
            today = dt.datetime.now().date()
            self.report_path = os.path.join(
                os.path.expanduser("~"), 
                "Documents", 
                f"TruckAccidentReport_{today.strftime('%Y%m%d')}.pdf"
            )
            os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
            
            self.update_progress(50, "Generating visualizations...")
            
            # Create PDF with temporary figures
            temp_dir = tempfile.mkdtemp()
            self.generate_pdf_report(self.report_path, temp_dir)
            
            self.update_progress(90, "Completing report...")
            
            # Enable preview and email buttons
            self.root.after(0, lambda: self.preview_button.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.email_button.configure(state=tk.NORMAL))
            
            self.update_progress(100, f"Report generated: {self.report_path}")
            
            # Show popup notification
            self.root.after(0, lambda: messagebox.showinfo(
                "Success", 
                f"Report generated successfully!\n\nSaved to: {self.report_path}"
            ))
            
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_pdf_report(self, output_path, temp_dir):
        """Generate the PDF report with all required sections"""
        # Get today's date and data
        today = dt.datetime.now().date()
        
        # Filter for today's accidents
        today_accidents = self.data[self.data['Date'].dt.date == today].copy()  # Make a copy to avoid SettingWithCopyWarning
        today_accidents['Date'] = today_accidents['Date'].dt.date  # Remove time component
        
        # Create document
        doc = SimpleDocTemplate(output_path, pagesize=landscape(letter))  # Use landscape for better fit
        styles = getSampleStyleSheet()
        
        # Create custom styles
        if 'CustomTitle' not in styles:
            styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                alignment=TA_CENTER,
                spaceAfter=20
            ))
        
        if 'CustomSubtitle' not in styles:
            styles.add(ParagraphStyle(
                name='CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12
            ))
        
        # Create smaller style for tables
        if 'TableText' not in styles:
            styles.add(ParagraphStyle(
                name='TableText',
                parent=styles['Normal'],
                fontSize=8,
                leading=10
            ))
        
        # Create content list for document
        content = []
        
        # Add title
        content.append(Paragraph(f"Truck Accident Report - {today.strftime('%B %d, %Y')}", styles['CustomTitle']))
        
        # Add summary section (using only today's data)
        if not today_accidents.empty:
            content.append(Paragraph("Daily Summary Statistics", styles['CustomSubtitle']))
            
            # Create summary statistics table using today's data only
            fault_stats = today_accidents.groupby('Fault').size().reset_index(name='Count')
            fault_stats = fault_stats.rename(columns={'Fault': 'Driver Fault'})
            
            truck_type_stats = today_accidents.groupby('Truck type').size().reset_index(name='Count')
            
            # Create fault statistics table
            fault_data = [['Driver Fault', 'Count']]
            for _, row in fault_stats.iterrows():
                fault_data.append([row['Driver Fault'], str(row['Count'])])
                
            fault_table = Table(fault_data, colWidths=[2*inch, 1*inch], style=[
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ])
            
            # Create truck type statistics table
            truck_data = [['Truck Type', 'Count']]
            for _, row in truck_type_stats.iterrows():
                truck_data.append([row['Truck type'], str(row['Count'])])
                
            truck_table = Table(truck_data, colWidths=[2*inch, 1*inch], style=[
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ])
            
            # Create a larger table to hold both statistic tables side by side
            stat_tables = Table([[fault_table, truck_table]], colWidths=[3.5*inch, 3.5*inch])
            stat_tables.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            content.append(stat_tables)
            content.append(Spacer(1, 0.2*inch))
        
        # Add new accidents table if there are any today
        content.append(Paragraph("New Accidents Today", styles['CustomSubtitle']))
        
        if not today_accidents.empty:
            # Create formatted data for table with smaller font
            table_data = [list(today_accidents.columns)]
            for _, row in today_accidents.iterrows():
                table_data.append([str(row[col]) for col in today_accidents.columns])
            
            # Adjusted column widths for better fit (reduced Fault column, increased Type column)
            col_widths = [1.5*inch, 1.5*inch, 1.5*inch, 1.0*inch, 0.8*inch, 1.2*inch, 3.0*inch]  # Adjusted Fault and Type columns
            
            # Create table with smaller font
            today_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            today_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('WORDWRAP', (0, 0), (-1, -1), True),
                ('FONTSIZE', (0, 0), (-1, -1), 8),  # Smaller font size
            ]))
            content.append(today_table)
        else:
            content.append(Paragraph("No new accidents reported today.", styles['Normal']))
        
        content.append(Spacer(1, 0.3*inch))
        
        # Add page break before charts and leaderboards
        content.append(PageBreak())
        
        # Add both charts to the report with title
        content.append(Paragraph("Monthly Comparison and Daily Trend", styles['CustomTitle']))
        
        # Generate monthly comparison chart (larger size)
        current_month = today.month
        current_year = today.year
        
        self.data['Month'] = self.data['Date'].dt.month
        self.data['Year'] = self.data['Date'].dt.year
        
        # Group by month and count accidents
        monthly_counts = self.data.groupby(['Year', 'Month']).size().reset_index(name='Count')
        
        # Get current month data
        current_month_data = monthly_counts[
            (monthly_counts['Month'] == current_month) & 
            (monthly_counts['Year'] == current_year)
        ]
        
        # Get previous months data (exclude current month)
        prev_months_data = monthly_counts[
            ~((monthly_counts['Month'] == current_month) & 
            (monthly_counts['Year'] == current_year))
        ]
        
        # Calculate previous months average
        prev_avg = prev_months_data['Count'].mean() if not prev_months_data.empty else 0
        current_count = current_month_data['Count'].iloc[0] if not current_month_data.empty else 0
        
        # Create monthly comparison chart (larger size)
        fig1, ax1 = plt.subplots(figsize=(8, 5))  # Increased size
        labels = ['Previous Months Avg', f'Current Month ({dt.datetime(current_year, current_month, 1).strftime("%B")})']
        values = [prev_avg, current_count]
        
        bars = ax1.bar(labels, values, color=['#5DA5DA', '#FAA43A'])
        
        # Add value labels above bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}', ha='center', va='bottom')
        
        ax1.set_ylabel('Number of Accidents', fontsize=12)
        ax1.set_title('Current Month vs. Previous Months Average', fontsize=14)
        plt.xticks(fontsize=10)
        fig1.tight_layout()
        
        # Save figure to temporary file
        monthly_chart_path = os.path.join(temp_dir, 'monthly_chart.png')
        fig1.savefig(monthly_chart_path, dpi=120, bbox_inches='tight')  # Higher DPI
        plt.close(fig1)
        
        # Generate daily trend chart for last 30 days (larger size)
        last_30days = today - dt.timedelta(days=30)
        last_month_data = self.data[self.data['Date'].dt.date >= last_30days]
        
        # Group by date and count accidents
        daily_counts = last_month_data.groupby(last_month_data['Date'].dt.date).size().reset_index(name='Count')
        daily_counts = daily_counts.sort_values('Date')
        
        # Create daily trend chart (larger size)
        fig2, ax2 = plt.subplots(figsize=(8, 5))  # Increased size
        ax2.plot(daily_counts['Date'], daily_counts['Count'], marker='o', linestyle='-', color='#4285F4')
        
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Number of Accidents', fontsize=12)
        ax2.set_title('Daily Accident Count (Last 30 Days)', fontsize=14)
        ax2.tick_params(axis='x', rotation=45, labelsize=10)
        ax2.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Format x-axis to show fewer date labels
        plt.gcf().autofmt_xdate()
        fig2.tight_layout()
        
        # Save figure to temporary file
        daily_chart_path = os.path.join(temp_dir, 'daily_chart.png')
        fig2.savefig(daily_chart_path, dpi=120, bbox_inches='tight')  # Higher DPI
        plt.close(fig2)
        
        # Create image objects from saved figures
        monthly_img = Image(monthly_chart_path, width=4.5*inch, height=3*inch)  # Larger images
        daily_img = Image(daily_chart_path, width=4.5*inch, height=3*inch)      # Larger images
        
        # Add images side by side in a table
        chart_table = Table([[monthly_img, daily_img]], colWidths=[4.5*inch, 4.5*inch])
        chart_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        content.append(chart_table)
        content.append(Spacer(1, 0.5*inch))
        
        # Start leaderboards on a new page
        content.append(PageBreak())
        
        # Driver leaderboards section (all on one page)
        content.append(Paragraph("Driver Accident Leaderboards", styles['CustomTitle']))
        content.append(Spacer(1, 0.2*inch))
        
        # Generate top 20 drivers overall
        driver_overall = self.data.groupby('Driver').size().reset_index(name='Count')
        driver_overall = driver_overall.sort_values('Count', ascending=False).head(20)

        # Generate top 5 drivers for current month
        current_month_drivers = self.data[
            (self.data['Date'].dt.month == current_month) & 
            (self.data['Date'].dt.year == current_year)
        ]
        
        driver_monthly = current_month_drivers.groupby('Driver').size().reset_index(name='Count')
        driver_monthly = driver_monthly.sort_values('Count', ascending=False).head(5)

        # Create a single table structure that includes both titles and tables
        leaderboard_content = [
            [Paragraph("Top 20 Drivers by Total Accidents", styles['CustomSubtitle']), 
             Paragraph(f"Top 5 Drivers in {today.strftime('%B %Y')}", styles['CustomSubtitle'])],
            [self._create_driver_table(driver_overall, "Total"), 
             self._create_driver_table(driver_monthly, today.strftime('%B'))]
        ]

        leaderboard_table = Table(leaderboard_content, colWidths=[4.5*inch, 4.5*inch])
        leaderboard_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),  # Space after titles
        ]))

        content.append(leaderboard_table)
        
        # Build the document
        doc.build(content)
        
        # Save the chart paths for preview
        self.preview_images = [monthly_chart_path, daily_chart_path]
        
        return output_path

    def _create_driver_table(self, data, count_header):
        """Helper method to create a driver table"""
        table_data = [['Rank', 'Driver', count_header]]
        for idx, (_, row) in enumerate(data.iterrows(), 1):
            table_data.append([str(idx), row['Driver'], str(row['Count'])])
            
        table = Table(table_data, colWidths=[0.5*inch, 3.5*inch, 0.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, 3), colors.lightgrey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        return table

    def preview_report(self):
        """Show a preview of the generated report"""
        if not self.report_path or not os.path.exists(self.report_path):
            messagebox.showerror("Error", "No report to preview. Please generate a report first.")
            return
        
        try:
            # Clear previous preview content
            for widget in self.preview_canvas.winfo_children():
                widget.destroy()
            
            self.preview_canvas.delete("all")
            
            # Create a frame to hold preview images
            preview_container = tk.Frame(self.preview_canvas, bg="white")
            self.preview_canvas.create_window((0, 0), window=preview_container, anchor="nw")
            
            # Load and display the figures
            for i, img_path in enumerate(self.preview_images):
                # Load image
                pil_img = PILImage.open(img_path)
                pil_img.thumbnail((400, 300))  # Larger preview size
                
                # Convert to tkinter PhotoImage
                tk_img = ImageTk.PhotoImage(pil_img)
                
                # Keep a reference to prevent garbage collection
                if not hasattr(self, 'tk_images'):
                    self.tk_images = []
                self.tk_images.append(tk_img)
                
                # Create and place label with image
                img_label = tk.Label(preview_container, image=tk_img, bg="white")
                img_label.grid(row=0, column=i, padx=10, pady=10)
                
                # Add caption
                caption = "Monthly Comparison" if i == 0 else "Daily Trend"
                caption_label = tk.Label(preview_container, text=caption, bg="white", font=('Helvetica', 10, 'bold'))
                caption_label.grid(row=1, column=i)
            
            # Add a note about PDF
            note_label = tk.Label(preview_container, 
                                text=f"Full PDF report saved to:\n{self.report_path}", 
                                bg="white", fg="blue", font=('Helvetica', 10))
            note_label.grid(row=2, column=0, columnspan=2, pady=10)
            
            # Add button to open the PDF
            open_pdf_btn = ttk.Button(preview_container, text="Open PDF", 
                                     command=lambda: os.startfile(self.report_path))
            open_pdf_btn.grid(row=3, column=0, columnspan=2, pady=5)
            
            # Update scrollregion
            preview_container.update_idletasks()
            self.preview_canvas.config(scrollregion=self.preview_canvas.bbox("all"))
            
            # Configure canvas scrolling
            self.preview_canvas.configure(yscrollcommand=self.v_scrollbar.set,
                                        xscrollcommand=self.h_scrollbar.set)
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Could not display preview: {str(e)}")

    def show_email_dialog(self):
        """Show dialog to send email"""
        if not self.report_path or not os.path.exists(self.report_path):
            messagebox.showerror("Error", "No report to send. Please generate a report first.")
            return
            
        # Create email dialog window
        email_dialog = tk.Toplevel(self.root)
        email_dialog.title("Send Report via Email")
        email_dialog.geometry("500x400")
        email_dialog.transient(self.root)
        email_dialog.grab_set()
        
        # Add close button to email dialog
        email_dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_email_dialog(email_dialog))
        
        # Email form
        form_frame = ttk.Frame(email_dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # To field
        ttk.Label(form_frame, text="To:").grid(row=0, column=0, sticky=tk.W, pady=5)
        to_var = tk.StringVar()
        to_entry = ttk.Entry(form_frame, textvariable=to_var, width=40)
        to_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Subject field
        ttk.Label(form_frame, text="Subject:").grid(row=1, column=0, sticky=tk.W, pady=5)
        subject_var = tk.StringVar(value=f"Truck Accident Report - {dt.datetime.now().strftime('%B %d, %Y')}")
        subject_entry = ttk.Entry(form_frame, textvariable=subject_var, width=40)
        subject_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Body field
        ttk.Label(form_frame, text="Message:").grid(row=2, column=0, sticky=tk.W+tk.N, pady=5)
        body_text = tk.Text(form_frame, height=10, width=40)
        body_text.grid(row=2, column=1, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)
        
        # Default email body
        default_body = (
            "Dear Team,\n\n"
            "Attached is the daily truck accident report generated on "
            f"{dt.datetime.now().strftime('%B %d, %Y')}.\n\n"
            "The report includes:\n"
            "- Summary of new accidents\n"
            "- Monthly accident statistics\n"
            "- Daily trend for the last 30 days\n"
            "- Driver accident leaderboards\n\n"
            "Please review at your earliest convenience.\n\n"
            "Best regards,\n"
            "Safety Department\n"
            "Your Company Name\n"
            "safety@yourcompany.com\n"
            "555-123-4567"
        )
        body_text.insert(tk.END, default_body)
        
        # Scrollbar for body
        body_scroll = ttk.Scrollbar(form_frame, orient=tk.VERTICAL, command=body_text.yview)
        body_scroll.grid(row=2, column=2, sticky=tk.N+tk.S)
        body_text.config(yscrollcommand=body_scroll.set)
        
        # Attachment label
        attachment_label = ttk.Label(form_frame, 
                                   text=f"Attachment: {os.path.basename(self.report_path)}")
        attachment_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Button frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Send button
        send_button = ttk.Button(button_frame, text="Send Email", 
                              command=lambda: self.send_email(
                                  to_var.get(), 
                                  subject_var.get(), 
                                  body_text.get("1.0", tk.END),
                                  email_dialog  # Pass dialog reference
                              ))
        send_button.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", 
                                command=lambda: self.close_email_dialog(email_dialog))
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        form_frame.rowconfigure(2, weight=1)
        
        # Focus to field
        to_entry.focus_set()

    def close_email_dialog(self, dialog):
        """Close the email dialog"""
        if hasattr(self, 'tk_images'):
            del self.tk_images  # Clean up image references
        dialog.destroy()

    def send_email(self, recipients, subject, body, email_dialog=None):
        """Send the report via Outlook"""
        if not recipients:
            messagebox.showerror("Error", "Please provide at least one email recipient")
            return
            
        try:
            self.status_var.set("Sending email...")
            
            # Create Outlook application object
            outlook = win32com.client.Dispatch("Outlook.Application")
            
            # Create a new mail item
            mail = outlook.CreateItem(0)  # 0: olMailItem
            
            # Set properties
            mail.To = recipients
            mail.Subject = subject
            mail.Body = body
            
            # Add attachment
            mail.Attachments.Add(self.report_path)
            
            # Send
            mail.Send()
            
            self.status_var.set("Email sent successfully!")
            messagebox.showinfo("Success", "Email sent successfully!")
            
            # Close email dialog if it exists
            if email_dialog:
                self.close_email_dialog(email_dialog)
            
        except Exception as e:
            self.status_var.set(f"Error sending email: {str(e)}")
            messagebox.showerror("Email Error", f"Failed to send email: {str(e)}")

    def on_close(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.root.destroy()

if __name__ == "__main__":
    # Set up the application
    root = tk.Tk()
    app = TruckAccidentReporter(root)
    root.mainloop()