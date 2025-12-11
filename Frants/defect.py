import numpy as np

class HeatMap():
    def __init__(self):
        self.array = np.zeros((200,200),dtype=np.int256)


if __name__=="__main__":
    hm = HeatMap()
    print(hm.array)