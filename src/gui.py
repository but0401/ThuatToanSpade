import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import pandas as pd
from datetime import datetime
from PIL import Image, ImageTk
import os
import sv_ttk  # Thư viện theme hiện đại cho tkinter
from tkcalendar import DateEntry  # Add this import for date picker

from data_processing import load_and_process_data
from spade_algorithm import SPADEAlgorithm
from visualization import create_visualizations
from recommendation import generate_recommendations_from_sequences

class SPADEApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("SPADE Data Mining Application")
        self.geometry("800x600")
        self.minsize(1024, 700)
        
        # Áp dụng theme Sun Valley
        sv_ttk.set_theme("light")
        
        # Tạo font styles
        self.font_header = ('Segoe UI', 12, 'bold')
        self.font_subheader = ('Segoe UI', 10, 'bold')
        self.font_normal = ('Segoe UI', 9)
        
        # Thiết lập màu sắc
        self.color_highlight = "#1976d2"
        self.color_bg_light = "#f5f5f5"
        
        self.data = None
        self.cleaned_data = None
        self.spade = None
        self.standard_products = None
        
        # Thiết lập icon cho phần cửa sổ (nếu có)
        # try:
        #     self.iconbitmap("path/to/icon.ico")
        # except:
        #     pass
            
        # Tạo notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Thêm các tab hiện có
        self.create_widgets()
        
        # Thêm tab nhập dữ liệu mới
        self.data_entry_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_entry_frame, text="Import Data")
        
        # Thiết lập giao diện nhập dữ liệu
        self.setup_data_entry_ui()
    
    def create_widgets(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel for input and parameters with improved styling
        left_frame = ttk.LabelFrame(main_frame, text="Controls", padding="15")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # File input section with improved layout
        file_frame = ttk.LabelFrame(left_frame, text="Input Data", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(file_frame, text="CSV File:", font=self.font_normal).pack(anchor=tk.W, pady=(0, 5))
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X)
        
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(file_select_frame, text="Browse...", command=self.browse_file, style="Accent.TButton")
        browse_btn.pack(side=tk.RIGHT)
        
        # Parameters section with improved styling
        param_frame = ttk.LabelFrame(left_frame, text="Algorithm Parameters", padding="10")
        param_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(param_frame, text="Minimum Support:", font=self.font_normal).pack(anchor=tk.W, pady=(0, 5))
        
        self.min_support = tk.DoubleVar(value=0.01)
        support_frame = ttk.Frame(param_frame)
        support_frame.pack(fill=tk.X)
        
        support_entry = ttk.Entry(support_frame, textvariable=self.min_support, width=10)
        support_entry.pack(side=tk.LEFT)
        
        ttk.Label(support_frame, text="(0-1 range)", foreground="gray").pack(side=tk.LEFT, padx=(5, 0))
        
        # Buttons section with improved styling and icons
        button_frame = ttk.LabelFrame(left_frame, text="Actions", padding="10")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Load Data", command=self.load_data, style="TButton").pack(fill=tk.X, pady=(0, 8))
        ttk.Button(button_frame, text="Clean Data", command=self.clean_data, style="TButton").pack(fill=tk.X, pady=(0, 8))
        ttk.Button(button_frame, text="Run SPADE Algorithm", command=self.run_spade, style="Accent.TButton").pack(fill=tk.X, pady=(0, 8))
        ttk.Button(button_frame, text="Generate Statistics", command=self.generate_statistics, style="TButton").pack(fill=tk.X)
        
        # Create modern styled notebook for different tabs
        self.notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Data tab
        self.data_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.data_tab, text="Data")
        
        # Results tab
        self.results_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.results_tab, text="Frequent Patterns")
        
        # Statistics tab
        self.stats_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.stats_tab, text="Statistics")
        
        # Visualization tab
        self.viz_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.viz_tab, text="Visualizations")
        
        # Recommendations tab
        self.rec_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(self.rec_tab, text="Recommendations")
        
        # Improved status bar with progress indicator
        status_frame = ttk.Frame(self)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var, anchor=tk.W, padding=(10, 5)).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def load_standard_products(self):
        """Load standard products from data.csv"""
        product_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "data.csv")
        try:
            self.standard_products = pd.read_csv(product_data_path)
            return True
        except Exception as e:
            print(f"Warning: Could not load standard products: {e}")
            self.standard_products = None
            return False

    def setup_data_entry_ui(self):
        # Frame containing the data entry form
        entry_frame = ttk.LabelFrame(self.data_entry_frame, text="New Order Information")
        entry_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Load standard products
        have_standards = self.load_standard_products()
        
        # Create input fields
        self.entries = {}
        
        # Generate auto-incrementing invoice number
        next_invoice_no = self.get_next_invoice_number()
        
        # Modified field list
        fields = [
            ("InvoiceNo", "Invoice Number (auto):"), 
            ("Description", "Product Description:"), 
            ("StockCode", "Product Code:"), 
            ("Quantity", "Quantity:"), 
            ("InvoiceDate", "Date and Time:"),
            ("UnitPrice", "Unit Price:"), 
            ("CustomerID", "Customer ID:"), 
            ("Country", "Country:")
        ]
        
        # Create labels and entry fields
        for i, (field, label) in enumerate(fields):
            ttk.Label(entry_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            
            # Special handling for InvoiceNo (auto-generated, read-only)
            if field == "InvoiceNo":
                self.entries[field] = ttk.Entry(entry_frame, width=50)
                self.entries[field].insert(0, str(next_invoice_no))
                self.entries[field].configure(state="readonly")
                self.entries[field].grid(row=i, column=1, padx=5, pady=5)
                
            # Special handling for Description (dropdown + entry)
            elif field == "Description" and have_standards:
                desc_frame = ttk.Frame(entry_frame)
                desc_frame.grid(row=i, column=1, sticky=tk.W, padx=5, pady=5)
                
                self.description_var = tk.StringVar()
                
                # Create combo box with standard descriptions
                descriptions = self.standard_products['Description'].tolist()
                
                desc_combo = ttk.Combobox(desc_frame, textvariable=self.description_var, width=47)
                desc_combo['values'] = descriptions
                desc_combo.pack(side=tk.LEFT)
                
                # Bind selection event to update StockCode and UnitPrice
                desc_combo.bind("<<ComboboxSelected>>", self.update_product_info)
                
                # Enable type-ahead search in dropdown
                def handle_keypress(event):
                    if event.widget == desc_combo:
                        if event.char.isalnum():
                            typed = event.char.upper()
                            for idx, item in enumerate(descriptions):
                                if str(item).upper().startswith(typed):
                                    desc_combo.current(idx)
                                    break

                desc_combo.bind('<KeyPress>', handle_keypress)
                
                # Store the combobox in entries dict
                self.entries[field] = desc_combo
                    
            # Special handling for StockCode (may be auto-populated)
            elif field == "StockCode" and have_standards:
                self.entries[field] = ttk.Entry(entry_frame, width=50)
                self.entries[field].grid(row=i, column=1, padx=5, pady=5)
                
            # Special handling for UnitPrice (may be auto-populated)
            elif field == "UnitPrice" and have_standards:
                self.entries[field] = ttk.Entry(entry_frame, width=50)
                self.entries[field].grid(row=i, column=1, padx=5, pady=5)
                
            # Special handling for InvoiceDate (date picker)
            elif field == "InvoiceDate":
                # Create a frame to hold date and time components
                date_frame = ttk.Frame(entry_frame)
                date_frame.grid(row=i, column=1, sticky=tk.W, padx=5, pady=5)
                
                # Add date picker
                self.date_picker = DateEntry(
                    date_frame, 
                    width=12, 
                    background=self.color_highlight,
                    foreground='white', 
                    borderwidth=2, 
                    date_pattern='yyyy-mm-dd'
                )
                self.date_picker.pack(side=tk.LEFT, padx=(0, 10))
                
                # Add time entry (hours and minutes)
                time_frame = ttk.Frame(date_frame)
                time_frame.pack(side=tk.LEFT)
                
                ttk.Label(time_frame, text="Time:").pack(side=tk.LEFT, padx=(0, 5))
                
                # Hours combobox
                self.hour_var = tk.StringVar()
                hour_combo = ttk.Combobox(time_frame, textvariable=self.hour_var, width=2)
                hour_combo['values'] = [f"{i:02d}" for i in range(24)]  # 00-23 hours
                hour_combo.pack(side=tk.LEFT)
                hour_combo.set(datetime.now().strftime("%H"))
                
                ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
                
                # Minutes combobox
                self.minute_var = tk.StringVar()
                minute_combo = ttk.Combobox(time_frame, textvariable=self.minute_var, width=2)
                minute_combo['values'] = [f"{i:02d}" for i in range(0, 60, 5)]  # 00-55 minutes (5 min increments)
                minute_combo.pack(side=tk.LEFT)
                minute_combo.set(datetime.now().strftime("%M"))
                
                # Create a hidden entry to store the formatted date+time
                self.entries[field] = ttk.Entry(entry_frame)
                
            else:
                # Standard entry fields for other inputs
                self.entries[field] = ttk.Entry(entry_frame, width=50)
                self.entries[field].grid(row=i, column=1, padx=5, pady=5)
            
        # Preset country field
        self.entries["Country"].insert(0, "Vietnam")
        
        # Save data button
        save_button = ttk.Button(entry_frame, text="Save Data", command=self.save_data)
        save_button.grid(row=len(fields), column=1, sticky=tk.E, padx=5, pady=10)
        
        # Clear form button
        clear_button = ttk.Button(entry_frame, text="Clear Form", command=self.clear_form)
        clear_button.grid(row=len(fields), column=0, sticky=tk.W, padx=5, pady=10)

    def update_product_info(self, event):
        """Auto-populate product details when a Description is selected"""
        if not hasattr(self, 'standard_products') or self.standard_products is None:
            return
            
        selected_description = self.description_var.get()
        
        # Find the product in the standard list
        product = self.standard_products[self.standard_products['Description'] == selected_description]
        
        if len(product) > 0:
            # Update StockCode
            self.entries["StockCode"].delete(0, tk.END)
            self.entries["StockCode"].insert(0, product["StockCode"].iloc[0])
            
            # Update UnitPrice
            self.entries["UnitPrice"].delete(0, tk.END)
            self.entries["UnitPrice"].insert(0, str(product["UnitPrice"].iloc[0]))
            
            # Provide visual feedback that fields were auto-populated
            self.entries["StockCode"].config(foreground="blue")
            self.entries["UnitPrice"].config(foreground="blue")
            
            # Schedule reset of text color after a short delay
            self.after(1500, self.reset_field_colors)

    def reset_field_colors(self):
        """Reset text colors back to default after visual feedback"""
        if "StockCode" in self.entries:
            self.entries["StockCode"].config(foreground="")
        if "UnitPrice" in self.entries:
            self.entries["UnitPrice"].config(foreground="")

    def get_next_invoice_number(self):
        """Generate the next invoice number based on existing data"""
        try:
            # Path to CSV file
            csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_data.csv")
            
            # Check if file exists
            if not os.path.exists(csv_path):
                return 100001  # Starting invoice number if file doesn't exist
            
            # Read existing CSV file
            df = pd.read_csv(csv_path)
            
            # If there are no invoice numbers or column doesn't exist
            if 'InvoiceNo' not in df.columns or len(df) == 0:
                return 100001
                
            # Get the highest invoice number (excluding those starting with 'C' for cancellations)
            numeric_invoices = df[~df['InvoiceNo'].astype(str).str.startswith('C')]['InvoiceNo']
            
            if len(numeric_invoices) == 0:
                return 100001
                
            # Convert to integers where possible and find max
            try:
                max_invoice = max(int(inv) for inv in numeric_invoices if str(inv).isdigit())
                return max_invoice + 1
            except:
                # If there's an error (e.g., non-numeric invoice numbers), start from a default
                return 100001
                
        except Exception as e:
            print(f"Error generating invoice number: {str(e)}")
            return 100001  # Default in case of error

    def validate_data(self):
        """Validate the entered data"""
        try:
            # Format the date+time value before validation
            if hasattr(self, 'date_picker'):
                selected_date = self.date_picker.get_date()
                hour = self.hour_var.get()
                minute = self.minute_var.get()
                
                # Format as "YYYY-MM-DD HH:MM"
                formatted_datetime = f"{selected_date.strftime('%Y-%m-%d')} {hour}:{minute}"
                
                # Update the hidden InvoiceDate entry with the formatted value
                self.entries["InvoiceDate"].delete(0, tk.END)
                self.entries["InvoiceDate"].insert(0, formatted_datetime)
            
            # Check quantity if it's not empty
            if self.entries["Quantity"].get().strip():
                try:
                    quantity = int(self.entries["Quantity"].get())
                    if quantity <= 0:
                        messagebox.showerror("Error", "Quantity must be a positive integer")
                        return False
                except ValueError:
                    messagebox.showerror("Error", "Quantity must be an integer")
                    return False
                    
            # Check unit price if it's not empty
            if self.entries["UnitPrice"].get().strip():
                try:
                    unit_price = float(self.entries["UnitPrice"].get())
                    if unit_price <= 0:
                        messagebox.showerror("Error", "Unit price must be greater than 0")
                        return False
                except ValueError:
                    messagebox.showerror("Error", "Unit price must be a number")
                    return False
            
            # Date format is already validated by the date picker
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error validating data: {str(e)}")
            return False

    def save_data(self):
        """Save data to CSV file"""
        if not self.validate_data():
            return
            
        try:
            # Path to CSV file
            csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_data.csv")
            
            # Prepare data for writing to file
            new_data = {field: entry.get() for field, entry in self.entries.items()}
            
            # Read existing CSV file
            try:
                df = pd.read_csv(csv_path)
            except FileNotFoundError:
                # Create new DataFrame if file doesn't exist
                df = pd.DataFrame(columns=list(self.entries.keys()))
            
            # Add new data to DataFrame
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            
            # Save DataFrame to CSV file
            df.to_csv(csv_path, index=False)
            
            messagebox.showinfo("Success", "Data saved successfully!")
            
            # Clear form and generate next invoice number
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save data: {str(e)}")

    def clear_form(self):
        """Clear data in the form and reset to defaults"""
        # Generate new invoice number for next entry
        next_invoice_no = self.get_next_invoice_number()
        
        # Reset invoice number field
        self.entries["InvoiceNo"].configure(state="normal")
        self.entries["InvoiceNo"].delete(0, tk.END)
        self.entries["InvoiceNo"].insert(0, str(next_invoice_no))
        self.entries["InvoiceNo"].configure(state="readonly")
        
        # Clear other fields
        for field, entry in self.entries.items():
            if field != "InvoiceNo":  # Skip invoice number as it's already handled
                entry.delete(0, tk.END)
        
        # Reset date picker to current date
        if hasattr(self, 'date_picker'):
            today = datetime.now().date()
            self.date_picker.set_date(today)
            
            # Reset time to current time
            current_time = datetime.now()
            self.hour_var.set(current_time.strftime("%H"))
            self.minute_var.set(current_time.strftime("%M"))
        
        # Reset default value for Country
        self.entries["Country"].insert(0, "Vietnam")
        
        # Reset text colors
        self.reset_field_colors()
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.status_var.set(f"Selected file: {filename}")
    
    def load_data(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file first.")
            return
        
        try:
            self.status_var.set("Loading data...")
            self.update_idletasks()
            
            # Load data
            self.data = pd.read_csv(file_path)
            
            # Display data in the data tab
            self.display_data(self.data)
            
            self.status_var.set(f"Loaded {len(self.data)} rows successfully.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.status_var.set("Error loading data.")
    
    def display_data(self, df, tab=None):
        if tab is None:
            tab = self.data_tab
        
        # Clear tab
        for widget in tab.winfo_children():
            widget.destroy()
        
        # Thêm thông tin tóm tắt
        info_frame = ttk.Frame(tab, padding=(10, 5))
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text="Dataset Overview", font=self.font_header, foreground=self.color_highlight).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Rows: {len(df):,} | Columns: {len(df.columns)}", font=self.font_normal).pack(anchor=tk.W, pady=(0, 10))
        
        # Create frame for data table
        frame = ttk.Frame(tab, padding=(10, 0))
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for displaying data with improved styling
        columns = list(df.columns)
        tree = ttk.Treeview(frame, columns=columns, show="headings", style="Treeview")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack scrollbars and treeview
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure columns and headings with better styling
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            # Thay đổi chiều rộng tùy theo loại dữ liệu
            if df[col].dtype in [int, float] or 'date' in col.lower():
                tree.column(col, width=80, anchor=tk.E)
            elif 'id' in col.lower():
                tree.column(col, width=70)
            elif 'descr' in col.lower() or 'name' in col.lower():
                tree.column(col, width=200)
            else:
                tree.column(col, width=120)
        
        # Insert data (first 1000 rows for performance) with alternating row colors
        for i, row in df.head(1000).iterrows():
            values = [str(row[col]) for col in columns]
            tree.insert("", tk.END, values=values, tags=('even' if i % 2 == 0 else 'odd',))
        
        # Configure row tags for alternating colors
        tree.tag_configure('even', background='#f5f5f5')
        tree.tag_configure('odd', background='white')
        
        # Show info about displayed rows
        if len(df) > 1000:
            status_frame = ttk.Frame(tab, padding=(10, 5))
            status_frame.pack(fill=tk.X)
            ttk.Label(status_frame, 
                    text=f"Showing first 1,000 of {len(df):,} rows", 
                    foreground="gray").pack(anchor=tk.W)
    
    def clean_data(self):
        if self.data is None:
            messagebox.showerror("Error", "Please load data first.")
            return
        
        try:
            self.status_var.set("Cleaning data...")
            self.update_idletasks()
            
            # Make a copy of the data
            df = self.data.copy()
            
            # 1. Handle missing values
            df = df.dropna(subset=['CustomerID', 'StockCode', 'InvoiceNo'])
            
            # 2. Convert data types
            df['CustomerID'] = df['CustomerID'].astype(int)
            
            # 3. Convert InvoiceDate to datetime
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
            
            # 4. Remove cancelled invoices (those starting with 'C')
            df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
            
            # 5. Remove rows with negative or zero quantities
            df = df[df['Quantity'] > 0]
            
            # 6. Remove rows with negative or zero prices
            df = df[df['UnitPrice'] > 0]
            
            # Store cleaned data
            self.cleaned_data = df
            
            # Display cleaned data
            self.display_data(self.cleaned_data)
            
            # Show before/after statistics
            before_count = len(self.data)
            after_count = len(self.cleaned_data)
            removed = before_count - after_count
            
            messagebox.showinfo(
                "Data Cleaning Results",
                f"Original rows: {before_count}\n"
                f"Cleaned rows: {after_count}\n"
                f"Removed rows: {removed} ({removed/before_count*100:.1f}%)"
            )
            
            self.status_var.set(f"Data cleaned: {after_count} rows remain.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cleaning data: {str(e)}")
            self.status_var.set("Error during data cleaning.")
    
    def run_spade(self):
        if self.cleaned_data is None:
            messagebox.showerror("Error", "Please clean the data first.")
            return
        
        try:
            self.status_var.set("Running SPADE algorithm...")
            self.update_idletasks()
            
            # Get minimum support parameter
            min_support = self.min_support.get()
            if min_support <= 0 or min_support > 1:
                messagebox.showerror("Error", "Minimum support must be between 0 and 1.")
                return
            
            # Initialize SPADE algorithm
            self.spade = SPADEAlgorithm(min_support=min_support)
            
            # Preprocess data
            self.spade.preprocess_data(self.cleaned_data)
            
            # Find frequent sequences
            frequent_sequences = self.spade.find_frequent_sequences()
            
            # Display results
            self.display_frequent_sequences(frequent_sequences)
            
            # Generate recommendations
            self.generate_recommendations()
            
            self.status_var.set(f"Found {len(frequent_sequences)} frequent sequences.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error running SPADE: {str(e)}")
            self.status_var.set("Error running SPADE algorithm.")
    
    def display_frequent_sequences(self, sequences):
        # Clear results tab
        for widget in self.results_tab.winfo_children():
            widget.destroy()
        
        # Create frame
        frame = ttk.Frame(self.results_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview
        tree = ttk.Treeview(frame, columns=["Sequence", "Support", "Items"], show="headings")
        
        # Add scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Pack scrollbars and treeview
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure columns
        tree.heading("Sequence", text="Sequence")
        tree.column("Sequence", width=100)
        tree.heading("Support", text="Support")
        tree.column("Support", width=100)
        tree.heading("Items", text="Items")
        tree.column("Items", width=400)
        
        # Insert data
        for i, (sequence, support) in enumerate(sequences):
            # Lookup product descriptions if available
            if 'Description' in self.cleaned_data.columns:
                items_desc = []
                for item in sequence:
                    desc = self.cleaned_data[self.cleaned_data['StockCode'] == item]['Description'].iloc[0] \
                        if len(self.cleaned_data[self.cleaned_data['StockCode'] == item]) > 0 else "Unknown"
                    items_desc.append(f"{item}: {desc}")
                items_str = " -> ".join(items_desc)
            else:
                items_str = " -> ".join(sequence)
            
            tree.insert("", tk.END, values=[str(sequence), f"{support:.4f}", items_str])
    
    def generate_statistics(self):
        if self.cleaned_data is None:
            messagebox.showerror("Error", "Please clean the data first.")
            return
        
        try:
            self.status_var.set("Generating statistics and visualizations...")
            self.update_idletasks()
            
            # Generate stats
            self.display_statistics()
            
            # Generate visualizations
            create_visualizations(self.cleaned_data, self.viz_tab)
            
            self.status_var.set("Statistics and visualizations generated.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating statistics: {str(e)}")
            self.status_var.set("Error generating statistics.")
    
    def display_statistics(self):
        # Clear stats tab
        for widget in self.stats_tab.winfo_children():
            widget.destroy()
        
        # Create container frame
        main_frame = ttk.Frame(self.stats_tab, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        ttk.Label(main_frame, text="Dataset Analytics", 
                 font=('Segoe UI', 16, 'bold'), 
                 foreground=self.color_highlight).pack(anchor=tk.W, pady=(0, 15))
        
        # Create scrollable frame for content
        canvas = tk.Canvas(main_frame, background=self.color_bg_light)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        
        content_frame = ttk.Frame(canvas)
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Overview section with better styling
        overview_frame = ttk.LabelFrame(content_frame, text="Overview", padding=15)
        overview_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a 2-column grid layout
        for i, (label, value) in enumerate([
            ("Total Transactions:", f"{self.cleaned_data['InvoiceNo'].nunique():,}"),
            ("Total Products:", f"{self.cleaned_data['StockCode'].nunique():,}"),
            ("Total Customers:", f"{self.cleaned_data['CustomerID'].nunique():,}"),
            ("Date Range:", f"{self.cleaned_data['InvoiceDate'].min().date()} to {self.cleaned_data['InvoiceDate'].max().date()}")
        ]):
            row, col = divmod(i, 2)
            ttk.Label(overview_frame, text=label, font=self.font_subheader).grid(row=row, column=col*2, sticky=tk.W, padx=(10 if col else 0, 5), pady=5)
            ttk.Label(overview_frame, text=value, font=self.font_normal).grid(row=row, column=col*2+1, sticky=tk.W, padx=5, pady=5)
        
        # Product statistics with better styling
        product_frame = ttk.LabelFrame(content_frame, text="Product Statistics", padding=15)
        product_frame.pack(fill=tk.X, padx=5, pady=5)
        
        product_counts = self.cleaned_data.groupby('StockCode')['Quantity'].sum().sort_values(ascending=False)
        
        # Basic product stats
        basic_prod_frame = ttk.Frame(product_frame)
        basic_prod_frame.pack(fill=tk.X)
        
        for i, (label, value) in enumerate([
            ("Average quantity per product:", f"{product_counts.mean():.2f}"),
            ("Median quantity per product:", f"{product_counts.median():.2f}")
        ]):
            row, col = divmod(i, 2)
            ttk.Label(basic_prod_frame, text=label, font=self.font_subheader).grid(row=row, column=col*2, sticky=tk.W, padx=(10 if col else 0, 5), pady=5)
            ttk.Label(basic_prod_frame, text=value, font=self.font_normal).grid(row=row, column=col*2+1, sticky=tk.W, padx=5, pady=5)
        
        # Top products table
        ttk.Label(product_frame, text="Top 10 Products by Quantity:", font=self.font_subheader).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Create modern styled treeview for top products
        top_prod_frame = ttk.Frame(product_frame)
        top_prod_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        cols = ["Rank", "Product Code", "Description", "Quantity"]
        tree = ttk.Treeview(top_prod_frame, columns=cols, show="headings", height=10)
        for col in cols:
            tree.heading(col, text=col)
        
        tree.column("Rank", width=50, anchor=tk.CENTER)
        tree.column("Product Code", width=100)
        tree.column("Description", width=300)
        tree.column("Quantity", width=100, anchor=tk.E)
        
        tree.pack(fill=tk.X)
        
        # Insert top products
        for i, (product, count) in enumerate(product_counts.head(10).items(), 1):
            desc = self.cleaned_data[self.cleaned_data['StockCode'] == product]['Description'].iloc[0] \
                if 'Description' in self.cleaned_data.columns and len(self.cleaned_data[self.cleaned_data['StockCode'] == product]) > 0 else "Unknown"
            tree.insert("", tk.END, values=[i, product, desc, f"{count:,}"], tags=('even' if i % 2 == 0 else 'odd',))
        
        # Configure row tags for alternating colors
        tree.tag_configure('even', background='#f5f5f5')
        tree.tag_configure('odd', background='white')
        
        # Add similar improved sections for Customer and Country statistics
        # [Code tương tự cho các phần thống kê khác]

        # Implement similar improvements for Customer and Country sections
    
    def generate_recommendations(self):
        if not hasattr(self, 'spade') or self.spade is None:
            return
        
        # Clear recommendations tab
        for widget in self.rec_tab.winfo_children():
            widget.destroy()
        
        # Create controls frame
        controls_frame = ttk.Frame(self.rec_tab)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Product selection dropdown
        ttk.Label(controls_frame, text="Select a product:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Get unique products
        products = sorted(self.cleaned_data['StockCode'].unique())
        
        # Create combobox
        self.selected_product = tk.StringVar()
        product_combo = ttk.Combobox(controls_frame, textvariable=self.selected_product, values=products, width=30)
        product_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        # Find button
        ttk.Button(controls_frame, text="Find Recommendations", 
                   command=self.show_product_recommendations).pack(side=tk.LEFT)
        
        # Results frame
        self.rec_results_frame = ttk.LabelFrame(self.rec_tab, text="Product Recommendations")
        self.rec_results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Initial message
        ttk.Label(self.rec_results_frame, 
                 text="Select a product and click 'Find Recommendations' to see products frequently purchased together.").pack(pady=20)
    
    def show_product_recommendations(self):
        product = self.selected_product.get()
        if not product:
            messagebox.showinfo("Info", "Please select a product first.")
            return
        
        # Clear previous results
        for widget in self.rec_results_frame.winfo_children():
            widget.destroy()
        
        # Find sequences containing the selected product
        recommendations = {}
        
        for seq, support in self.spade.frequent_sequences:
            if product in seq:
                # Find position of product in sequence
                pos = seq.index(product)
                
                # Get products that appear after the selected product
                for i in range(pos + 1, len(seq)):
                    next_item = seq[i]
                    if next_item != product:  # Don't recommend the same product
                        if next_item in recommendations:
                            recommendations[next_item] = max(recommendations[next_item], support)
                        else:
                            recommendations[next_item] = support
        
        # Sort recommendations by support
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_recs:
            # Hiển thị thông báo không có đề xuất với kiểu đẹp hơn
            no_rec_frame = ttk.Frame(self.rec_results_frame, padding=20)
            no_rec_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(no_rec_frame, 
                     text=f"No recommendations found for product {product}",
                     font=self.font_subheader).pack(pady=20)
            return
        
        # Get product description
        if 'Description' in self.cleaned_data.columns:
            prod_desc = self.cleaned_data[self.cleaned_data['StockCode'] == product]['Description'].iloc[0] \
                if len(self.cleaned_data[self.cleaned_data['StockCode'] == product]) > 0 else "Unknown"
            product_info = f"{product} ({prod_desc})"
        else:
            product_info = product
        
        # Tạo header có thiết kế đẹp hơn
        header_frame = ttk.Frame(self.rec_results_frame)
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        ttk.Label(header_frame, text="Recommendations for:", font=self.font_normal).pack(side=tk.LEFT)
        ttk.Label(header_frame, text=product_info, font=self.font_subheader, foreground=self.color_highlight).pack(side=tk.LEFT, padx=(5, 0))
        
        # Create frame for results with better styling
        results_frame = ttk.Frame(self.rec_results_frame, padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview với thiết kế hiện đại hơn
        tree = ttk.Treeview(results_frame, columns=["Rank", "Product", "Description", "Confidence"], show="headings", height=15)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        # Pack scrollbar and treeview
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure columns with better styling
        tree.heading("Rank", text="#")
        tree.column("Rank", width=40, anchor=tk.CENTER)
        tree.heading("Product", text="Product Code")
        tree.column("Product", width=100)
        tree.heading("Description", text="Description")
        tree.column("Description", width=300)
        tree.heading("Confidence", text="Confidence")
        tree.column("Confidence", width=100, anchor=tk.CENTER)
        
        # Insert recommendations with rank and alternating colors
        for i, (product, confidence) in enumerate(sorted_recs[:20], 1):  # Show top 20 recommendations
            if 'Description' in self.cleaned_data.columns:
                desc = self.cleaned_data[self.cleaned_data['StockCode'] == product]['Description'].iloc[0] \
                    if len(self.cleaned_data[self.cleaned_data['StockCode'] == product]) > 0 else "Unknown"
            else:
                desc = "N/A"
            
            tree.insert("", tk.END, values=[i, product, desc, f"{confidence:.4f}"], tags=('even' if i % 2 == 0 else 'odd',))
        
        # Configure row tags for alternating colors
        tree.tag_configure('even', background='#f5f5f5')
        tree.tag_configure('odd', background='white')