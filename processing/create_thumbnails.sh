#!/bin/bash

script_path=$(dirname "$0")
source_dir="${1:-$script_path}"
target_dir="${2:-$script_path}"

for i in "$source_dir"/*.jpg; do
    base=$(basename "$i")
    echo "$base"
    if ! [ "$base" = *"-thumb.jpg" ]; then
      convert -verbose "$i" -thumbnail 460 "$target_dir/${base%.jpg}-thumb.jpg"
    fi
done;
