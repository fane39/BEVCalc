"""
BEV Calculator - PyQt5 Version
Application to compare cost-effectiveness of BEV and ICE vehicles.
"""
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QGroupBox, QFormLayout,
    QFileDialog, QMessageBox, QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
import matplotlib.ticker as mticker

from calculator import calculate_costs
import os
import json
import numpy as np
import sys

# --- Constants ---
PROFILES_DIR = "car_profiles"
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
SETTINGS_FILE = "theme_settings.json"

# --- Light Theme Colors ---
LIGHT_COLORS = {
    "primary": "#1976D2",
    "secondary": "#1565C0",
    "success": "#388E3C",
    "warning": "#F57C00",
    "error": "#D32F2F",
    "bev_line": "#1E88E5",
    "ice_line": "#E64A19",
    "chart_bg": "#F5F5F5",
    "text_primary": "#212121",
    "text_secondary": "#666666",
    "bg": "#FFFFFF",
    "input_bg": "#FFFFFF",
    "input_border": "#BDBDBD",
    "input_focus_bg": "#F5F5F5",
}

# --- Dark Theme Colors ---
DARK_COLORS = {
    "primary": "#1E88E5",
    "secondary": "#1565C0",
    "success": "#66BB6A",
    "warning": "#FFA726",
    "error": "#EF5350",
    "bev_line": "#42A5F5",
    "ice_line": "#FF7043",
    "chart_bg": "#2A2A2A",
    "text_primary": "#E0E0E0",
    "text_secondary": "#9E9E9E",
    "bg": "#1E1E1E",
    "input_bg": "#2A2A2A",
    "input_border": "#424242",
    "input_focus_bg": "#303030",
}


