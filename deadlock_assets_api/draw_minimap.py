import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import rcParams
from matplotlib.axes import Axes
from shapely.geometry.linestring import LineString

from deadlock_assets_api.models.map_data import (
    LANE_COLORS,
    LANE_ORIGINS,
    LANES,
    MAP_RADIUS,
)

rcParams.update({"figure.autolayout": True})

HEIGHT, WIDTH = 512, 512
DPI = 100


def draw_minimap(with_background: bool = True):
    img_path = "images/maps/minimap.png" if with_background else "images/maps/minimap_plain.png"

    lanes = get_smoothed_lanes()

    # plot on matplotlib as a line
    fig, ax = plt.subplots(figsize=(HEIGHT / DPI, WIDTH / DPI))
    fig.set_dpi(DPI)

    fig.subplots_adjust(top=1.0, bottom=0, right=1.0, left=0, hspace=0, wspace=0)
    if with_background:
        add_background(ax)

    for lane, color in zip(lanes, LANE_COLORS):
        ax.plot(*lane.xy, linewidth=4, color=color)

    ax.set_aspect("equal")
    plt.axis("off")
    plt.savefig(img_path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()

    postprocess_minimap_img(img_path)


def get_smoothed_lanes() -> list[LineString]:
    lanes = [[np.array(lane_points[:2]) for lane_points in lane] for lane in LANES]
    origins = [np.array(origin[:2]) for origin in LANE_ORIGINS]
    lanes = [
        [lane_points[:2] + origin for lane_points in lane] for lane, origin in zip(lanes, origins)
    ]
    return [LineString(lane_points) for lane_points in lanes]


def add_background(ax: Axes):
    background_img = plt.imread("images/maps/minimap_bg.png")
    ax.imshow(background_img, extent=(-MAP_RADIUS, MAP_RADIUS, -MAP_RADIUS, MAP_RADIUS))
    mid_img = plt.imread("images/maps/minimap_midtown_mid_2k.png")
    ax.imshow(mid_img, extent=(-MAP_RADIUS, MAP_RADIUS, -MAP_RADIUS, MAP_RADIUS))
    frame_img = plt.imread("images/maps/minimap_frame.png")
    ax.imshow(frame_img, extent=(-MAP_RADIUS, MAP_RADIUS, -MAP_RADIUS, MAP_RADIUS))


def postprocess_minimap_img(img_path: str):
    img = cv2.imread(img_path)
    img_h, img_w, _ = img.shape

    # cut off circular mask
    mask = np.zeros_like(img)
    cv2.circle(mask, (img_w // 2, img_h // 2), img_w // 2, (255, 255, 255), -1)
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2BGRA)
    masked_img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    masked_img[:, :, 3] = mask[:, :, 0]

    # cut off transparent edges
    first_non_transparent_row = np.argmax(masked_img[:, :, 3].sum(axis=1) > 0)
    last_non_transparent_row = img_h - np.argmax(masked_img[:, :, 3][::-1].sum(axis=1) > 0)
    first_non_transparent_col = np.argmax(masked_img[:, :, 3].sum(axis=0) > 0)
    last_non_transparent_col = img_w - np.argmax(masked_img[:, :, 3][:, ::-1].sum(axis=0) > 0)
    masked_img = masked_img[
        first_non_transparent_row:last_non_transparent_row,
        first_non_transparent_col:last_non_transparent_col,
    ]

    # resize to original size
    masked_img = cv2.resize(masked_img, (WIDTH, HEIGHT))

    cv2.imwrite(img_path, masked_img)


if __name__ == "__main__":
    draw_minimap()
    draw_minimap(with_background=False)
