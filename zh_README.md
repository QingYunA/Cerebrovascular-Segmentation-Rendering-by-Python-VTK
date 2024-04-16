# Cerebrovascular Segmentation Rendering by Python VTK

基于ITK与VTK的医学图像三维可视化

## 使用方法
在 `conf.yml` 中设置配置，然后运行
```python
python main.py
```
你会在终端中看到渲染进度条。
渲染完成后，结果会自动保存为 `.obj` 和 `.png` 格式。如果不想保存，请在 `conf.yml` 中更改 `save_png` 和 `save_obj` 。

## 未来计划

* [x] 多窗口可视化
* [x] FN，TN，FP，TP等指标单独着色渲染
* [x] 输出结果与GT做距离，采用color bar映射颜色
* [ ] 单行渲染会出现不对齐的情况，需要调整
* [ ] 目前没考虑渲染速度问题
* [ ] PyQT+VTK渲染，可以实现交互式渲染

## 如何修改config

在 `conf.yml` 可以配置大多数的设置，较为重要的设置如下

```yaml
#* BASE
render_mode: 可选single, multi, color。分别代表仅pred文件渲染，tp、tn不同颜色渲染，color bar渲染
data_path: 数据集路径
gt_path: gt文件路径
layout: 排布方式, 可选 "1*n"，"2*n" 分别代表单行与双行排布
#* COLOR
red_color: 控制血管主体颜色
confusion_color: [[fp],[fn],[tp],[tn]]，控制混淆矩阵渲染出的颜色
background: 控制背景颜色
color_bar_labels: 控制color bar标签数量
```

## Example

### 仅渲染pred文件

![](https://s2.loli.net/2024/04/16/Fsy6o4NagnOK1jS.webp)

### pred + gt

![](https://s2.loli.net/2024/04/16/sEhaJQiLIqMKdbW.webp)


### Color Bar
![](https://s2.loli.net/2024/04/16/Svpk6YAUVjxCQRI.webp)