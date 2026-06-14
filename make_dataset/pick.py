# 该脚本作用：从源文件夹中按固定间隔抽取图片，分别复制到训练集和验证集
# 脚本制作的数据集用于初步标注并训练一个用于半自动标注的模型
# 默认抽取50张训练集图片，10张验证集图片

import shutil
from pathlib import Path


def extract_images_with_interval(source_dir, train_dir, val_dir,
                                 train_count=50, val_count=10):
    """
    从源文件夹中按固定间隔抽取图片，分别复制到训练集和验证集

    Args:
        source_dir: 源图片文件夹路径
        train_dir: 训练集目标文件夹路径
        val_dir: 验证集目标文件夹路径
        train_count: 训练集抽取数量（默认50）
        val_count: 验证集抽取数量（默认10）
    """

    # 创建目标目录
    Path(train_dir).mkdir(parents=True, exist_ok=True)
    Path(val_dir).mkdir(parents=True, exist_ok=True)

    # 获取所有图片文件（支持常见格式）
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    all_images = []

    for ext in image_extensions:
        all_images.extend(Path(source_dir).glob(f'*{ext}'))
        all_images.extend(Path(source_dir).glob(f'*{ext.upper()}'))

    # 排序以确保顺序一致
    all_images = sorted(set(all_images))
    total_images = len(all_images)

    print(f"在 {source_dir} 中找到 {total_images} 张图片")

    if total_images == 0:
        print("错误：没有找到任何图片文件！")
        return

    # 计算总共需要的图片数量
    total_needed = train_count + val_count

    if total_images < total_needed:
        print(f"警告：源图片数量({total_images})少于所需数量({total_needed})")
        print(f"将使用所有图片，训练集和验证集可能会有重叠")

        # 如果图片不够，使用所有图片，但按比例分配
        train_ratio = train_count / total_needed
        val_ratio = val_count / total_needed

        train_actual = max(1, int(total_images * train_ratio))
        val_actual = total_images - train_actual

        # 重新计算抽取策略
        train_indices = list(range(0, total_images, max(1, total_images // train_actual)))[:train_actual]
        val_indices = [i for i in range(total_images) if i not in train_indices][:val_actual]

        print(f"实际抽取：训练集 {len(train_indices)} 张，验证集 {len(val_indices)} 张")

    else:
        # 计算固定间隔
        # 我们希望均匀地抽取 total_needed 张图片
        interval = total_images / total_needed

        # 生成所有要抽取的索引（按顺序）
        all_indices = [int(i * interval) for i in range(total_needed)]

        # 前 train_count 个给训练集，后 val_count 个给验证集
        train_indices = all_indices[:train_count]
        val_indices = all_indices[train_count:train_count + val_count]

        print(f"抽取间隔：{interval:.2f}")
        print(f"训练集索引：{train_indices[:5]}... (共{train_count}个)")
        print(f"验证集索引：{val_indices[:5]}... (共{val_count}个)")

    # 复制训练集图片
    print(f"\n开始复制训练集图片到: {train_dir}")
    for i, idx in enumerate(train_indices, 1):
        if idx >= total_images:
            continue

        src_path = all_images[idx]
        # 保持原文件名
        dst_path = Path(train_dir) / src_path.name

        # 如果文件名冲突，添加前缀
        if dst_path.exists():
            dst_path = Path(train_dir) / f"train_{i}_{src_path.name}"

        shutil.copy2(src_path, dst_path)

        if i % 10 == 0:
            print(f"  已复制 {i}/{len(train_indices)} 张图片")

    print(f"训练集复制完成！共 {len(train_indices)} 张图片")

    # 复制验证集图片
    print(f"\n开始复制验证集图片到: {val_dir}")
    for i, idx in enumerate(val_indices, 1):
        if idx >= total_images:
            continue

        src_path = all_images[idx]
        # 保持原文件名
        dst_path = Path(val_dir) / src_path.name

        # 如果文件名冲突，添加前缀
        if dst_path.exists():
            dst_path = Path(val_dir) / f"val_{i}_{src_path.name}"

        shutil.copy2(src_path, dst_path)

        if i % 5 == 0:
            print(f"  已复制 {i}/{len(val_indices)} 张图片")

    print(f"验证集复制完成！共 {len(val_indices)} 张图片")

    # 输出统计信息
    print("\n" + "=" * 50)
    print("抽取完成！统计信息：")
    print(f"源图片总数：{total_images}")
    print(f"训练集图片：{len(train_indices)} 张")
    print(f"验证集图片：{len(val_indices)} 张")
    print(f"训练集路径：{train_dir}")
    print(f"验证集路径：{val_dir}")
    print("=" * 50)


def stratified_extract(source_dir, train_dir, val_dir,
                       train_count=50, val_count=10, by_name=True):
    """
    按文件名序号进行分层抽取（适用于文件名包含序号的图片）

    Args:
        source_dir: 源图片文件夹路径
        train_dir: 训练集目标文件夹路径
        val_dir: 验证集目标文件夹路径
        train_count: 训练集抽取数量
        val_count: 验证集抽取数量
        by_name: 是否按文件名序号排序（True）还是按修改时间（False）
    """

    # 创建目标目录
    Path(train_dir).mkdir(parents=True, exist_ok=True)
    Path(val_dir).mkdir(parents=True, exist_ok=True)
    Path(r'.\predata\labels\train').mkdir(parents=True, exist_ok=True)
    Path(r'.\predata\labels\val').mkdir(parents=True, exist_ok=True)

    # 获取所有图片文件
    all_images = list(Path(source_dir).glob('*.jpg')) + \
                 list(Path(source_dir).glob('*.jpeg')) + \
                 list(Path(source_dir).glob('*.png'))

    if by_name:
        # 按文件名排序（假设文件名包含序号）
        all_images.sort(key=lambda x: x.stem)
    else:
        # 按修改时间排序
        all_images.sort(key=lambda x: x.stat().st_mtime)

    total_images = len(all_images)
    total_needed = train_count + val_count

    print(f"找到 {total_images} 张图片")

    if total_images >= total_needed:
        # 计算间隔
        interval = total_images / total_needed
        step = interval

        # 使用更均匀的分布策略
        import random
        random.seed(42)  # 固定随机种子以确保结果可重复

        # 生成均匀分布的索引
        indices = [int(i * interval) for i in range(total_needed)]

        # 可选：添加少量随机扰动，使分布更自然
        # indices = [min(max(0, int(i * interval + random.uniform(-interval/3, interval/3))), total_images-1)
        #            for i in range(total_needed)]

        train_indices = indices[:train_count]
        val_indices = indices[train_count:]
    else:
        print(f"警告：图片数量({total_images})不足，将重复使用部分图片")
        # 循环使用图片
        import itertools
        cyclic_images = itertools.cycle(all_images)
        train_images = [next(cyclic_images) for _ in range(train_count)]
        val_images = [next(cyclic_images) for _ in range(val_count)]

        # 复制图片
        for i, src in enumerate(train_images, 1):
            dst = Path(train_dir) / src.name
            shutil.copy2(src, dst)
        for i, src in enumerate(val_images, 1):
            dst = Path(val_dir) / src.name
            shutil.copy2(src, dst)

        print(f"完成！训练集：{len(train_images)}，验证集：{len(val_images)}")
        return

    # 复制图片
    print(f"复制训练集图片 ({len(train_indices)}张)...")
    for idx in train_indices:
        src = all_images[idx]
        dst = Path(train_dir) / src.name
        shutil.copy2(src, dst)

    print(f"复制验证集图片 ({len(val_indices)}张)...")
    for idx in val_indices:
        src = all_images[idx]
        dst = Path(val_dir) / src.name
        shutil.copy2(src, dst)

    print(f"\n完成！")
    print(f"训练集图片索引：{train_indices[:5]}...")
    print(f"验证集图片索引：{val_indices[:5]}...")


def main():
    # 设置路径
    source_dir = r'.\img'  # 源图片文件夹
    train_dir = r'.\predata\images\train'  # 训练集文件夹
    val_dir = r'.\predata\images\val'  # 验证集文件夹

    # 设置抽取数量
    train_count = 50  # 训练集抽取50张
    val_count = 10  # 验证集抽取10张

    # 方法1：使用固定间隔均匀抽取
    print("=" * 50)
    print("方法1：固定间隔均匀抽取")
    print("=" * 50)
    extract_images_with_interval(source_dir, train_dir, val_dir,
                                 train_count, val_count)

    # 方法2：使用分层抽取（按文件名序号）
    # 取消下面的注释来使用方法2
    # print("\n" + "="*50)
    # print("方法2：按文件名序号分层抽取")
    # print("="*50)
    # stratified_extract(source_dir, train_dir, val_dir,
    #                   train_count, val_count, by_name=True)


if __name__ == "__main__":
    main()