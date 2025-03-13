#!/bin/bash
layout=$(swaymsg -t get_inputs | grep -m1 'xkb_active_layout_name' | awk -F '"' '{print $4}')

if [[ $layout == *"English"* ]]; then
    echo "🇺🇸 EN"
elif [[ $layout == *"Ukrainian"* ]]; then
    echo "🇺🇦 UA"
else
    echo $layout
fi
