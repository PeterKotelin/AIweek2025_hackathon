import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import clipboard


class HeapMapVisualization:
    def __init__(self, img_width=200, img_height=200):
        self.__w = img_width
        self.__h = img_height

        self.__global_heatmap = np.zeros((self.__h, self.__w), dtype=np.float32)

    def visualize_heap_map(self, bboxes: list[list]):
        for bbox in bboxes:
            self.__global_heatmap[bbox[1]:bbox[3], bbox[0]:bbox[2]] += 1

        self.__global_heatmap = np.clip(self.__global_heatmap, 0, 255)

        fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
        im = ax.imshow(self.__global_heatmap, cmap='viridis')
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

        fig.tight_layout(pad=0.2)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)

        buf.seek(0)
        png_bytes = buf.getvalue()
        return png_bytes


if __name__ == '__main__':
    array = [[0, 0, 100, 100], [1, 3, 4, 5]]
    defect_visualization = HeapMapVisualization()
    img = defect_visualization.visualize_heap_map(array)

    buf = io.BytesIO(img)
    img_pil = Image.open(buf).convert("RGB")
    img_pil.show()
    plt.show()
