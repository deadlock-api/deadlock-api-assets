#!/bin/bash

if [ ! -f DepotDownloader ]; then
    wget https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_2.7.3/DepotDownloader-linux-x64.zip -O DepotDownloader-linux-x64.zip
    unzip -o DepotDownloader-linux-x64.zip DepotDownloader && rm DepotDownloader-linux-x64.zip
fi

if [ ! -f Decompiler ]; then
    wget https://github.com/ValveResourceFormat/ValveResourceFormat/releases/download/10.2/Decompiler-linux-x64.zip -O Decompiler-linux-x64.zip
    unzip -o Decompiler-linux-x64.zip && rm Decompiler-linux-x64.zip
fi

# Download Deadlock Game files
./DepotDownloader -app 1422450 -username "$STEAM_USERNAME" -password "$STEAM_PASSWORD" || exit 1

mkdir -p depots/game
rsync -av depots/*/*/game/* depots/game/
find depots/ -type d -empty -delete

# Extract Map-VPKs
citadel_folder="depots/game/citadel"

./Decompiler -i "$citadel_folder"/pak01_dir.vpk -d --threads 8 -o "$citadel_folder" -f scripts
./Decompiler -i "$citadel_folder"/pak01_dir.vpk -d --threads 8 -o "$citadel_folder" -f resource
./Decompiler -i "$citadel_folder"/pak01_dir.vpk -d --threads 8 -o "$citadel_folder" -f panorama

# Extract chunked VPK files
#maps_folder="depots/game/citadel/maps"
#for chunked_vpk_file in $(find depots/game/ -type f -name "*_dir.vpk"); do
#    parent_dir=$(dirname "$chunked_vpk_file")
#
#    echo "Extracting $(basename chunked_vpk_file)"
#    # TODO: Decompile only required files
#    ./Decompiler -i "$chunked_vpk_file" -d --threads 8 -o "$parent_dir" -f scripts -f resource -f panorama
#
#    echo "Removing chunk files"
#    rm "$parent_dir/$(basename "$chunked_vpk_file" | cut -c1-5)"*
#done
#
#for vpk_file in $(find "$maps_folder" -type f -name "*.vpk"); do
#    echo "Extracting $(basename vpk_file)"
#    # TODO: Decompile only required files
#    ./Decompiler -i "$vpk_file" -d --threads 8 -o "$citadel_folder"
#
#    echo "Removing VPK file"
#    rm "$vpk_file"
#done
#
## Extract non-chunked VPK files
#for vpk_file in $(find depots/game/ -type f -name "*.vpk"); do
#    parent_dir=$(dirname "$vpk_file")
#
#    echo "Extracting $(basename vpk_file)"
#    # TODO: Decompile only required files
#    ./Decompiler -i "$vpk_file" -d --threads 8 -o "$parent_dir"
#
#    echo "Removing VPK file"
#    rm "$vpk_file"
#done

# Extract Steam Info
mkdir -p res
cp "$citadel_folder"/steam.inf res/

# Extract vData files
mkdir -p vdata
cp "$citadel_folder"/scripts/abilities.vdata vdata/
cp "$citadel_folder"/scripts/heroes.vdata vdata/
cp "$citadel_folder"/scripts/generic_data.vdata vdata/

# Extract localization files
mkdir -p localization
cp -r "$citadel_folder"/resource/localization/citadel_gc/* localization/
cp -r "$citadel_folder"/resource/localization/citadel_heroes/* localization/
cp -r "$citadel_folder"/resource/localization/citadel_main/* localization/

# Extract icon files
mkdir -p svgs
find depots/game/ -type f -name '*.svg' -print0 | xargs -0 -n 1 cp -t svgs/

# Extract video files
mkdir -p videos
cp -r "$citadel_folder"/panorama/videos/hero_abilities videos/
find videos -type f -name "*.webm" -print0 | \
    xargs -P 8 -0 -I {} sh -c '
        video_file="{}"
        video_mp4_file=$(echo "$video_file" | sed "s/.webm/_h264.mp4/")
        echo "Converting $video_file to $video_mp4_file"
        ffmpeg -i "$video_file" -c:v libx264 -crf 23 -y "$video_mp4_file"
    '

# Extract css files
cp "$citadel_folder"/panorama/styles/objectives_map.css res/
cp "$citadel_folder"/panorama/styles/citadel_shared_colors.css res/

# Extract image files
mkdir -p images
mkdir -p images/hud
cp -r "$citadel_folder"/panorama/images/heroes images/
cp -r "$citadel_folder"/panorama/images/hud/*.png images/hud/
cp "$citadel_folder"/panorama/images/hud/hero_portraits/* images/heroes/
cp "$citadel_folder"/panorama/images/*.* images/
cp -r "$citadel_folder"/panorama/images/hud/hero_portraits images/hud/

mkdir -p images/abilities
cp -r "$citadel_folder"/panorama/images/hud/abilities images/
cp -r "$citadel_folder"/panorama/images/upgrades images/

mkdir -p images/maps
cp -r "$citadel_folder"/panorama/images/minimap/base/* images/maps/

mkdir -p images/ranks
cp -r "$citadel_folder"/panorama/images/ranked/badges/* images/ranks/

# Generate webp images
for file in $(find images -type f -name "*.png"); do
    base_name=$(basename "$file")
    dir_name=$(dirname "$file")
    file_name="${base_name%.png}"
    new_file_name="${file_name}.webp"
    new_file_path="$dir_name/$new_file_name"
    convert -quality 50 -define webp:lossless=true "$file" "$new_file_path"
    echo "Converted to webp: $new_file_path"
done

# Optimize images
optipng -o2 images/**/*.png
