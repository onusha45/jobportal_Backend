def euclidean_distance(point1: list, point2: list):
    print(point1, point2)
    if None in point1 or None in point2:
        raise ValueError("Both points must have valid coordinates (latitude and longitude)")

    if len(point1) != len(point2) or len(point1) != 2:
        raise ValueError("Points must be [longitude, latitude]")

    # point1 = [longitude1, latitude1], point2 = [longitude2, latitude2]
    lon1, lat1 = point1
    lon2, lat2 = point2

    # Approximate conversion factors (no math library)
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km at equator, decreasing towards poles
    # For Nepal (roughly 26°-28°N), we can use an average scaling factor for longitude
    LATITUDE_TO_KM = 111.0  # Constant: km per degree of latitude
    LONGITUDE_SCALE = 0.85  # Rough approximation for longitude at ~27°N (cos(27°) ≈ 0.891, adjusted)

    # Convert differences to kilometers
    delta_lat_km = (lat2 - lat1) * LATITUDE_TO_KM
    delta_lon_km = (lon2 - lon1) * LATITUDE_TO_KM * LONGITUDE_SCALE

    # Euclidean distance in kilometers: sqrt((Δlat_km)² + (Δlon_km)²)
    squared_diff_sum = (delta_lat_km * delta_lat_km) + (delta_lon_km * delta_lon_km)
    
    # Manual square root approximation (Newton's method, simple iteration)
    distance = squared_diff_sum
    for _ in range(5):  # 5 iterations for decent precision
        if distance <= 0:
            distance = 0
            break
        distance = (distance + squared_diff_sum / distance) / 2

    return distance