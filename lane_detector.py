import cv2
import numpy as np

# Store the most recent valid lane lines
last_left_lane = None
last_right_lane = None


# Average multiple lane segments into a single lane line
def average_lane(lines):

    if len(lines) == 0:
        return None

    slopes = []
    intercepts = []

    for x1, y1, x2, y2 in lines:

        # Ignore vertical lines
        if x2 - x1 == 0:
            continue

        slope = (y2 - y1) / (x2 - x1)

        # Filter out nearly horizontal lines
        if abs(slope) < 0.5:
            continue

        # Filter out unrealistic lane candidates
        if abs(slope) > 2:
            continue

        intercept = y1 - slope * x1

        slopes.append(slope)
        intercepts.append(intercept)

    if len(slopes) == 0:
        return None

    avg_slope = np.mean(slopes)
    avg_intercept = np.mean(intercepts)

    return avg_slope, avg_intercept


# Convert slope-intercept form into drawable image coordinates
def make_line(frame, lane):

    if lane is None:
        return None

    slope, intercept = lane

    y1 = frame.shape[0]
    y2 = 500

    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)

    return (x1, y1, x2, y2)


def detect_lane(frame):

    global last_left_lane
    global last_right_lane

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Reduce noise before edge detection
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Extract strong edges from the road
    edges = cv2.Canny(blur, 50, 150)

    height, width = edges.shape

    # Create a region of interest covering the road ahead
    mask = np.zeros_like(edges)

    polygon = np.array([[
        (250, height),
        (500, 500),
        (780, 500),
        (1050, height)
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)

    # Keep only edges inside the road region
    masked_edges = cv2.bitwise_and(edges, mask)

    # Detect line segments using Hough Transform
    lines = cv2.HoughLinesP(
        masked_edges,
        rho=1,
        theta=np.pi / 180,
        threshold=50,
        minLineLength=50,
        maxLineGap=50
    )

    line_image = frame.copy()

    left_lines = []
    right_lines = []

    if lines is not None:

        for line in lines:

            x1, y1, x2, y2 = line[0]

            if x2 - x1 == 0:
                continue

            slope = (y2 - y1) / (x2 - x1)

            if abs(slope) < 0.5:
                continue

            if abs(slope) > 2:
                continue

            # Separate left and right lane candidates
            if slope < 0:
                left_lines.append((x1, y1, x2, y2))
            else:
                right_lines.append((x1, y1, x2, y2))

    # Generate a single lane line for each side
    left_avg = average_lane(left_lines)
    right_avg = average_lane(right_lines)

    left_lane = make_line(frame, left_avg)
    right_lane = make_line(frame, right_avg)

    # Reuse previous lane if detection is temporarily lost
    if left_lane is not None:
        last_left_lane = left_lane
    else:
        left_lane = last_left_lane

    if right_lane is not None:
        last_right_lane = right_lane
    else:
        right_lane = last_right_lane

    # Create a polygon between both lane boundaries
    if left_lane is not None and right_lane is not None:

        lane_polygon = np.array([[
            (left_lane[0], left_lane[1]),
            (left_lane[2], left_lane[3]),
            (right_lane[2], right_lane[3]),
            (right_lane[0], right_lane[1])
        ]], np.int32)

        overlay = line_image.copy()

        # Highlight the drivable lane region
        cv2.fillPoly(
            overlay,
            lane_polygon,
            (0, 255, 0)
        )

        cv2.addWeighted(
            overlay,
            0.3,
            line_image,
            0.7,
            0,
            line_image
        )

    # Draw left lane boundary
    if left_lane is not None:

        cv2.line(
            line_image,
            (left_lane[0], left_lane[1]),
            (left_lane[2], left_lane[3]),
            (0, 255, 0),
            5
        )

    # Draw right lane boundary
    if right_lane is not None:

        cv2.line(
            line_image,
            (right_lane[0], right_lane[1]),
            (right_lane[2], right_lane[3]),
            (0, 255, 0),
            5
        )

    cv2.imshow("Detected Lines", line_image)

    if left_lane is not None and right_lane is not None:
        return left_lane, right_lane, lane_polygon

    return left_lane, right_lane, None
