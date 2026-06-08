import cv2

from lane_detector import detect_lane
from vehicle_detector import detect_vehicles
from collision_logic import (
    check_vehicle_in_lane,
    collision_warning
)

# Load input video
cap = cv2.VideoCapture("edit.mp4")

while True:

    # Read one frame at a time
    ret, frame = cap.read()

    if not ret:
        break

    # Keep frame size consistent throughout the pipeline
    frame = cv2.resize(frame, (1280, 720))

    # Detect lane boundaries and lane region
    left_lane, right_lane, lane_polygon = detect_lane(frame)

    # Detect vehicles using YOLO
    vehicles = detect_vehicles(frame)

    # Process every detected vehicle
    for vehicle in vehicles:

        x1, y1, x2, y2 = vehicle

        # Center point of the bounding box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        # Check whether the vehicle is inside the current lane
        target_vehicle = check_vehicle_in_lane(
            vehicle,
            lane_polygon
        )

        if target_vehicle:

            # Trigger warning for close vehicles in the ego lane
            if collision_warning(vehicle):

                cv2.putText(
                    frame,
                    "FORWARD COLLISION WARNING",
                    (300, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    3
                )

            # Red box = vehicle inside current lane
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 0, 255),
                3
            )

        else:

            # Green box = vehicle outside current lane
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

        # Draw center point used for lane membership testing
        cv2.circle(
            frame,
            (cx, cy),
            5,
            (255, 0, 0),
            -1
        )

    # Display final FCW output
    cv2.imshow("FCW", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
