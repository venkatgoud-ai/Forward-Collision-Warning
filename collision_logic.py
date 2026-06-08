import cv2


# Check whether a detected vehicle lies inside the lane region
def check_vehicle_in_lane(vehicle, lane_polygon):

    if lane_polygon is None:
        return False

    x1, y1, x2, y2 = vehicle

    # Center point of the vehicle bounding box
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2

    # Returns a positive value when the point is inside the polygon
    inside = cv2.pointPolygonTest(
        lane_polygon,
        (cx, cy),
        False
    )

    return inside >= 0


# Estimate proximity using the height of the bounding box
def estimate_distance(vehicle):

    x1, y1, x2, y2 = vehicle

    box_height = y2 - y1

    return box_height


# Generate a collision warning when the vehicle appears close
def collision_warning(vehicle):

    distance = estimate_distance(vehicle)

    return distance > 90
