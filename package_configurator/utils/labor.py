def calc_labor_hours(quantity: int, units_per_hour: int, setup_minutes: int):
    return quantity / units_per_hour + (setup_minutes / 60)
