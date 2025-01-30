def euclidean_distance(point1, point2):
    """
    Calculate Euclidean distance between two points of any dimension
    
    Args:
        point1 (list): First point coordinates
        point2 (list): Second point coordinates
    
    Returns:
        float: Euclidean distance between the points
    
    Example:
        >>> euclidean_distance([1, 2], [4, 6])
        5.0
        >>> euclidean_distance([1, 2, 3], [4, 5, 6])
        5.196152422706632
    """
    if len(point1) != len(point2):
        raise ValueError("Points must have the same number of dimensions")
    
    squared_diff_sum = sum((x - y) ** 2 for x, y in zip(point1, point2))
    distance = squared_diff_sum ** 0.5
    
    return distance