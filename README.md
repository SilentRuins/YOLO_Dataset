# 使用半自动标注技术将视频制作成可以直接供yolo训练的数据集
- **半自动标注的思想**：从大量未标注的数据中抽取少量数据进行手动标注，用这部分少量数据训练一个模型，使用这个模型对大量数据进行自动标注，最终完成数据标注。使用半自动标注可以为数据标注省下大量时间成本

- 该项目使用`make_dataset/`中的.py脚本配合yolo完成半自动标注数据集
## 技术栈：
`python-3.10`,`pytorch`,`yolo26`,`opencv`,`labelimg`
## 文件结构：
```
dataset&model/  
├── make_dataset/  
│   ├── img/  
│   ├── labels/  
│   ├── mydataset/  
│   ├── predata/  
│   ├── 数据集视频/  
│   ├── format.py  
│   ├── make_data.py  
│   └── pick.py  
├── 使用说明/  
│   └── 说明.md  
├── best.pt   
├── video_test.avi  
└── video_test.mp4
```
## 文件说明：
- `make_dataset`包含了我制作好的数据集、制作数据集所需的视频和.py文件
- **`使用说明`** 内有详细使用流程
- `best.pt`为使用制作好的数据集训练出的模型
- `video_test.avi`为使用`best.pt`预测的成果
- `video_test.mp4`为用于预测的视频源

