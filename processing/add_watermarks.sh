#!/bin/bash

script_path=$(dirname "$0")
source_dir="${1:-$script_path}"
target_dir="${2:-$script_path}"

for i in "$source_dir"/*.jpg; do
  # watermark using images
  # convert wmark_image.png -fill grey50 -colorize 40  miff:- |\
  # composite -dissolve 30 -gravity south - $i "watermark/$i.jpg"
  # watermark using text
  convert -size 320x240 xc:none -fill '#80808080' \
  -gravity NorthWest -draw "text 15,15 'Copyright'" \
  miff:- |\
  composite -verbose -tile - "$i" "$target_dir/$(basename "$i")"
done;

