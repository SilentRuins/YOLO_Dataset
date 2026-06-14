# 该脚本作用：将标注好的数据集标准化，即转换成yolo标准文件格式

import os
import shutil
import random
from pathlib import Path


def setup_yolo_dataset():
    # 定义路径
    img_source = 'img'  # 原始图片文件夹
    labels_source = 'labels'  # 原始标注文件夹
    target_dir = 'mydataset'  # 目标根目录

    # 创建目标文件夹结构
    images_dir = os.path.join(target_dir, 'images')
    labels_dir = os.path.join(target_dir, 'labels')
    train_images_dir = os.path.join(images_dir, 'train')
    val_images_dir = os.path.join(images_dir, 'val')
    train_labels_dir = os.path.join(labels_dir, 'train')
    val_labels_dir = os.path.join(labels_dir, 'val')

    # 创建所有必需的目录
    for dir_path in [train_images_dir, val_images_dir, train_labels_dir, val_labels_dir]:
        os.makedirs(dir_path, exist_ok=True)

    # 获取所有图片文件（支持常见格式）
    img_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
    img_files = []

    for file in os.listdir(img_source):
        if Path(file).suffix.lower() in img_extensions:
            img_files.append(file)

    if not img_files:
        print("错误：在 'img' 文件夹中没有找到图片文件！")
        return

    # 获取对应的标注文件（.txt格式）
    valid_pairs = []
    for img_file in img_files:
        img_name = Path(img_file).stem  # 不含扩展名的文件名
        label_file = img_name + '.txt'
        label_path = os.path.join(labels_source, label_file)

        if os.path.exists(label_path):
            valid_pairs.append((img_file, label_file))
        else:
            print(f"警告：图片 '{img_file}' 没有对应的标注文件，已跳过")

    if not valid_pairs:
        print("错误：没有找到任何图片和标注的配对文件！")
        return

    print(f"找到 {len(valid_pairs)} 对有效的图片-标注文件")

    # 随机打乱数据
    random.shuffle(valid_pairs)

    # 计算训练集和验证集的数量（8:2）
    val_count = int(len(valid_pairs) * 0.2)
    train_count = len(valid_pairs) - val_count

    train_pairs = valid_pairs[:train_count]
    val_pairs = valid_pairs[train_count:]

    print(f"训练集: {len(train_pairs)} 对")
    print(f"验证集: {len(val_pairs)} 对")

    # 复制文件到目标位置
    def copy_files(pairs, target_type):
        for img_file, label_file in pairs:
            # 复制图片
            src_img = os.path.join(img_source, img_file)
            dst_img = os.path.join(images_dir, target_type, img_file)
            shutil.copy2(src_img, dst_img)

            # 复制标注
            src_label = os.path.join(labels_source, label_file)
            dst_label = os.path.join(labels_dir, target_type, label_file)
            shutil.copy2(src_label, dst_label)

        print(f"{target_type}集: 已复制 {len(pairs)} 对文件")

    # 复制训练集和验证集
    copy_files(train_pairs, 'train')
    copy_files(val_pairs, 'val')

    # 创建数据集配置文件
    config_content = f"""# YOLO数据集配置文件
# 数据集路径
path: {os.path.abspath(target_dir)}  # 数据集根目录
train: images/train  # 训练集图片路径
val: images/val      # 验证集图片路径

# 类别数量（请根据实际情况修改）
nc: 1  # number of classes

# 类别名称（请根据实际情况修改）
names: ['object']  # class names
"""

    config_path = os.path.join(target_dir, 'dataset.yaml')
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)

    print(f"\n完成！数据集已创建在 '{target_dir}' 文件夹")
    print(f"配置文件已生成: {config_path}")
    print("\n注意：请根据实际类别数量修改 dataset.yaml 文件中的 'nc' 和 'names' 字段")


if __name__ == "__main__":
    # 设置随机种子以确保结果可重现
    random.seed(42)
    setup_yolo_dataset()