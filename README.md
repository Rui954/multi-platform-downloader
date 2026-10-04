# multi-platform-downloader

一个基于 PySide6 的多平台内容下载工具，支持 B 站、抖音、番茄小说、快手等平台。

> ⚠️ **本项目仅供学习和技术研究使用。请在下载完成后的 24 小时内主动删除所下载的全部内容。请勿将本工具用于任何商业用途、批量分发或侵犯他人版权的行为。**

## 功能特性

- **B 站**：通过 [bilibili-api-python](https://github.com/Nemo2011/bilibili-api) 下载视频。支持扫码登录，登录后可下载 1080P 高清视频。
- **抖音**：通过 [douyin-downloader-skill](https://github.com/belingud/douyin-downloader-skill) 下载无水印视频 / 图文，自动识别 `modal_id` 格式链接。
- **番茄小说**：本地解析，自动解密字体加密。仅可获取免费章节，付费章节自动跳过。
- **快手**：通过 [KS-Downloader](https://github.com/JoeanAmier/KS-Downloader) 下载，短链自动重定向。
- **其他平台**：走 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 通用解析。

## 环境要求

- Python 3.10 或更高版本（推荐 3.12）
- Windows / macOS / Linux
- FFmpeg（用于音视频合并）

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/Rui954/multi-platform-downloader.git
cd multi-platform-downloader