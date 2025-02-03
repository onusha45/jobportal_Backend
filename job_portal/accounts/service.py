def euclidean_distance(point1: list, point2: list):
    print(point1, point2)
    if None in point1 or None in point2:
        raise ValueError("Both points must have valid coordinates (latitude and longitude)")

    if len(point1) != len(point2):
        raise ValueError("Points must have the same number of dimensions")
    squared_diff_sum = sum((x - y) ** 2 for x, y in zip(point1, point2))
    distance = squared_diff_sum ** 0.5

    return distance
