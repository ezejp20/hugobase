#!/bin/bash

source_dir="${1:-./img}"
target_dir="${2:-../static/img/}"

# Create thumbnails in target dir
sh ./create_thumbnails.sh "$source_dir" "$target_dir"

# Create watermarked images in target dir
sh ./add_watermarks.sh "$source_dir" "$target_dir"