class BEVCalculatorPyQt5(QMainWindow):
    """PyQt5 BEV Calculator app."""
    
    # --- Default Values ---
    VEHICLE_ENTRIES = [
        ("bev_name", "BEV name", "Tesla Model 3"),
        ("ice_name", "ICE name", "VW Golf 8"),
        ("bev_price", "BEV price (€)", "40000"),
        ("ice_price", "ICE price (€)", "25000"),
        ("subsidy", "Subsidy (€)", "9000"),
        ("bev_maintenance", "BEV maintenance (€/yr)", "150"),
        ("ice_maintenance", "ICE maintenance (€/yr)", "400"),
    ]
    USAGE_ENTRIES = [
        ("annual_km", "Annual mileage (km)", "15000"),
        ("bev_consumption", "BEV consumption (kWh/100km)", "18"),
        ("ice_consumption", "ICE consumption (l/100km)", "7"),
        ("fuel_price", "Fuel price (€/l)", "1.5"),
    ]
    CHARGING_TYPES = [
        ("home_charge_pct", "home_charge_price", "Home", "80", "0.15"),
        ("public_ac_pct", "public_ac_price", "Public AC", "15", "0.40"),
        ("public_dc_pct", "public_dc_price", "Public DC", "5", "0.65"),
    ]
    STRING_PARAMS = {"bev_name", "ice_name"}
    CHARGING_PARAMS = {
        "home_charge_pct", "home_charge_price",
        "public_ac_pct", "public_ac_price",
        "public_dc_pct", "public_dc_price"
    }

    def __init__(self):
        """Inicijalizacija aplikacije."""
        super().__init__()
        os.makedirs(PROFILES_DIR, exist_ok=True)
        
        self.setWindowTitle("BEV Cost Calculator")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Inicijalizacija varijabli
        self.results = None
        self.bev_name = "BEV"
        self.ice_name = "ICE"
        self.inputs = {}
        self.charging_inputs = {}
        
        # Inicijalizacija teme
        self.dark_mode = self._load_theme_preference()
        self.colors = DARK_COLORS if self.dark_mode else LIGHT_COLORS
        
        # Kreiraj UI
        self._create_ui()
        self._apply_styles()
        
        # Inicijalni prikaz praznog grafikona
        self._clear_graph()

    def _apply_styles(self):
        """Apply CSS styles to the application."""
        c = self.colors
        # Dinamička boja teksta za load dugme ovisno o temi
        load_btn_color = "#FFFFFF" if self.dark_mode else "#000000"
        style = f"""
        QMainWindow {{
            background-color: {c['bg']};
        }}
        QGroupBox {{
            color: {c['text_primary']};
            font-weight: bold;
            border: 2px solid {c['secondary']};
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0px 5px;
        }}
        QLabel {{
            color: {c['text_primary']};
        }}
        QLineEdit {{
            background-color: {c['input_bg']};
            border: 1px solid {c['input_border']};
            border-radius: 4px;
            padding: 5px;
            color: {c['text_primary']};
        }}
        QLineEdit:focus {{
            border: 2px solid {c['primary']};
            background-color: {c['input_focus_bg']};
        }}
        QComboBox {{
            background-color: {c['input_bg']};
            border: 1px solid {c['input_border']};
            border-radius: 4px;
            padding: 5px;
            color: {c['text_primary']};
        }}
        QComboBox QAbstractItemView {{
            background-color: {c['input_bg']};
            color: {c['text_primary']};
            selection-background-color: {c['primary']};
        }}
        QPushButton {{
            background-color: {c['primary']};
            color: #000000;
            border: 2px solid {c['secondary']};
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            margin: 4px;
            font-size: 12px;
            outline: none;
        }}
        QPushButton:hover {{
            background-color: {c['secondary']};
            border: 2px solid {c['primary']};
            color: #000000 !important;
        }}
        QPushButton:pressed {{
            background-color: {c['secondary']};
            color: #000000 !important;
        }}
        QPushButton:focus {{
            outline: none;
            color: #000000 !important;
        }}
        #saveButton {{
            background-color: {c['success']};
            border: 2px solid {c['success']};
            color: white !important;
        }}
        #saveButton:hover {{
            background-color: {c['warning']};
            border: 2px solid {c['warning']};
            color: white !important;
        }}
        #deleteButton {{
            background-color: {c['error']};
            border: 2px solid {c['error']};
            color: white !important;
        }}
        #deleteButton:hover {{
            background-color: {c['warning']};
            border: 2px solid {c['warning']};
            color: white !important;
        }}
        #exportButton {{
            background-color: {c['warning']};
            border: 2px solid {c['warning']};
            color: #000000;
        }}
        #exportButton:hover {{
            background-color: {c['success']};
            border: 2px solid {c['success']};
            color: #000000 !important;
        }}
        #themeButton {{
            background-color: {c['primary']};
            border: 2px solid {c['secondary']};
            min-width: 40px;
            max-width: 120px;
            color: #000000;
        }}
        #calcButton {{
            color: {load_btn_color} !important;
        }}
        #calcButton:hover {{
            color: {load_btn_color} !important;
        }}
        #calcButton:pressed {{
            color: {load_btn_color} !important;
        }}
        #loadButton {{
            color: {load_btn_color} !important;
        }}
        #loadButton:hover {{
            color: {load_btn_color} !important;
        }}
        QScrollArea {{
            background-color: {c['bg']};
            border: none;
        }}
        QWidget {{
            background-color: {c['bg']};
        }}
        """
        self.setStyleSheet(style)

    def _create_ui(self):
        """Create main UI."""
        #Centalni widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Glavni layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Lijevi panel (Input)
        left_panel = self._create_input_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Desni panel (Output)
        right_panel = self._create_output_panel()
        main_layout.addWidget(right_panel, 2)

    def _create_input_panel(self):
        """Create input panel (left)."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)
        
        # Theme toggle button
        layout.addWidget(self._create_theme_group())
        
        # Profile section
        layout.addWidget(self._create_profile_group())
        
        # Vehicle data sekcija
        layout.addWidget(self._create_vehicle_group())
        
        # Usage sekcija
        layout.addWidget(self._create_usage_group())
        
        # Charging sekcija
        layout.addWidget(self._create_charging_group())
        
        # Warning label
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet(f"color: {self.colors['warning']}; font-weight: bold;")
        layout.addWidget(self.warning_label)
        
        # Buttons
        layout.addWidget(self._create_button_group())
        
        layout.addStretch()
        
        scroll_area.setWidget(container)
        return scroll_area

    def _create_profile_group(self):
        """Create profile management group."""
        group = QGroupBox("Load profile")
        layout = QVBoxLayout()
        
        # Combo box
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self._get_profiles_list() or ["No saved profiles"])
        layout.addWidget(self.profile_combo)
        
        # Button
        load_button = QPushButton("Load profile")
        load_button.setObjectName("loadButton")
        load_button.clicked.connect(self._load_profile)
        layout.addWidget(load_button)
        
        group.setLayout(layout)
        return group

    def _load_theme_preference(self):
        """Load preferred theme from file."""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    return settings.get("dark_mode", False)
        except Exception:
            pass
        return False

    def _save_theme_preference(self):
        """Save theme preference to file."""
        try:
            settings = {"dark_mode": self.dark_mode}
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f)
        except Exception:
            pass

    def _toggle_theme(self):
        """Toggle theme between light and dark."""
        self.dark_mode = not self.dark_mode
        self.colors = DARK_COLORS if self.dark_mode else LIGHT_COLORS
        self._save_theme_preference()
        self._apply_styles()
        
        # Ažuriraj grafikon ako postoji
        if self.results is not None:
            self._draw_graph(self.results)
        else:
            self._clear_graph()
        
        # Update theme button label
        self.theme_button.setText("☀️ Light" if self.dark_mode else "🌙 Dark")

    def _create_theme_group(self):
        """Create theme toggle group."""
        group = QGroupBox("Appearance")
        layout = QHBoxLayout()
        
        self.theme_button = QPushButton("🌙 Dark" if not self.dark_mode else "☀️ Light")
        self.theme_button.setObjectName("themeButton")
        self.theme_button.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_button)
        layout.addStretch()
        
        group.setLayout(layout)
        return group


    def _create_form_group(self, title, entries):
        """Generic method to create a form group."""
        group = QGroupBox(title)
        form = QFormLayout()
        
        for name, label, default in entries:
            line_edit = QLineEdit(default)
            line_edit.setMinimumWidth(250)
            self.inputs[name] = line_edit
            form.addRow(label + ":", line_edit)
        
        group.setLayout(form)
        return group

    def _create_vehicle_group(self):
        """Create group for vehicle data."""
        return self._create_form_group("Vehicle data", self.VEHICLE_ENTRIES)

    def _create_usage_group(self):
        """Create group for usage and consumption."""
        return self._create_form_group("Usage and consumption", self.USAGE_ENTRIES)

    def _create_charging_group(self):
        """Create charging settings group."""
        group = QGroupBox("BEV Charging settings")
        layout = QGridLayout()
        
        # Headers
        layout.addWidget(QLabel("Charging type"), 0, 0)
        layout.addWidget(QLabel("Share (%)"), 0, 1)
        layout.addWidget(QLabel("Price (€/kWh)"), 0, 2)
        
        # Rows
        for idx, (pct_name, price_name, text, pct_def, price_def) in enumerate(self.CHARGING_TYPES, 1):
            # Label
            layout.addWidget(QLabel(text), idx, 0)
            
            # Percentage input
            pct_input = QLineEdit(pct_def)
            pct_input.setMaximumWidth(100)
            self.charging_inputs[pct_name] = pct_input
            layout.addWidget(pct_input, idx, 1)
            
            # Price input
            price_input = QLineEdit(price_def)
            price_input.setMaximumWidth(150)
            self.charging_inputs[price_name] = price_input
            layout.addWidget(price_input, idx, 2)
        
        group.setLayout(layout)
        return group

    def _create_button_group(self):
        """Create action buttons group."""
        group = QGroupBox("Actions")
        layout = QHBoxLayout()
        
        # Calculate
        calc_button = QPushButton("Calculate")
        calc_button.setObjectName("calcButton")
        calc_button.clicked.connect(self._perform_calculation)
        layout.addWidget(calc_button)
        
        # Save
        save_button = QPushButton("Save profile")
        save_button.setObjectName("saveButton")
        save_button.clicked.connect(self._save_profile)
        layout.addWidget(save_button)
        
        # Delete
        delete_button = QPushButton("Delete profile")
        delete_button.setObjectName("deleteButton")
        delete_button.clicked.connect(self._delete_profile)
        layout.addWidget(delete_button)
        
        group.setLayout(layout)
        return group

    def _create_output_panel(self):
        """Kreiraj output panel (desno)."""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Results group
        layout.addWidget(self._create_results_group())
        
        # Export button
        export_button = QPushButton("Export as PNG")
        export_button.setObjectName("exportButton")
        export_button.clicked.connect(self._export_to_png)
        layout.addWidget(export_button)
        
        # Graph
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.fig.patch.set_facecolor(self.colors['chart_bg'])
        self.canvas = FigureCanvas(self.fig)
        
        toolbar = NavigationToolbar(self.canvas, panel)
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        
        return panel

    def _create_results_group(self):
        """Kreiraj grupu za prikaz rezultata."""
        group = QGroupBox("Results")
        layout = QVBoxLayout()
        
        # Breakeven label
        self.breakeven_label = QLabel("Break-even: -")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.breakeven_label.setFont(font)
        self.breakeven_label.setStyleSheet(f"color: {self.colors['primary']};")
        layout.addWidget(self.breakeven_label)
        
        # Annual costs labels
        self.bev_annual_label = QLabel("Annual cost BEV: -")
        self.ice_annual_label = QLabel("Annual cost ICE: -")
        
        # Styling za godišnje troškove
        annual_font = QFont()
        annual_font.setPointSize(11)
        annual_font.setBold(True)
        self.bev_annual_label.setFont(annual_font)
        self.ice_annual_label.setFont(annual_font)
        
        is_dark = self.dark_mode
        error_color = self.colors['error']
        bg_color = "#3D1F1F" if is_dark else "#FADBD8"
        self.bev_annual_label.setStyleSheet(f"color: {error_color}; background-color: {bg_color}; padding: 5px; border-radius: 3px;")
        self.ice_annual_label.setStyleSheet(f"color: {error_color}; background-color: {bg_color}; padding: 5px; border-radius: 3px;")
        
        layout.addWidget(self.bev_annual_label)
        layout.addWidget(self.ice_annual_label)
        
        group.setLayout(layout)
        return group

    def _get_profiles_list(self):
        """Get list of available profiles."""
        try:
            profiles = [
                f.replace(".json", "") for f in os.listdir(PROFILES_DIR)
                if f.endswith(".json")
            ]
            return sorted(profiles)
        except Exception:
            return []

    @staticmethod
    def _format_currency(value):
        """Format value as currency with localized separators."""
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _get_charging_values(self, keys):
        """Helper metoda za dohvaćanje više vrijednosti iz charging_inputs."""
        try:
            return tuple(float(self.charging_inputs[key].text()) for key in keys)
        except (ValueError, KeyError):
            return tuple(None for _ in keys)

    def _get_charging_percentages(self):
        """Dohvati i validiraj postotke punjenja."""
        pct_keys = ["home_charge_pct", "public_ac_pct", "public_dc_pct"]
        return self._get_charging_values(pct_keys)

    def _get_charging_prices(self):
        """Dohvati i validiraj cijene punjenja."""
        price_keys = ["home_charge_price", "public_ac_price", "public_dc_price"]
        return self._get_charging_values(price_keys)

    def _calculate_avg_electricity_price(self):
        """Calculate average electricity price."""
        home_pct, ac_pct, dc_pct = self._get_charging_percentages()
        if home_pct is None or ac_pct is None or dc_pct is None:
            return None, "Error reading charging percentages."

        total_pct = home_pct + ac_pct + dc_pct
        if abs(total_pct - 100.0) > 0.01:
            warning = f"⚠️ Warning: Sum of shares is {total_pct:.0f}%, should be 100%."
        else:
            warning = ""

        home_price, ac_price, dc_price = self._get_charging_prices()
        if home_price is None or ac_price is None or dc_price is None:
            return None, "Error reading charging prices."

        avg_price = (home_pct/100 * home_price) + (ac_pct/100 * ac_price) + (dc_pct/100 * dc_price)
        return avg_price, warning

    def _extract_numeric_params(self, avg_elec_price):
        """Ekstrahiraj i konvertiraj numeričke parametre."""
        numeric_params = {}
        int_params = {"annual_km", "bev_maintenance", "ice_maintenance"}

        try:
            # Vehicle entries
            for name, _, _ in self.VEHICLE_ENTRIES:
                if name not in self.STRING_PARAMS:
                    value = float(self.inputs[name].text())
                    numeric_params[name] = int(value) if name in int_params else value

            # Usage entries
            for name, _, _ in self.USAGE_ENTRIES:
                value = float(self.inputs[name].text())
                numeric_params[name] = int(value) if name in int_params else value

            numeric_params["electricity_price"] = avg_elec_price
            return numeric_params
        except (ValueError, KeyError) as e:
            return None

    def _get_vehicle_names(self):
        """Dohvati imena vozila."""
        bev_name = self.inputs["bev_name"].text() or "BEV"
        ice_name = self.inputs["ice_name"].text() or "ICE"
        return bev_name, ice_name

    def _setup_graph_background(self, ax):
        """Postavi background boje za grafikon."""
        ax.set_facecolor(self.colors['chart_bg'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.colors['text_secondary'])
        ax.spines['bottom'].set_color(self.colors['text_secondary'])

    def _plot_cost_lines(self, ax, results):
        """Plot cost lines."""
        bev_label = f"{self.bev_name} Total cost"
        ice_label = f"{self.ice_name} Total cost"
        ax.plot(results['years'], results['bev_costs'], label=bev_label,
                color=self.colors['bev_line'], linewidth=2.5, marker='o', markersize=4)
        ax.plot(results['years'], results['ice_costs'], label=ice_label,
                color=self.colors['ice_line'], linewidth=2.5, marker='s', markersize=4)

    def _plot_breakeven_point(self, ax, results):
        """Plot break-even point."""
        break_even = results['break_even_years']
        if break_even is not None and 0 < break_even < results['years'][-1]:
            break_even_cost = np.interp(
                break_even, results['years'], results['ice_costs']
            )
            ax.plot(break_even, break_even_cost, 'g*', markersize=20,
                    label=f'Break-even ({break_even:.2f} yrs)', zorder=5)

    def _setup_graph_labels_formatting(self, ax):
        """Postavi labele i formatiranje grafikona."""
        ax.set_title(f"Cost comparison: {self.bev_name} vs. {self.ice_name}",
                     fontsize=14, fontweight='bold', color=self.colors['text_primary'], pad=15)
        ax.set_xlabel("years", fontsize=11, color=self.colors['text_primary'], fontweight='bold')
        ax.set_ylabel("Ukupni trošak (€)", fontsize=11, color=self.colors['text_primary'], fontweight='bold')
        ax.tick_params(axis='x', colors=self.colors['text_secondary'], labelsize=10)
        ax.tick_params(axis='y', colors=self.colors['text_secondary'], labelsize=10)

        formatter = mticker.FuncFormatter(lambda x, p: self._format_currency(x))
        ax.yaxis.set_major_formatter(formatter)

    def _setup_graph_grid_legend(self, ax):
        """Postavi grid i legendu."""
        ax.grid(True, which='both', linestyle='--', linewidth=0.5,
               color=self.colors['text_secondary'], alpha=0.2)
        legend = ax.legend(loc='upper left', fontsize=10, framealpha=1.0,
                          facecolor=self.colors['input_bg'],
                          edgecolor=self.colors['text_secondary'])
        for text in legend.get_texts():
            text.set_color(self.colors['text_primary'])

    def _draw_graph(self, results):
        """Nacrtaj grafikon."""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        self._setup_graph_background(ax)
        self._plot_cost_lines(ax, results)
        self._plot_breakeven_point(ax, results)
        self._setup_graph_labels_formatting(ax)
        self._setup_graph_grid_legend(ax)
        
        self.fig.tight_layout()
        self.canvas.draw()

    def _clear_graph(self, message="Calculate to show results"):
        """Clear the graph and show a message."""
        self.fig.clear()
        self.fig.patch.set_facecolor(self.colors['chart_bg'])
        ax = self.fig.add_subplot(111)
        self._setup_graph_background(ax)
        ax.text(0.5, 0.5, message, horizontalalignment='center',
                verticalalignment='center', fontsize=12, color=self.colors['text_secondary'],
                transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_title("")
        self.canvas.draw()

    def _perform_calculation(self):
        """Perform calculation and update display."""
        try:
            avg_elec_price, warning_text = self._calculate_avg_electricity_price()
            self.warning_label.setText(warning_text)

            if avg_elec_price is None:
                self.breakeven_label.setText("Error: Check charging settings.")
                self._clear_graph("Error in charging settings")
                return

            self.bev_name, self.ice_name = self._get_vehicle_names()
            numeric_params = self._extract_numeric_params(avg_elec_price)

            if numeric_params is None:
                self.breakeven_label.setText("Error: Check that all inputs are valid.")
                self._clear_graph("Invalid inputs")
                return

            self.results = calculate_costs(**numeric_params)

            # Update results
            if self.results["break_even_years"] is not None:
                if self.results["break_even_years"] == 0:
                    text = f"✅ {self.bev_name} is profitable from day one!"
                else:
                    text = f"Break-even: {self.results['break_even_years']:.2f} years"
                self.breakeven_label.setText(text)
                self.breakeven_label.setStyleSheet(f"color: {self.colors['success']}; font-weight: bold;")
            else:
                self.breakeven_label.setText(
                    f"❌ {self.bev_name} does not become economical within the period."
                )
                self.breakeven_label.setStyleSheet(f"color: {self.colors['error']}; font-weight: bold;")

            bev_cost_text = f"Annual cost {self.bev_name}: {self._format_currency(self.results['bev_annual_cost'])} €"
            ice_cost_text = f"Annual cost {self.ice_name}: {self._format_currency(self.results['ice_annual_cost'])} €"
            self.bev_annual_label.setText(bev_cost_text)
            self.ice_annual_label.setText(ice_cost_text)

            # Nacrtaj grafikon
            self._draw_graph(self.results)

        except Exception as e:
            self.breakeven_label.setText(f"Error: {str(e)}")
            self._clear_graph(f"Error:\n{str(e)}")

    def _load_profile(self):
        """Load profile from JSON file."""
        profile_name = self.profile_combo.currentText()
        if not profile_name or profile_name == "No saved profiles":
            return

        file_path = os.path.join(PROFILES_DIR, f"{profile_name}.json")
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Ažuriraj sve input polje
            for key, value in data.items():
                if key in self.inputs:
                    self.inputs[key].setText(str(value))
                elif key in self.charging_inputs:
                    self.charging_inputs[key].setText(str(value))

            # Perform calculation
            self._perform_calculation()
            QMessageBox.information(self, "Success", f"Profile '{profile_name}' loaded.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading profile: {e}")

    def _save_profile(self):
        """Save current inputs as a profile."""
        profile_name, ok = self._get_input_dialog(
            "Save profile", "Enter profile name:"
        )
        if not ok or not profile_name:
            return

        try:
            data_to_save = {}

            # Spremi sve vehicle i usage unose
            for name, _, _ in self.VEHICLE_ENTRIES:
                data_to_save[name] = self.inputs[name].text()
            for name, _, _ in self.USAGE_ENTRIES:
                data_to_save[name] = self.inputs[name].text()

            # Spremi charging unose
            for pct_name, price_name, _, _, _ in self.CHARGING_TYPES:
                data_to_save[pct_name] = self.charging_inputs[pct_name].text()
                data_to_save[price_name] = self.charging_inputs[price_name].text()

            file_path = os.path.join(PROFILES_DIR, f"{profile_name}.json")
            with open(file_path, 'w') as f:
                json.dump(data_to_save, f, indent=4)

            # Refresh profiles list
            profiles = self._get_profiles_list()
            self.profile_combo.clear()
            self.profile_combo.addItems(profiles or ["No saved profiles"])
            self.profile_combo.setCurrentText(profile_name)

            QMessageBox.information(self, "Success", f"Profile '{profile_name}' saved.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving profile: {e}")

    def _delete_profile(self):
        """Delete profile."""
        profile_name = self.profile_combo.currentText()
        if not profile_name or profile_name == "No saved profiles":
            QMessageBox.warning(self, "Warning", "No profile selected for deletion.")
            return

        reply = QMessageBox.question(
            self, "Delete confirmation",
            f"Are you sure you want to permanently delete profile '{profile_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        file_path = os.path.join(PROFILES_DIR, f"{profile_name}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                profiles = self._get_profiles_list()
                self.profile_combo.clear()
                self.profile_combo.addItems(profiles or ["No saved profiles"])
                QMessageBox.information(self, "Success", f"Profile '{profile_name}' deleted.")
            else:
                QMessageBox.critical(self, "Error", "Profile file not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error deleting profile: {e}")

    def _export_to_png(self):
        """Izvezi grafikon kao PNG datoteku."""
        if self.results is None:
            QMessageBox.warning(
                self, "Warning",
                "No data to export. Please calculate results first."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save chart as PNG",
            "",
            "PNG Files (*.png);;All Files (*.*)"
        )

        if not file_path:
            return

        try:
            # Kreiraj novu figuru za export sa bijelim pozadinom
            export_fig = Figure(figsize=(10, 6), dpi=300)
            export_ax = export_fig.add_subplot(111)
            export_ax.set_facecolor("white")

            # Nacrtaj grafikon
            self._plot_cost_lines(export_ax, self.results)
            self._plot_breakeven_point(export_ax, self.results)

            export_ax.set_title(
                f"Usporedba troškova: {self.bev_name} vs. {self.ice_name}",
                fontsize=14, fontweight='bold', color=LIGHT_COLORS['text_primary'], pad=15
            )
            export_ax.set_xlabel("godine", fontsize=11, color=LIGHT_COLORS['text_primary'])
            export_ax.set_ylabel("Ukupni trošak (€)", fontsize=11, color=LIGHT_COLORS['text_primary'])

            formatter = mticker.FuncFormatter(lambda x, p: self._format_currency(x))
            export_ax.yaxis.set_major_formatter(formatter)
            export_ax.grid(True, which='both', linestyle='--', linewidth=0.5,
                          color='gray', alpha=0.3)

            legend = export_ax.legend(loc='upper left', fontsize=10)
            for text in legend.get_texts():
                text.set_color(LIGHT_COLORS['text_primary'])

            export_fig.tight_layout()
            export_fig.savefig(file_path, dpi=300, bbox_inches='tight')

            QMessageBox.information(
                self, "Success",
                f"Chart exported successfully:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting: {e}")

    def _get_input_dialog(self, title, label):
        """Kreiraj input dialog."""
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, title, label)
        return text, ok


def main():
    """Glavna funkcija."""
    app = QApplication(sys.argv)
    calculator = BEVCalculatorPyQt5()
    calculator.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
