import cv2
import os
import time

# RTSP stream URL
rtsp_url = "rtsp://192.168.42.1/live"

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp|flags;low_delay|vf;setpts=0|fflags;nobuffer|framedrop|hwaccel;cuda|sync;ext|c:v;h264_nvenc|analyzeduration;0"

#|hwaccel;cuda|probesize;32|sync;ext|analyzeduration;0"

#|hwaccel;cuda;hwaccel_output_format;cuda|c:v;h264_nvenc"

# Create a VideoCapture object
cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG, (cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY, cv2.CAP_PROP_N_THREADS, 1))

# Check if the connection was successful
if not cap.isOpened():
    print("Error: Cannot connect to the RTSP stream.")
    exit()

width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(f"Cap is {width} x {height}")

hw_accel = cap.get(cv2.CAP_PROP_HW_ACCELERATION)
print(f"{hw_accel=}")

# cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
# print(f"{hw_accel=}")

# Read and display the video stream
while True:
    ret, frame = cap.read()
    
    if not ret:
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG, (cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY))
        continue
    
    # Display the frame
    # cv2.imshow('RTSP Stream', frame)

    filename = f"{round(time.time() * 1000)}"
    cv2.imwrite(f"images/{filename}.jpg", frame)
    
    # Press 'q' to exit the video display window
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# Release the VideoCapture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
