# 本脚本作用：将视频文件转化成图片，用于制作数据集
# 实现方式：按设定的间隔截取视频的帧，每一帧即为一张图片，存放到img文件夹
# 默认为每3帧截取一帧

import cv2
import os
from pathlib import Path


def extract_frames_from_videos(video_dir, output_dir, frame_interval=3):
    """
    从视频文件夹中每3帧截取一帧图片

    Args:
        video_dir: 视频文件夹路径
        output_dir: 输出图片文件夹路径
        frame_interval: 帧间隔（每多少帧截取一帧）
    """

    # 创建输出目录（如果不存在）
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 支持的视频格式
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']

    # 获取所有视频文件
    video_files = []
    for ext in video_extensions:
        video_files.extend(Path(video_dir).glob(f'*{ext}'))
        video_files.extend(Path(video_dir).glob(f'*{ext.upper()}'))

    # 去重并排序
    video_files = sorted(set(video_files))

    if not video_files:
        print(f"在 {video_dir} 中没有找到视频文件")
        return

    print(f"找到 {len(video_files)} 个视频文件")

    for video_path in video_files:
        # 获取视频名（不含扩展名）
        video_name = video_path.stem

        # 打开视频
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            print(f"无法打开视频: {video_path}")
            continue

        # 获取视频基本信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        print(f"\n处理视频: {video_name}")
        print(f"  总帧数: {total_frames}, FPS: {fps:.2f}")

        frame_count = 0
        saved_count = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            # 每 frame_interval 帧截取一帧（从第1帧开始）
            if frame_count % frame_interval == 0:
                # 生成文件名: 视频名_5位序号.jpg
                # 序号从1开始，格式化为5位数字
                sequence_num = saved_count + 1
                filename = f"{video_name}_{sequence_num:05d}.jpg"
                filepath = Path(output_dir) / filename

                # 保存图片
                cv2.imwrite(str(filepath), frame)
                saved_count += 1

                # 每保存100张打印一次进度
                if saved_count % 100 == 0:
                    print(f"    已保存 {saved_count} 张图片")

            frame_count += 1

        # 释放视频资源
        cap.release()

        print(f"  完成！从 {frame_count} 帧中截取了 {saved_count} 张图片")
        print(f"  保存位置: {output_dir}")

    print(f"\n所有视频处理完成！")


def main():
    # 设置路径
    video_dir = r'.\数据集视频'
    output_dir = r'.\img'
    frame_interval = 3  # 每3帧截取一帧

    # 执行截取
    extract_frames_from_videos(video_dir, output_dir, frame_interval)


if __name__ == "__main__":
    main()