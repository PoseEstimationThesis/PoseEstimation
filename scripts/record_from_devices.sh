#!/bin/bash

# Function to display the help message
show_help() {
    echo "Usage: $0 <duration_in_seconds>"
    echo "Record video from connected cameras for a specified duration."
    echo "Options:"
    echo "  -h, --help    Display this help message."
    exit 1
}

# Check if the script is run with arguments
if [ $# -eq 0 ]; then
    show_help
fi

# Check for the help flag
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
fi

# Get the duration from the command-line argument
duration=$1

# Get a list of connected camera devices
cameras=$(v4l2-ctl --list-devices | grep -o "/dev/video[0-9]*")

# Create a directory to store the recordings
mkdir -p videos_recordings

# Loop through each camera and start recording in the background
for camera in $cameras; do
    # Set the output file for each camera
    output_file="videos_recordings/$(basename $camera)_output.mp4"

    # Record video for the specified duration in the background
    ffmpeg -y -f v4l2 -input_format mjpeg -i $camera -t $duration $output_file & 2>/dev/null
done

# Wait for all background processes to finish
wait

echo "All recordings completed."
