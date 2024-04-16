import tkinter
from pathlib import Path
from tkinter import filedialog


def select_path(conf):
    if conf.use_gui:
        root = tkinter.Tk()
        root.withdraw()
        conf.data_path = filedialog.askopenfilenames()
    else:
        source_path = Path(conf.data_path)
        source_path = sorted(source_path.glob("*"))
        pred_path = []
        for net in source_path:
            net_list = sorted(net.glob("*.mhd"))
            pred_path.append(net_list[conf.data_index - 1])
        gt_path = Path(conf.gt_path)
        gt_path = sorted(gt_path.glob("*.mhd"))

        file_num = len(pred_path)
        conf.gt_path = [gt_path[conf.data_index - 1] for i in range(file_num)]
        conf.data_path = pred_path
        print(conf.data_path)
