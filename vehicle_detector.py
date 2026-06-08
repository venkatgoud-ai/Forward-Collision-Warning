from ultralytics import YOLO

# Load YOLOv8 model once during startup
model = YOLO('yolov8n.pt')


def detect_vehicles(frame):

    # Run object detection on the current frame
    results = model(frame, verbose=False)

    vehicles = []

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])

            # Keep only road vehicles
            # 2 = car, 3 = motorcycle, 5 = bus, 7 = truck
            if cls in [2, 3, 5, 7]:

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                vehicles.append(
                    (x1, y1, x2, y2)
                )

    return vehicles
