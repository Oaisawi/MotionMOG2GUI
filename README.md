# Real-Time Motion Tracker GUI with MOG2 and Audio Playback

This is a Python desktop application that allows users to upload video files and perform real-time motion detection using OpenCV’s MOG2 (Mixture of Gaussians v2) background subtraction algorithm. The interface provides options to view either bounding boxes or the motion mask, control audio playback using VLC, and adjust detection sensitivity and playback speed.

## Features

- Upload and play video files (supported formats: .mp4, .avi, .mov, .mkv)
- Real-time motion detection using OpenCV’s MOG2 background subtraction
- Display motion as either bounding boxes or raw binary mask
- Integrated VLC-based audio playback
- Adjustable motion detection sensitivity (threshold)
- Adjustable minimum contour area for motion visualization
- Playback speed control (from 0.25x to 2.0x)
- Volume control
- Seamless video looping
- Pause and resume functionality
- Modern dark-themed graphical interface

## Requirements

- Python 3.7 or higher
- opencv-python
- pillow
- python-vlc

Install dependencies:

```bash
pip install opencv-python pillow python-vlc
```

1- Run the script:

```bash

python motion_tracker_gui.py
```
2- Click Open Video to load a file.

3- Adjust the mask threshold and minimum area for better motion tracking.

4- Toggle between bounding box view and raw motion mask.

5- Control audio volume and playback speed using the sliders.

6- Use Pause to toggle between paused and playing states.

## What is MOG2 ?
MOG2 (Mixture of Gaussians version 2) is a background subtraction algorithm provided by OpenCV. It models each pixel with a mixture of Gaussians and adapts to changes in illumination and background movement. It is ideal for real-time video surveillance and motion tracking.
