#!/bin/bash

if [ ! -f DepotDownloader ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        curl -L -o DepotDownloader.zip "https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_3.3.0/DepotDownloader-macos-arm64.zip"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget https://github.com/SteamRE/DepotDownloader/releases/download/DepotDownloader_3.3.0/DepotDownloader-linux-x64.zip -O DepotDownloader.zip
    else
        echo "Unsupported OS: $OSTYPE"
        exit 1
    fi
    unzip -o DepotDownloader.zip DepotDownloader && rm DepotDownloader.zip
fi

if [ ! -f Decompiler ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        curl -L -o Decompiler.zip "https://github.com/ValveResourceFormat/ValveResourceFormat/releases/download/12.0/cli-macos-arm64.zip"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget https://github.com/ValveResourceFormat/ValveResourceFormat/releases/download/12.0/cli-linux-x64.zip -O Decompiler.zip
    else
        echo "Unsupported OS: $OSTYPE"
        exit 1
    fi
    unzip -o Decompiler.zip && rm Decompiler.zip
fi

# Remove com.apple.quarantine xattr if present
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Removing com.apple.quarantine xattr from files"
    find . -type f | while read -r file; do
        if xattr -p com.apple.quarantine "$file" &>/dev/null; then
            echo "Removing quarantine attribute from: $file"
            xattr -d com.apple.quarantine "$file"
        fi
    done
fi

# Download Deadlock Game files
./DepotDownloader -app 1422450 -username "$STEAM_USERNAME" -password "$STEAM_PASSWORD" -all-platforms -all-languages -validate -remember-password || exit 1

mkdir -p depots/game
rsync -av depots/*/*/game/* depots/game/
find depots/ -type d -empty -delete

# Extract Map-VPKs
citadel_folder="depots/game/citadel"

./Source2Viewer-CLI -i "$citadel_folder"/pak01_dir.vpk -d --threads 8 -o "$citadel_folder" -f scripts
./Source2Viewer-CLI -i "$citadel_folder"/pak01_dir.vpk -d --threads 8 -o "$citadel_folder" -f resource
./Source2Viewer-CLI -i "$citadel_folder"/pak01_dir.vpk -d --threads 8 -o "$citadel_folder" -f panorama
./Source2Viewer-CLI -i "$citadel_folder"/pak01_dir.vpk -d --threads 8 -o "$citadel_folder" -f sounds

# Extract chunked VPK files
#maps_folder="depots/game/citadel/maps"
#for chunked_vpk_file in $(find depots/game/ -type f -name "*_dir.vpk"); do
#    parent_dir=$(dirname "$chunked_vpk_file")
#
#    echo "Extracting $(basename chunked_vpk_file)"
#    # TODO: Decompile only required files
#    ./Source2Viewer-CLI -i "$chunked_vpk_file" -d --threads 8 -o "$parent_dir" -f scripts -f resource -f panorama
#
#    echo "Removing chunk files"
#    rm "$parent_dir/$(basename "$chunked_vpk_file" | cut -c1-5)"*
#done
#
#for vpk_file in $(find "$maps_folder" -type f -name "*.vpk"); do
#    echo "Extracting $(basename vpk_file)"
#    # TODO: Decompile only required files
#    ./Source2Viewer-CLI -i "$vpk_file" -d --threads 8 -o "$citadel_folder"
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
#    ./Source2Viewer-CLI -i "$vpk_file" -d --threads 8 -o "$parent_dir"
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
cp vdata/* res/

# Extract localization files
mkdir -p localization
cp -r "$citadel_folder"/resource/localization/citadel_gc/* localization/
cp -r "$citadel_folder"/resource/localization/citadel_heroes/* localization/
cp -r "$citadel_folder"/resource/localization/citadel_mods/* localization/
cp -r "$citadel_folder"/resource/localization/citadel_main/* localization/
cp -r "$citadel_folder"/resource/localization/citadel_attributes/* localization/

# Extract icon files
mkdir -p svgs
find depots/game/ -type f -name '*.svg' -print0 | xargs -0 -n 1 cp -t svgs/
find depots/game/ -type f -name 'keystat_*.png' -print0 | xargs -0 -n 1 cp -t svgs/
find svgs -type f -name "*_png.*" -exec bash -c 'mv "$1" "${1/_png./.}"' _ {} \;

# Add SVGs with currentColor fill
for f in svgs/*.svg;
do
    if [[ "$f" == *"_unfilled.svg" ]]; then
        continue
    fi
    sed 's/fill="[^"]*"/fill="currentColor"/g' "$f" > "${f%.svg}_unfilled.svg";
done

# Extract css files
cp "$citadel_folder"/panorama/styles/ability_icons.css res/
cp "$citadel_folder"/panorama/styles/ability_properties.css res/
cp "$citadel_folder"/panorama/styles/tooltips/citadel_mod_tooltip_shared.css res/
cp "$citadel_folder"/panorama/styles/citadel_base_styles.css res/
cp "$citadel_folder"/panorama/styles/objectives_map.css res/
cp "$citadel_folder"/panorama/styles/citadel_shared_colors.css res/

# Extract sound files
mkdir -p sounds
cp -r "$citadel_folder"/sounds/* sounds/

# Extract image files
mkdir -p images
mkdir -p images/hud
mkdir -p images/hud/core
cp -r "$citadel_folder"/panorama/images/heroes images/
cp -r "$citadel_folder"/panorama/images/hud/*.png images/hud/
cp -r "$citadel_folder"/panorama/images/hud/*/*.png images/hud/core/
cp "$citadel_folder"/panorama/images/hud/hero_portraits/* images/heroes/
cp "$citadel_folder"/panorama/images/*.* images/
cp -r "$citadel_folder"/panorama/images/hud/hero_portraits images/hud/
cp -r "$citadel_folder"/panorama/images/items/ images/
cp -r "$citadel_folder"/panorama/images/ images/shop/

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

# Rename Images, replace "_psd." and "_png." with "."
find images -type f -name "*_psd.*" -exec bash -c 'mv "$1" "${1/_psd./.}"' _ {} \;
find images -type f -name "*_png.*" -exec bash -c 'mv "$1" "${1/_png./.}"' _ {} \;

# Optimize images
optipng -o2 images/**/*.png

# Extract video files
mkdir -p videos
cp -r "$citadel_folder"/panorama/videos/hero_abilities videos/
find videos -type f -name "*.webm" -print0 | \
    xargs -P 4 -0 -I {} sh -c '
        video_file="{}"
        video_mp4_file=$(echo "$video_file" | sed "s/.webm/_h264.mp4/")
        echo "Converting $video_file to $video_mp4_file"
        ffmpeg -i "$video_file" -c:v libx264 -crf 23 -y "$video_mp4_file"
    '
