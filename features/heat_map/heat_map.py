import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib

matplotlib.use('Agg')

class HeatMapVisualization:
    def __init__(self, img_width=200, img_height=200):
        self.__w = img_width
        self.__h = img_height

        self.__global_heatmap = np.zeros((self.__h, self.__w), dtype=np.float32)

    def visualize_heatmap(self, bboxes: list[list]):
        for bbox in bboxes:
            self.__global_heatmap[bbox[1]:bbox[3], bbox[0]:bbox[2]] += 1

        self.__global_heatmap = np.clip(self.__global_heatmap, 0, 255)

        fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
        im = ax.imshow(self.__global_heatmap, cmap='viridis')
        plt.colorbar(im, ax=ax)

        fig.tight_layout(pad=0.2)

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)

        return buf


if __name__ == '__main__':
    array = [[0, 0, 100, 100], [1, 3, 4, 5]]
    defect_visualization = HeatMapVisualization()
    img = defect_visualization.visualize_heatmap(array)

    buf = io.BytesIO(img)
    img_pil = Image.open(buf).convert("RGB")
    img_pil.show()
    plt.show()
