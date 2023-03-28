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
        source_path = sorted(source_path.glob('*.mhd'))
        gt_path = Path(conf.gt_path)
        gt_path = sorted(gt_path.glob('*.mhd'))
        conf.data_path = source_path
        conf.gt_path = gt_path