#!/bin/bash

# Function to display the help message
show_help() {
    echo "Usage: $0 <mp4_file1> [<mp4_file2> ...]"
    echo ""
    echo "Stream provided MP4 files to virtual video devices created with v4l2loopback."
    echo ""
    echo "Options:"
    echo "  -h, --help      Display this help message and exit."
}

# Check for help flag
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    show_help
    exit 0
fi

if [ "$#" -lt 1 ]; then
    echo "Please provide at least one MP4 video."
    show_help
    exit 1
fi

NUM_DEVICES="$#"

# Function to list all video devices
list_devices() {
    ls /dev/ | grep video | sort
}

# Get the list of devices before loading v4l2loopback
DEVICES_BEFORE=$(list_devices)

# Function to clean up on exit
cleanup() {
    pkill -f ffmpeg
    sudo modprobe -r v4l2loopback
    exit
}

# Trap the SIGINT signal (Ctrl+C) to run the cleanup function
trap cleanup SIGINT SIGTERM

# Load the v4l2loopback module to create the dummy devices for all videos at once
sudo modprobe v4l2loopback devices="$NUM_DEVICES" exclusive_caps=1

# Get the list of devices after loading v4l2loopback
DEVICES_AFTER=$(list_devices)

# Determine the newly created devices
NEW_DEVICES=$(comm -13 <(echo "$DEVICES_BEFORE") <(echo "$DEVICES_AFTER"))

# Convert positional parameters into an array of MP4 files
mp4_files=("$@")

# Stream the provided MP4 files to the new devices
i=0
for device in $NEW_DEVICES; do
    ffmpeg -re -stream_loop -1 -i "${mp4_files[$i]}" -f v4l2 "/dev/$device" &
    let "i++"
    if [ "$i" -ge "$NUM_DEVICES" ]; then
        break
    fi
done

# Wait for user input to stop streaming and cleanup
wait
