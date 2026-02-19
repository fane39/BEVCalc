"""Calculate total cost of ownership for BEV vs ICE vehicles."""
import numpy as np


def calculate_costs(
    # --- Vehicle Prices ---
    bev_price: float,
    ice_price: float,
    subsidy: float,
    
    # --- Consumption & Energy Prices ---
    bev_consumption: float,  # kWh/100km
    ice_consumption: float,  # L/100km
    electricity_price: float,  # EUR/kWh
    fuel_price: float,  # EUR/L
    
    # --- Usage & Maintenance ---
    annual_km: int,
    bev_maintenance: int,
    ice_maintenance: int,
    
    # --- Calculation Period ---
    years: int = 15
) -> dict:
    """
    Calculate the total cost of ownership for a BEV and an ICE vehicle.

    Compares cumulative costs over a specified period and calculates the
    break-even point where the BEV becomes more economical than the ICE vehicle.

    Args:
        bev_price: Initial purchase price of BEV in EUR
        ice_price: Initial purchase price of ICE vehicle in EUR
        subsidy: Government subsidy/incentive for BEV in EUR
        bev_consumption: Energy consumption in kWh/100km
        ice_consumption: Fuel consumption in L/100km
        electricity_price: Average electricity price in EUR/kWh
        fuel_price: Fuel price in EUR/L
        annual_km: Annual kilometers driven
        bev_maintenance: Annual maintenance cost for BEV in EUR
        ice_maintenance: Annual maintenance cost for ICE vehicle in EUR
        years: Analysis period in years (default 15)

    Returns:
        Dictionary containing:
        - years: Array of years from 0 to specified number
        - bev_costs: Cumulative costs for BEV at each year
        - ice_costs: Cumulative costs for ICE at each year
        - break_even_years: Years until BEV becomes cheaper (or None if not within period)
        - bev_annual_cost: Annual operating cost for BEV
        - ice_annual_cost: Annual operating cost for ICE
    """
    
    # 1. Initial Investment
    bev_initial_cost = bev_price - subsidy
    ice_initial_cost = ice_price

    # 2. Annual Running Costs
    # Energy cost per year (kWh/100km * 100km/year * EUR/kWh)
    bev_annual_energy_cost = (annual_km / 100) * bev_consumption * electricity_price
    ice_annual_fuel_cost = (annual_km / 100) * ice_consumption * fuel_price

    # Total Annual Running Cost (Energy + Maintenance)
    bev_total_annual_cost = bev_annual_energy_cost + bev_maintenance
    ice_total_annual_cost = ice_annual_fuel_cost + ice_maintenance

    # 3. Cumulative Costs Over Time
    # Create array of years from 0 to specified period
    years_axis = np.arange(0, years + 1)
    
    # Calculate cumulative cost for each year
    # Formula: Initial Cost + (years * annual_cost)
    bev_cumulative_cost = bev_initial_cost + (years_axis * bev_total_annual_cost)
    ice_cumulative_cost = ice_initial_cost + (years_axis * ice_total_annual_cost)

    # 4. Break-Even Point Calculation
    # The break-even point is where the total cost lines intersect.
    # Solving: BEV_Initial + x * BEV_Annual = ICE_Initial + x * ICE_Annual
    # Gives: x = (ICE_Initial - BEV_Initial) / (BEV_Annual - ICE_Annual)
    
    initial_cost_difference = bev_initial_cost - ice_initial_cost
    annual_cost_difference = ice_total_annual_cost - bev_total_annual_cost
    
    break_even_years = None
    # The break-even point is only meaningful if BEV has lower annual costs
    if annual_cost_difference > 0:
        # If BEV initial cost is already lower, break-even is immediate
        if initial_cost_difference <= 0:
            break_even_years = 0
        else:
            break_even_years = initial_cost_difference / annual_cost_difference

    return {
        "years": years_axis,
        "bev_costs": bev_cumulative_cost,
        "ice_costs": ice_cumulative_cost,
        "break_even_years": break_even_years,
        "bev_annual_cost": bev_total_annual_cost,
        "ice_annual_cost": ice_total_annual_cost
    }
