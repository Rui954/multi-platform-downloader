# -*- coding: utf-8 -*-
"""一键准备第三方依赖。"""

import subprocess
from pathlib import Path

REPOS = [
    ("https://github.com/belingud/douyin-downloader-skill.git",
     "douyin-downloader-skill"),
    ("https://github.com/zhoulianglen/fanqiexiaoshuo-Download.git",
     "fanqiexiaoshuo-Download"),
    ("https://github.com/JoeanAmier/KS-Downloader.git",
     "KS-Downloader"),
]


def main():
    base = Path(__file__).parent / "third_party"
    base.mkdir(exist_ok=True)

    for url, name in REPOS:
        target = base / name
        if target.exists():
            print(f"[跳过] {name} 已存在")
            continue
        print(f"[克隆] {name}")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", url, str(target)],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"  克隆失败: {e}")
            return

    print("\n[完成] 三方依赖已准备好。")
    print("请记得单独安装 KS-Downloader 的依赖：")
    print("  cd third_party/KS-Downloader")
    print("  pip install -r requirements.txt")


if __name__ == "__main__":
    main()
