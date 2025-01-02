def calculate_price(distance_km, duration_hours, base_fare, rate_per_km, rate_per_hour):
    # Calculate the total fare based on distance, duration, and pricing parameters
    distance_cost = distance_km * rate_per_km
    duration_cost = duration_hours * rate_per_hour
    total_fare = base_fare + distance_cost + duration_cost
    return total_fare