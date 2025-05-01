from ultralytics import YOLO
import cv2
import numpy as np
import sys
import os

import util
from sort.sort import *
from util import get_car, read_license_plate, write_csv


results = {}

mot_tracker = Sort()

# Get input and output paths from command-line arguments
input_video_path = sys.argv[1]
output_video_path = sys.argv[2]

# load models
coco_model = YOLO('yolov8n.pt')

# Get the absolute path to the model file
model_path = os.path.join(os.path.dirname(__file__), 'license_plate_detector.pt')
license_plate_detector = YOLO(model_path)

# load video
cap = cv2.VideoCapture(input_video_path)

# get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# initialize video writer
out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

# Vehicle classes in COCO dataset
vehicle_classes = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

# Colors for different vehicle types (B, G, R)
colors = {
    "Car": (0, 255, 0),        # Green
    "Motorcycle": (0, 165, 255),   # Orange
    "Bus": (255, 0, 0),        # Blue
    "Truck": (0, 0, 255)       # Red
}

# Initialize counters
vehicle_counts = {2: 0, 3: 0, 5: 0, 7: 0}  # Vehicle types: 2, 3, 5, 7
total_vehicles = 0

# Dictionary to store previous positions of tracked vehicles
previous_positions = {}

# read frames
frame_nmr = -1
ret = True
while ret:
    frame_nmr += 1
    ret, frame = cap.read()
    if ret:
        results[frame_nmr] = {}
        # detect vehicles
        detections = coco_model(frame)[0]
        detections_ = []
        current_frame_type_counts = {vehicle_type: 0 for vehicle_type in vehicle_classes.values()}
        total_vehicles_in_frame = 0

        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            if int(class_id) in vehicle_classes:
                detections_.append([x1, y1, x2, y2, score])
                vehicle_type = vehicle_classes[int(class_id)]
                color = colors[vehicle_type]

                # Increment counts
                total_vehicles_in_frame += 1
                current_frame_type_counts[vehicle_type] += 1
                vehicle_counts[int(class_id)] += 1

                # Draw bounding box for vehicle
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

        # track vehicles
        track_ids = mot_tracker.update(np.asarray(detections_))

        # Process tracked vehicles
        for track in track_ids:
            x1, y1, x2, y2, track_id = track
            center_y = (y1 + y2) / 2  # Calculate the vertical center of the bounding box

            # Check if the vehicle is moving towards the camera
            if track_id in previous_positions:
                if center_y > previous_positions[track_id]:  # Moving downwards (towards the camera)
                    total_vehicles += 1

            # Update the previous position
            previous_positions[track_id] = center_y

        # detect license plates
        license_plates = license_plate_detector(frame)[0]
        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate

            # assign license plate to car
            xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

            if car_id != -1:
                # draw bounding box for license plate
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)

                # crop license plate
                license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]

                # process license plate
                license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

                # read license plate number
                license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)

                if license_plate_text is not None:
                    results[frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                                                  'license_plate': {'bbox': [x1, y1, x2, y2],
                                                                    'text': license_plate_text,
                                                                    'bbox_score': score,
                                                                    'text_score': license_plate_text_score}}
                    # put license plate text on frame
                    cv2.putText(frame, license_plate_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

        # Overlay total vehicle count
        cv2.putText(frame, f"Total Vehicles: {total_vehicles_in_frame}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Display vehicle type counts
        y_offset = 70
        for vehicle_type, count in current_frame_type_counts.items():
            if count > 0:
                color = colors[vehicle_type]
                cv2.putText(frame, f"{vehicle_type}s: {count}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                y_offset += 30

        # Show the frame in a window
        cv2.imshow("Vehicle Detection", frame)

        # write the frame to the output video
        out.write(frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# release video objects
cap.release()
out.release()
cv2.destroyAllWindows()

# Print the results
print(f"Total vehicles moving towards the camera: {total_vehicles}")
print("Vehicle counts by type:")
for vehicle_type, count in vehicle_counts.items():
    print(f"Type {vehicle_type}: {count}")

