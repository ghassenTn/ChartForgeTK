import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ChartForgeTK import (
    BarChart, LineChart, PieChart, TableauChart, 
    ScatterPlot, Histogram, BoxPlot, BubbleChart
)
import random
from datetime import datetime, timedelta
import json

class SalesDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Enterprise Analytics Dashboard - ChartForgeTK")
        self.geometry("1500x950")
        self.configure(bg="#0f0f1a")
        self.minsize(1300, 850)
        
        # Data storage
        self.historical_data = self.generate_historical_data()
        self.notifications = []
        self.theme = "dark"
        
        # Configure styles
        self.setup_styles()
        
        # Create UI
        self.create_header()
        self.create_main_content()
        self.create_footer()
        
        # Initialize
        self.auto_refresh_enabled = False
        self.update_clock()
        self.add_notification("Dashboard loaded successfully", "success")
    
    def generate_historical_data(self):
        """Generate realistic historical data"""
        data = {
            "daily_sales": [],
            "products": ["Widget Pro", "Gadget X", "Tool Kit", "Accessory Pack", "Premium Suite"],
            "regions": ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"],
        }
        
        # Generate 30 days of data
        base_date = datetime.now() - timedelta(days=30)
        for i in range(30):
            date = base_date + timedelta(days=i)
            data["daily_sales"].append({
                "date": date.strftime("%Y-%m-%d"),
                "revenue": random.randint(8000, 15000),
                "orders": random.randint(50, 150),
                "visitors": random.randint(500, 2000)
            })
        
        return data
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        self.colors = {
            "bg_dark": "#0f0f1a",
            "bg_card": "#1a1a2e",
            "bg_hover": "#252542",
            "accent": "#6366f1",
            "accent_hover": "#4f46e5",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "text": "#ffffff",
            "text_muted": "#94a3b8",
            "border": "#2d2d44"
        }
        
        # Notebook
        style.configure('TNotebook', background=self.colors["bg_dark"], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.colors["bg_card"], 
                       foreground=self.colors["text"],
                       padding=[25, 12],
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors["accent"])],
                 foreground=[('selected', 'white')])
        
        # Buttons
        style.configure('Accent.TButton',
                       background=self.colors["accent"],
                       foreground='white',
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        
        # Combobox
        style.configure('TCombobox',
                       background=self.colors["bg_card"],
                       foreground=self.colors["text"],
                       fieldbackground=self.colors["bg_card"])

    def create_header(self):
        """Create the application header"""
        header = tk.Frame(self, bg=self.colors["bg_card"], height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Left - Logo and title
        left_frame = tk.Frame(header, bg=self.colors["bg_card"])
        left_frame.pack(side="left", padx=25, pady=15)
        
        # Animated logo effect
        logo_frame = tk.Frame(left_frame, bg=self.colors["accent"], width=45, height=45)
        logo_frame.pack(side="left")
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="📊", font=("Segoe UI", 20), 
                bg=self.colors["accent"], fg="white").place(relx=0.5, rely=0.5, anchor="center")
        
        title_frame = tk.Frame(left_frame, bg=self.colors["bg_card"])
        title_frame.pack(side="left", padx=(15, 0))
        tk.Label(title_frame, text="Enterprise Analytics", font=("Segoe UI", 18, "bold"), 
                bg=self.colors["bg_card"], fg="white").pack(anchor="w")
        tk.Label(title_frame, text="Real-time Business Intelligence", font=("Segoe UI", 10), 
                bg=self.colors["bg_card"], fg=self.colors["text_muted"]).pack(anchor="w")
        
        # Center - Search bar
        search_frame = tk.Frame(header, bg=self.colors["bg_card"])
        search_frame.pack(side="left", expand=True, padx=50)
        
        search_container = tk.Frame(search_frame, bg=self.colors["bg_dark"], padx=2, pady=2)
        search_container.pack()
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_container, textvariable=self.search_var,
                               font=("Segoe UI", 11), width=40,
                               bg=self.colors["bg_dark"], fg=self.colors["text"],
                               insertbackground="white", relief="flat", bd=10)
        search_entry.pack(side="left")
        search_entry.insert(0, "🔍  Search metrics, reports, data...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, "end") if "Search" in search_entry.get() else None)
        
        # Right - Controls
        right_frame = tk.Frame(header, bg=self.colors["bg_card"])
        right_frame.pack(side="right", padx=25, pady=15)
        
        # Notifications bell
        self.notif_btn = tk.Button(right_frame, text="🔔", font=("Segoe UI", 14),
                                   bg=self.colors["bg_card"], fg="white", bd=0,
                                   activebackground=self.colors["bg_hover"],
                                   cursor="hand2", command=self.show_notifications)
        self.notif_btn.pack(side="left", padx=(0, 15))
        
        # Theme toggle
        self.theme_btn = tk.Button(right_frame, text="🌙", font=("Segoe UI", 14),
                                   bg=self.colors["bg_card"], fg="white", bd=0,
                                   activebackground=self.colors["bg_hover"],
                                   cursor="hand2", command=self.toggle_theme)
        self.theme_btn.pack(side="left", padx=(0, 15))
        
        # Clock
        self.clock_label = tk.Label(right_frame, text="", font=("Segoe UI", 10), 
                                    bg=self.colors["bg_card"], fg=self.colors["text_muted"])
        self.clock_label.pack(side="left", padx=(0, 20))
        
        # Auto refresh
        self.auto_refresh_var = tk.BooleanVar(value=False)
        auto_frame = tk.Frame(right_frame, bg=self.colors["bg_card"])
        auto_frame.pack(side="left", padx=(0, 15))
        
        ttk.Checkbutton(auto_frame, text="Live", variable=self.auto_refresh_var,
                       command=self.toggle_auto_refresh).pack()
        
        # Refresh button
        refresh_btn = tk.Button(right_frame, text="⟳ Refresh", font=("Segoe UI", 10, "bold"),
                               bg=self.colors["accent"], fg="white", bd=0,
                               activebackground=self.colors["accent_hover"],
                               cursor="hand2", padx=20, pady=8,
                               command=self.refresh_all)
        refresh_btn.pack(side="left")

    def create_main_content(self):
        """Create the main content area"""
        main_frame = tk.Frame(self, bg=self.colors["bg_dark"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=(10, 0))
        
        # Left sidebar
        sidebar = tk.Frame(main_frame, bg=self.colors["bg_dark"], width=240)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)
        
        self.create_sidebar(sidebar)
        
        # Main content
        content = tk.Frame(main_frame, bg=self.colors["bg_dark"])
        content.pack(side="left", fill="both", expand=True)
        
        # Notebook
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill="both", expand=True)
        
        self.create_overview_tab()
        self.create_analytics_tab()
        self.create_reports_tab()
        self.create_settings_tab()
    
    def create_sidebar(self, parent):
        """Create the sidebar with stats and actions"""
        # Stats section
        stats_header = tk.Frame(parent, bg=self.colors["bg_dark"])
        stats_header.pack(fill="x", pady=(0, 15))
        tk.Label(stats_header, text="KEY METRICS", font=("Segoe UI", 9, "bold"),
                bg=self.colors["bg_dark"], fg=self.colors["text_muted"]).pack(side="left")
        
        # Time filter
        self.time_filter = ttk.Combobox(stats_header, values=["Today", "This Week", "This Month", "This Year"],
                                        width=10, state="readonly")
        self.time_filter.set("This Month")
        self.time_filter.pack(side="right")
        self.time_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_all())
        
        # Stat cards
        self.stat_widgets = {}
        stats = [
            ("revenue", "💰", "Total Revenue", "$142,580", "+14.2%", self.colors["success"]),
            ("orders", "📦", "Total Orders", "1,847", "+8.5%", self.colors["success"]),
            ("customers", "👥", "Active Users", "12,459", "+22.1%", self.colors["success"]),
            ("conversion", "🎯", "Conversion", "3.42%", "-0.3%", self.colors["danger"]),
            ("avg_order", "💳", "Avg. Order", "$77.20", "+5.8%", self.colors["success"]),
            ("bounce", "↩️", "Bounce Rate", "32.1%", "-2.4%", self.colors["success"]),
        ]
        
        for key, icon, title, value, change, change_color in stats:
            card = self.create_stat_card(parent, icon, title, value, change, change_color)
            self.stat_widgets[key] = card
        
        # Separator
        tk.Frame(parent, bg=self.colors["border"], height=1).pack(fill="x", pady=20)
        
        # Quick actions
        tk.Label(parent, text="QUICK ACTIONS", font=("Segoe UI", 9, "bold"),
                bg=self.colors["bg_dark"], fg=self.colors["text_muted"]).pack(anchor="w", pady=(0, 10))
        
        actions = [
            ("📊 Generate Report", self.generate_report),
            ("📥 Export Data", self.export_data),
            ("📧 Email Summary", self.email_summary),
            ("🔔 Set Alert", self.set_alert),
            ("📅 Schedule Report", self.schedule_report),
        ]
        
        for text, command in actions:
            btn = tk.Button(parent, text=text, font=("Segoe UI", 10),
                           bg=self.colors["bg_card"], fg="white", bd=0,
                           activebackground=self.colors["accent"],
                           cursor="hand2", anchor="w", padx=15, pady=10,
                           command=command)
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.colors["bg_hover"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors["bg_card"]))
    
    def create_stat_card(self, parent, icon, title, value, change, change_color):
        """Create a stat card widget"""
        card = tk.Frame(parent, bg=self.colors["bg_card"])
        card.pack(fill="x", pady=4)
        
        # Left - Icon
        icon_frame = tk.Frame(card, bg=self.colors["bg_hover"], width=40, height=40)
        icon_frame.pack(side="left", padx=10, pady=10)
        icon_frame.pack_propagate(False)
        tk.Label(icon_frame, text=icon, font=("Segoe UI", 14),
                bg=self.colors["bg_hover"]).place(relx=0.5, rely=0.5, anchor="center")
        
        # Middle - Title and value
        content = tk.Frame(card, bg=self.colors["bg_card"])
        content.pack(side="left", fill="x", expand=True, pady=10)
        
        tk.Label(content, text=title, font=("Segoe UI", 9),
                bg=self.colors["bg_card"], fg=self.colors["text_muted"]).pack(anchor="w")
        value_label = tk.Label(content, text=value, font=("Segoe UI", 14, "bold"),
                              bg=self.colors["bg_card"], fg="white")
        value_label.pack(anchor="w")
        
        # Right - Change
        change_label = tk.Label(card, text=change, font=("Segoe UI", 9, "bold"),
                               bg=self.colors["bg_card"], fg=change_color)
        change_label.pack(side="right", padx=10)
        
        return {"card": card, "value": value_label, "change": change_label}

    def create_overview_tab(self):
        """Create the overview dashboard tab"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg_dark"])
        self.notebook.add(tab, text="  📈 Overview  ")
        
        # Top row - 2 charts
        top_row = tk.Frame(tab, bg=self.colors["bg_dark"])
        top_row.pack(fill="both", expand=True, pady=(10, 5))
        
        # Revenue Chart
        revenue_card = self.create_chart_card(top_row, "Revenue Overview", 
                                              "Monthly revenue performance", 
                                              ["Export", "Fullscreen"])
        revenue_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        self.bar_chart = BarChart(revenue_card, width=500, height=320, theme="dark")
        self.bar_chart.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.bar_chart.plot([125, 148, 132, 165, 178, 195], 
                           ["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
        
        # Trends Chart
        trends_card = self.create_chart_card(top_row, "Performance Trends", 
                                             "Sales, costs, and profit margins",
                                             ["Compare", "Export"])
        trends_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        
        self.line_chart = LineChart(trends_card, width=500, height=320, theme="dark")
        self.line_chart.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.line_chart.plot([
            {'data': [45, 52, 48, 61, 55, 72, 68, 75], 'color': '#6366f1', 'shape': 'circle', 'label': 'Revenue'},
            {'data': [30, 35, 32, 40, 38, 45, 42, 48], 'color': '#ef4444', 'shape': 'square', 'label': 'Costs'},
            {'data': [15, 17, 16, 21, 17, 27, 26, 27], 'color': '#10b981', 'shape': 'diamond', 'label': 'Profit'}
        ])
        
        # Bottom row - 3 charts
        bottom_row = tk.Frame(tab, bg=self.colors["bg_dark"])
        bottom_row.pack(fill="both", expand=True, pady=(5, 10))
        
        # Pie Chart
        pie_card = self.create_chart_card(bottom_row, "Market Distribution", 
                                          "Revenue by product category")
        pie_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        self.pie_chart = PieChart(pie_card, width=350, height=280, theme="dark")
        self.pie_chart.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.pie_chart.plot([32, 28, 18, 14, 8], 
                           ["Electronics", "Software", "Services", "Hardware", "Other"])
        
        # Bubble Chart
        bubble_card = self.create_chart_card(bottom_row, "Product Performance", 
                                             "Size = Revenue, Position = Growth vs Margin")
        bubble_card.pack(side="left", fill="both", expand=True, padx=8)
        
        self.bubble_chart = BubbleChart(bubble_card, width=350, height=280, theme="dark")
        self.bubble_chart.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        bubble_data = [(random.uniform(20, 80), random.uniform(10, 50), random.uniform(10, 40)) for _ in range(8)]
        self.bubble_chart.plot(bubble_data)
        
        # Table
        table_card = self.create_chart_card(bottom_row, "Recent Transactions", 
                                            "Latest order activity")
        table_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        
        self.tableau_chart = TableauChart(table_card, width=350, height=280, theme="dark")
        self.tableau_chart.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.tableau_chart.plot([
            {"Product": "Widget Pro", "Qty": 45, "Revenue": "$2,250"},
            {"Product": "Gadget X", "Qty": 32, "Revenue": "$1,600"},
            {"Product": "Tool Kit", "Qty": 28, "Revenue": "$1,400"},
        ])
    
    def create_analytics_tab(self):
        """Create the analytics tab"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg_dark"])
        self.notebook.add(tab, text="  📊 Analytics  ")
        
        # Top row
        top_row = tk.Frame(tab, bg=self.colors["bg_dark"])
        top_row.pack(fill="both", expand=True, pady=(10, 5))
        
        # Scatter Plot
        scatter_card = self.create_chart_card(top_row, "Correlation Analysis", 
                                              "Price vs Quantity relationship")
        scatter_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        self.scatter_chart = ScatterPlot(scatter_card, width=500, height=350, theme="dark")
        self.scatter_chart.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        scatter_data = [(random.uniform(10, 100), random.uniform(5, 50)) for _ in range(25)]
        self.scatter_chart.plot(scatter_data)
        
        # Histogram
        hist_card = self.create_chart_card(top_row, "Order Value Distribution", 
                                           "Frequency analysis of order amounts")
        hist_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        
        self.histogram = Histogram(hist_card, width=500, height=350, theme="dark")
        self.histogram.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        hist_data = [random.gauss(75, 25) for _ in range(150)]
        self.histogram.plot(hist_data, bins=12)
        
        # Bottom row
        bottom_row = tk.Frame(tab, bg=self.colors["bg_dark"])
        bottom_row.pack(fill="both", expand=True, pady=(5, 10))
        
        # Box Plot
        box_card = self.create_chart_card(bottom_row, "Regional Performance", 
                                          "Statistical distribution by region")
        box_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        self.box_chart = BoxPlot(box_card, width=500, height=350, theme="dark")
        self.box_chart.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        box_data = [
            sorted([random.uniform(50, 150) for _ in range(20)]),
            sorted([random.uniform(60, 180) for _ in range(20)]),
            sorted([random.uniform(40, 120) for _ in range(20)]),
            sorted([random.uniform(70, 200) for _ in range(20)]),
        ]
        self.box_chart.plot(box_data, ["North", "South", "East", "West"])
        
        # Regional Bar
        regional_card = self.create_chart_card(bottom_row, "Sales by Region", 
                                               "Comparative regional performance")
        regional_card.pack(side="left", fill="both", expand=True, padx=(8, 0))
        
        self.regional_chart = BarChart(regional_card, width=500, height=350, theme="dark")
        self.regional_chart.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.regional_chart.plot([95, 128, 87, 142, 76], 
                                ["NA", "EU", "APAC", "LATAM", "MEA"])

    def create_reports_tab(self):
        """Create the reports tab"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg_dark"])
        self.notebook.add(tab, text="  📋 Reports  ")
        
        # Header
        header = tk.Frame(tab, bg=self.colors["bg_dark"])
        header.pack(fill="x", pady=20, padx=20)
        
        tk.Label(header, text="Generated Reports", font=("Segoe UI", 18, "bold"),
                bg=self.colors["bg_dark"], fg="white").pack(side="left")
        
        tk.Button(header, text="+ New Report", font=("Segoe UI", 10, "bold"),
                 bg=self.colors["accent"], fg="white", bd=0,
                 activebackground=self.colors["accent_hover"],
                 cursor="hand2", padx=20, pady=8,
                 command=self.generate_report).pack(side="right")
        
        # Reports list
        reports_frame = tk.Frame(tab, bg=self.colors["bg_dark"])
        reports_frame.pack(fill="both", expand=True, padx=20)
        
        reports = [
            ("Monthly Sales Report", "Dec 1, 2024", "PDF", "2.4 MB", self.colors["success"]),
            ("Q4 Performance Analysis", "Nov 28, 2024", "Excel", "1.8 MB", self.colors["success"]),
            ("Customer Segmentation", "Nov 25, 2024", "PDF", "3.1 MB", self.colors["success"]),
            ("Revenue Forecast 2025", "Nov 20, 2024", "PDF", "1.2 MB", self.colors["warning"]),
            ("Inventory Status", "Nov 15, 2024", "Excel", "4.5 MB", self.colors["success"]),
            ("Marketing ROI Analysis", "Nov 10, 2024", "PDF", "2.8 MB", self.colors["success"]),
        ]
        
        # Table header
        header_frame = tk.Frame(reports_frame, bg=self.colors["bg_card"])
        header_frame.pack(fill="x", pady=(0, 2))
        
        headers = [("Report Name", 300), ("Date", 150), ("Format", 100), ("Size", 100), ("Status", 100), ("Actions", 150)]
        for text, width in headers:
            tk.Label(header_frame, text=text, font=("Segoe UI", 10, "bold"),
                    bg=self.colors["bg_card"], fg=self.colors["text_muted"],
                    width=width//10, anchor="w").pack(side="left", padx=15, pady=12)
        
        # Report rows
        for name, date, fmt, size, status_color in reports:
            row = tk.Frame(reports_frame, bg=self.colors["bg_card"])
            row.pack(fill="x", pady=1)
            
            tk.Label(row, text=f"📄 {name}", font=("Segoe UI", 10),
                    bg=self.colors["bg_card"], fg="white",
                    width=30, anchor="w").pack(side="left", padx=15, pady=12)
            tk.Label(row, text=date, font=("Segoe UI", 10),
                    bg=self.colors["bg_card"], fg=self.colors["text_muted"],
                    width=15, anchor="w").pack(side="left", padx=15, pady=12)
            tk.Label(row, text=fmt, font=("Segoe UI", 10),
                    bg=self.colors["bg_card"], fg=self.colors["text_muted"],
                    width=10, anchor="w").pack(side="left", padx=15, pady=12)
            tk.Label(row, text=size, font=("Segoe UI", 10),
                    bg=self.colors["bg_card"], fg=self.colors["text_muted"],
                    width=10, anchor="w").pack(side="left", padx=15, pady=12)
            tk.Label(row, text="● Ready", font=("Segoe UI", 10),
                    bg=self.colors["bg_card"], fg=status_color,
                    width=10, anchor="w").pack(side="left", padx=15, pady=12)
            
            actions = tk.Frame(row, bg=self.colors["bg_card"])
            actions.pack(side="left", padx=15)
            tk.Button(actions, text="📥", font=("Segoe UI", 10),
                     bg=self.colors["bg_card"], fg="white", bd=0,
                     cursor="hand2").pack(side="left", padx=2)
            tk.Button(actions, text="👁", font=("Segoe UI", 10),
                     bg=self.colors["bg_card"], fg="white", bd=0,
                     cursor="hand2").pack(side="left", padx=2)
            tk.Button(actions, text="🗑", font=("Segoe UI", 10),
                     bg=self.colors["bg_card"], fg="white", bd=0,
                     cursor="hand2").pack(side="left", padx=2)
    
    def create_settings_tab(self):
        """Create the settings tab"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg_dark"])
        self.notebook.add(tab, text="  ⚙️ Settings  ")
        
        # Settings container
        container = tk.Frame(tab, bg=self.colors["bg_dark"])
        container.pack(fill="both", expand=True, padx=40, pady=30)
        
        # General Settings
        general_frame = tk.LabelFrame(container, text="  General Settings  ", 
                                      font=("Segoe UI", 11, "bold"),
                                      bg=self.colors["bg_card"], fg="white",
                                      padx=20, pady=15)
        general_frame.pack(fill="x", pady=(0, 20))
        
        settings = [
            ("Dashboard refresh interval", ["5 seconds", "10 seconds", "30 seconds", "1 minute"]),
            ("Default date range", ["Today", "This Week", "This Month", "This Year"]),
            ("Chart animation speed", ["Fast", "Normal", "Slow", "None"]),
            ("Number format", ["1,234.56", "1.234,56", "1234.56"]),
        ]
        
        for label, options in settings:
            row = tk.Frame(general_frame, bg=self.colors["bg_card"])
            row.pack(fill="x", pady=8)
            tk.Label(row, text=label, font=("Segoe UI", 10),
                    bg=self.colors["bg_card"], fg="white").pack(side="left")
            combo = ttk.Combobox(row, values=options, width=20, state="readonly")
            combo.set(options[1])
            combo.pack(side="right")
        
        # Notification Settings
        notif_frame = tk.LabelFrame(container, text="  Notifications  ", 
                                    font=("Segoe UI", 11, "bold"),
                                    bg=self.colors["bg_card"], fg="white",
                                    padx=20, pady=15)
        notif_frame.pack(fill="x", pady=(0, 20))
        
        notif_options = [
            ("Email alerts for threshold breaches", True),
            ("Daily summary reports", True),
            ("Weekly performance digest", False),
            ("Real-time anomaly detection", True),
        ]
        
        for text, default in notif_options:
            row = tk.Frame(notif_frame, bg=self.colors["bg_card"])
            row.pack(fill="x", pady=5)
            var = tk.BooleanVar(value=default)
            ttk.Checkbutton(row, text=text, variable=var).pack(side="left")
        
        # Save button
        tk.Button(container, text="Save Settings", font=("Segoe UI", 11, "bold"),
                 bg=self.colors["accent"], fg="white", bd=0,
                 activebackground=self.colors["accent_hover"],
                 cursor="hand2", padx=30, pady=12,
                 command=lambda: self.add_notification("Settings saved successfully", "success")).pack(pady=20)

    def create_chart_card(self, parent, title, subtitle="", actions=None):
        """Create a styled chart card with header"""
        card = tk.Frame(parent, bg=self.colors["bg_card"])
        
        # Header
        header = tk.Frame(card, bg=self.colors["bg_card"])
        header.pack(fill="x", padx=15, pady=(15, 0))
        
        # Title section
        title_frame = tk.Frame(header, bg=self.colors["bg_card"])
        title_frame.pack(side="left")
        
        tk.Label(title_frame, text=title, font=("Segoe UI", 12, "bold"),
                bg=self.colors["bg_card"], fg="white").pack(anchor="w")
        if subtitle:
            tk.Label(title_frame, text=subtitle, font=("Segoe UI", 9),
                    bg=self.colors["bg_card"], fg=self.colors["text_muted"]).pack(anchor="w")
        
        # Action buttons
        if actions:
            actions_frame = tk.Frame(header, bg=self.colors["bg_card"])
            actions_frame.pack(side="right")
            for action in actions:
                btn = tk.Button(actions_frame, text=action, font=("Segoe UI", 8),
                               bg=self.colors["bg_hover"], fg=self.colors["text_muted"],
                               bd=0, padx=10, pady=3, cursor="hand2")
                btn.pack(side="left", padx=2)
        
        return card
    
    def create_footer(self):
        """Create the application footer"""
        footer = tk.Frame(self, bg=self.colors["bg_card"], height=40)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        # Left - Status
        left = tk.Frame(footer, bg=self.colors["bg_card"])
        left.pack(side="left", padx=20)
        tk.Label(left, text="●", font=("Segoe UI", 8), 
                bg=self.colors["bg_card"], fg=self.colors["success"]).pack(side="left")
        tk.Label(left, text=" Connected", font=("Segoe UI", 9),
                bg=self.colors["bg_card"], fg=self.colors["text_muted"]).pack(side="left")
        
        # Center - Branding
        tk.Label(footer, text="Powered by ChartForgeTK v2.0.0  •  Pure Tkinter  •  Zero Dependencies", 
                font=("Segoe UI", 9), bg=self.colors["bg_card"], 
                fg=self.colors["text_muted"]).pack(expand=True)
        
        # Right - Version
        tk.Label(footer, text="v1.0.0", font=("Segoe UI", 9),
                bg=self.colors["bg_card"], fg=self.colors["text_muted"]).pack(side="right", padx=20)
    
    # ==================== FUNCTIONALITY ====================
    
    def update_clock(self):
        """Update the clock display"""
        now = datetime.now().strftime("%a, %b %d  •  %I:%M:%S %p")
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh"""
        self.auto_refresh_enabled = self.auto_refresh_var.get()
        if self.auto_refresh_enabled:
            self.add_notification("Live mode enabled - refreshing every 5s", "info")
            self.auto_refresh()
        else:
            self.add_notification("Live mode disabled", "info")
    
    def auto_refresh(self):
        """Auto-refresh charts"""
        if self.auto_refresh_enabled:
            self.refresh_all(silent=True)
            self.after(5000, self.auto_refresh)
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.add_notification("Theme toggle coming soon!", "info")
    
    def show_notifications(self):
        """Show notifications panel"""
        if not self.notifications:
            messagebox.showinfo("Notifications", "No new notifications")
        else:
            msg = "\n".join([f"• {n['message']}" for n in self.notifications[-5:]])
            messagebox.showinfo("Recent Notifications", msg)
    
    def add_notification(self, message, type="info"):
        """Add a notification"""
        self.notifications.append({
            "message": message,
            "type": type,
            "time": datetime.now()
        })
    
    def refresh_all(self, silent=False):
        """Refresh all charts and stats"""
        # Update stats
        stats_data = {
            "revenue": (f"${random.randint(120000, 180000):,}", f"+{random.uniform(5, 20):.1f}%"),
            "orders": (f"{random.randint(1500, 2500):,}", f"+{random.uniform(3, 15):.1f}%"),
            "customers": (f"{random.randint(10000, 15000):,}", f"+{random.uniform(10, 30):.1f}%"),
            "conversion": (f"{random.uniform(2.5, 4.5):.2f}%", f"{random.choice(['+', '-'])}{random.uniform(0.1, 1):.1f}%"),
            "avg_order": (f"${random.uniform(60, 100):.2f}", f"+{random.uniform(2, 10):.1f}%"),
            "bounce": (f"{random.uniform(25, 40):.1f}%", f"-{random.uniform(1, 5):.1f}%"),
        }
        
        for key, (value, change) in stats_data.items():
            if key in self.stat_widgets:
                self.stat_widgets[key]["value"].config(text=value)
                color = self.colors["success"] if "+" in change or (key == "bounce" and "-" in change) else self.colors["danger"]
                self.stat_widgets[key]["change"].config(text=change, fg=color)
        
        # Refresh charts
        self.bar_chart.plot([random.randint(100, 200) for _ in range(6)],
                           ["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
        
        self.line_chart.plot([
            {'data': [random.randint(40, 80) for _ in range(8)], 'color': '#6366f1', 'shape': 'circle', 'label': 'Revenue'},
            {'data': [random.randint(25, 50) for _ in range(8)], 'color': '#ef4444', 'shape': 'square', 'label': 'Costs'},
            {'data': [random.randint(10, 30) for _ in range(8)], 'color': '#10b981', 'shape': 'diamond', 'label': 'Profit'}
        ])
        
        self.pie_chart.plot([random.randint(15, 40) for _ in range(5)],
                           ["Electronics", "Software", "Services", "Hardware", "Other"])
        
        bubble_data = [(random.uniform(20, 80), random.uniform(10, 50), random.uniform(10, 40)) for _ in range(8)]
        self.bubble_chart.plot(bubble_data)
        
        self.tableau_chart.plot([
            {"Product": p, "Qty": random.randint(20, 60), "Revenue": f"${random.randint(1000, 3000):,}"}
            for p in ["Widget Pro", "Gadget X", "Tool Kit"]
        ])
        
        scatter_data = [(random.uniform(10, 100), random.uniform(5, 50)) for _ in range(25)]
        self.scatter_chart.plot(scatter_data)
        
        hist_data = [random.gauss(75, 25) for _ in range(150)]
        self.histogram.plot(hist_data, bins=12)
        
        box_data = [sorted([random.uniform(50, 180) for _ in range(20)]) for _ in range(4)]
        self.box_chart.plot(box_data, ["North", "South", "East", "West"])
        
        self.regional_chart.plot([random.randint(70, 150) for _ in range(5)],
                                ["NA", "EU", "APAC", "LATAM", "MEA"])
        
        if not silent:
            self.add_notification("Dashboard refreshed successfully", "success")
    
    # Placeholder actions
    def generate_report(self):
        self.add_notification("Generating report...", "info")
        messagebox.showinfo("Report", "Report generation started!\nYou'll be notified when ready.")
    
    def export_data(self):
        file = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON", "*.json"), ("CSV", "*.csv")])
        if file:
            self.add_notification(f"Data exported to {file}", "success")
            messagebox.showinfo("Export", f"Data exported successfully to:\n{file}")
    
    def email_summary(self):
        messagebox.showinfo("Email", "Email summary feature coming soon!")
    
    def set_alert(self):
        messagebox.showinfo("Alerts", "Alert configuration coming soon!")
    
    def schedule_report(self):
        messagebox.showinfo("Schedule", "Report scheduling coming soon!")


if __name__ == "__main__":
    app = SalesDashboard()
    app.mainloop()
