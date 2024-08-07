#!/bin/bash
KLIPPER_PATH="${HOME}/klipper"
SYSTEMDDIR="/etc/systemd/system"

# Find SRCDIR from the pathname of this script
SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/ && pwd )"

SRC_FILE="${SRC_DIR}/bed_fans.py"
DST_FILE="${KLIPPER_PATH}/klippy/extras/bed_fans.py"

toggle_extension()
{
    if [[ -e $DST_FILE || -L $DST_FILE ]]; then
        echo "Removing extension from Klipper..."
        rm -f "${DST_FILE}"
    else
        echo "Linking extension to Klipper..."
        ln -sf "${SRC_FILE}" "${DST_FILE}"
    fi
}

restart_klipper()
{
    echo "Restarting Klipper..."
    sudo systemctl restart klipper
}

# Force script to exit if an error occurs
set -e

# Parse command line arguments
while getopts "k:" arg; do
    case $arg in
        k) KLIPPER_PATH=$OPTARG;;
    esac
done

# Run steps
toggle_extension
restart_klipper
