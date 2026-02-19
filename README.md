# BEV Calculator - PyQt5 Version

## 📋 Description

Application for analyzing the profitability of BEV (Battery Electric Vehicle) vehicles compared to ICE (Internal Combustion Engine) vehicles, written in the **PyQt5** framework.

## ✨ Characteristics

### 🎨 Modern UI
- ✅ Professional design with CSS styling
- ✅ Responsive layout with scroll areas
- ✅ Intuitive division into input and output panels
- ✅ Dynamically colored messages (warnings, errors, success)

### 🧮 Calculation Options
- ✅ Flexible input for all vehicle parameters
- ✅ Support for different types of charging (home, public AC/DC)
- ✅ Automatic calculation of the break-even point
- ✅ Comparison of annual costs

### 📊 Graphic Displays
- ✅ Interactive chart with Matplotlib
- ✅ Customized colors for BEV and ICE lines
- ✅ Marking the break-even point
- ✅ NavigationToolbar for zoom, pan, save

### 💾 Managing Profiles
- ✅ Save the current parameters as a profile
- ✅ Load previously saved profiles
- ✅ Delete unnecessary profiles
- ✅ JSON storage for simplicity

### 📤 Export
- ✅ Export the chart as a PNG file
- ✅ High resolution (300 DPI)
- ✅ Professional design for exported files

## 🚀 Launching

### Prerequisites

```bash
# Python 3.7+
pip install PyQt5 PyQt5-sip matplotlib numpy
```

### Installation

```bash
# Navigate to the directory
cd "BEVCalc"

# Start the application
python main_pyqt5.py
```

## 📘 Usage

### 1. Data entry

**The left side of the application contains:**

#### Load profile
- Select a previously saved profile from the list
- Click "Load profile"

#### Vehicle information
- **Name of BEV vehicle** - eg "Tesla Model 3"
- **Name of ICE vehicle** - eg "VW Golf 8"
- **BEV price (€)** - purchase price of a BEV vehicle
- **ICE price (€)** - purchase price of ICE vehicles
- **Incentives (€)** - government subsidies
- **Maintenance BEV (€/year)** - annual maintenance costs
- **ICE maintenance (€/year)** - annual maintenance costs

#### Use and consumption
- **Annual mileage (km)** - average km per year
- **BEV consumption (kWh/100km)** - energy consumption
- **ICE consumption (l/100km)** - fuel consumption
- **Fuel price (€/l)** - current price of a liter of fuel

#### BEV charging settings
- **Home** - Share (%) and Price (€/kWh)
- **Public AC** - Share (%) and Price (€/kWh)
- **Public DC** - Share (%) and Price (€/kWh)

#### Actions
- **Calculate** - Start calculation with current parameters
- **Save profile** - Save all entries as a profile
- **Delete Profile** - Delete the selected profile

### 2. Display Results

**The right side of the application shows:**

#### Results
- **Break-even point** - Number of years until investment return
- **Annual cost of BEV** - Sum of energy + maintenance
- **Annual cost of ICE** - Sum of fuel + maintenance

#### Chart
- **Blue lines** - Costs of BEV vehicles
- **Orange lines** - Costs of ICE vehicles
- **Green Star** - Breakeven point (if any)
- **Grid and legends** - For easier reading of data

#### Export
- **Export as PNG** - Save chart in high resolution

## 💡 Examples of Use

### Example 1: Tesla Model 3 vs VW Golf 8

**Input:**
```
Tesla Model 3:
- Price: €40,000
- Maintenance: €150/year
- Consumption: 18 kWh/100km

VW Golf 8:
- Price: €25,000
- Maintenance: €400/year
- Consumption: 7 l/100km

Other:
- Annual mileage: 15,000 km
- Fuel price: €1.50/l
- Incentives: €9,000
- Average electricity price: €0.20/kWh
```

**Result:**
```
Breakeven point: 8.45 years
Annual cost Tesla: €2,950
Annual cost Golf: €3,440
```

### Example 2: Creating Your Own Profile

1. Enter all desired parameters
2. Click "Calculate" to display the results
3. Click "Save profile" and enter a name (e.g. "My Profile")
4. The profile is now available in the quick load list

