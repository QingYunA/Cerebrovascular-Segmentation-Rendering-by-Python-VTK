# Cerebrovascular Segmentation Rendering by Python VTK
Chinese Readme in [zh_README](zh_README.md)

## Catalog

* [x] Segmentation and rendering of cerebral vessels
* [x] FN and FP identification in segmentation results
* [x] Display of the color bar for clarity
* [ ] Correction of occasional inaccuracies in segmentation
* [ ] Optimization of the segmentation algorithm for better performance
* [ ] Integration of PyQT and VTK for an interactive segmentation and rendering interface

## Usage
Set your configuration in `conf.yml` and then run
```python
python main.py
```
You will see a progress in the terminal indicates the rendering progress.
After rendering, the results will be automatically saved as `.obj` and `.png` format. If you don't want to save, change `save_png` and `save_obj` in `conf.yml`

## How to Change Config

The `conf.yml` file can be modified to adjust the parameters for segmentation. The base configuration should be updated carefully to ensure proper functioning of the segmentation and rendering process.

```yaml
# * BASE
render_mode: Choose between 'single', 'multi', or 'color' for the display mode
data_path: Path to the input data for segmentation
gt_path: Path to the ground truth data for comparison
layout: Choose the layout format as '1xn' or '2xn' for displaying the results
# * COLOR
red_color: Color for positive predictions (e.g., correct segmentation)
confusion_color: Define colors for false positives (fp), false negatives (fn), true positives (tp), and true negatives (tn)
background: Background color for the display
color_bar_labels: Define labels for the color bar display
```

## Example

### Only rendering prediction file.

![](https://s2.loli.net/2024/04/16/Fsy6o4NagnOK1jS.webp)

### Prediction vessel + gt (calcatulate confusion matrix and render them by different colors)

![](https://s2.loli.net/2024/04/16/sEhaJQiLIqMKdbW.webp)


### Color Bar
![](https://s2.loli.net/2024/04/16/Svpk6YAUVjxCQRI.webp)