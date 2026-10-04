# -*- coding: utf-8 -*-
"""
多平台内容下载器 — 单文件自包含版本

依赖安装：
    pip install PySide6 yt-dlp bilibili-api-python aiohttp httpx requests lxml ^
                ebooklib tqdm beautifulsoup4 qrcode pillow flask jinja2 ^
                pyyaml fonttools brotli pyinstaller
"""

import sys, os, re, io, json, time, shutil, subprocess, threading, traceback
import importlib.util, contextlib, builtins, urllib.request
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QFileDialog, QGroupBox, QMessageBox, QProgressBar, QDialog,
    QCheckBox, QTextBrowser, QFrame
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QPixmap


# ============================================================
#  全局样式表
# ============================================================
APP_STYLE = """
QWidget {
    font-family: "Microsoft YaHei UI", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #1F2937;
}
QMainWindow, QDialog { background: #F5F7FA; }
QFrame#Card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
}
QLabel#Title { font-size: 22px; font-weight: 600; color: #111827; }
QLabel#Subtitle { font-size: 12px; color: #6B7280; }
QLabel#Banner {
    background: #FEF3C7; color: #92400E; padding: 12px 16px;
    border-radius: 8px; font-size: 13px; border-left: 4px solid #F59E0B;
}
QPushButton {
    background: #FFFFFF; color: #374151;
    border: 1px solid #D1D5DB; border-radius: 6px;
    padding: 8px 16px; min-height: 20px; font-size: 13px;
}
QPushButton:hover { background: #F9FAFB; border-color: #9CA3AF; }
QPushButton:pressed { background: #F3F4F6; }
QPushButton:disabled { color: #9CA3AF; background: #F9FAFB; border-color: #E5E7EB; }
QPushButton#Primary {
    background: #2563EB; color: #FFFFFF; border: none;
    border-radius: 6px; padding: 10px 22px; font-size: 13px;
    font-weight: 600; min-height: 22px;
}
QPushButton#Primary:hover { background: #1D4ED8; }
QPushButton#Primary:pressed { background: #1E40AF; }
QPushButton#Primary:disabled { background: #93C5FD; color: #FFFFFF; }
QPushButton#Danger {
    background: #FFFFFF; color: #DC2626; border: 1px solid #FCA5A5;
    border-radius: 6px; padding: 10px 22px; font-size: 13px; min-height: 22px;
}
QPushButton#Danger:hover { background: #FEF2F2; border-color: #EF4444; }
QPushButton#Danger:disabled { color: #FCA5A5; background: #FEF2F2; border-color: #FECACA; }
QPushButton#Login {
    background: #FFFFFF; color: #059669; border: 1px solid #6EE7B7;
    border-radius: 6px; padding: 10px 22px; font-size: 13px; min-height: 22px;
}
QPushButton#Login:hover { background: #ECFDF5; border-color: #10B981; }
QLineEdit {
    background: #FFFFFF; border: 1px solid #D1D5DB; border-radius: 6px;
    padding: 9px 12px; font-size: 13px; selection-background-color: #BFDBFE;
}
QLineEdit:hover { border-color: #9CA3AF; }
QLineEdit:focus { border: 2px solid #2563EB; padding: 8px 11px; }
QComboBox {
    background: #FFFFFF; border: 1px solid #D1D5DB; border-radius: 6px;
    padding: 8px 12px; font-size: 13px; min-height: 22px;
}
QComboBox:hover { border-color: #9CA3AF; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent; border-right: 5px solid transparent;
    border-top: 6px solid #6B7280; width: 0; height: 0; margin-right: 8px;
}
QComboBox QAbstractItemView {
    background: #FFFFFF; border: 1px solid #D1D5DB; border-radius: 6px;
    padding: 4px; selection-background-color: #DBEAFE;
    selection-color: #1E40AF; outline: none;
}
QTextEdit#LogBox {
    background: #0F172A; color: #E2E8F0;
    border: 1px solid #1E293B; border-radius: 8px; padding: 10px;
    font-family: "Cascadia Code", "Consolas", "Menlo", monospace;
    font-size: 12px; selection-background-color: #334155;
}
QProgressBar {
    background: #E5E7EB; border: none; border-radius: 6px; height: 18px;
    text-align: center; font-size: 11px; color: #374151;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3B82F6, stop:1 #06B6D4);
    border-radius: 6px;
}
QCheckBox { spacing: 8px; font-size: 13px; }
QCheckBox::indicator {
    width: 16px; height: 16px; border: 1px solid #D1D5DB;
    border-radius: 3px; background: #FFFFFF;
}
QCheckBox::indicator:hover { border-color: #2563EB; }
QCheckBox::indicator:checked { background: #2563EB; border-color: #2563EB; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 0; }
QScrollBar::handle:vertical {
    background: #CBD5E1; border-radius: 5px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #94A3B8; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 0; }
QScrollBar::handle:horizontal {
    background: #CBD5E1; border-radius: 5px; min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #94A3B8; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: transparent; }
QTextBrowser {
    background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px;
    padding: 12px; font-size: 13px;
}
"""


# ============================================================
#  资源与路径工具
# ============================================================
def resource_path(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def user_data_dir() -> Path:
    d = Path.home() / ".multi_dl"
    d.mkdir(parents=True, exist_ok=True)
    return d


CREDENTIAL_FILE = user_data_dir() / "bili_credential.json"


def save_credential(credential) -> bool:
    try:
        data = {
            "sessdata": credential.sessdata or "",
            "bili_jct": credential.bili_jct or "",
            "buvid3": credential.buvid3 or "",
            "dedeuserid": credential.dedeuserid or "",
        }
        CREDENTIAL_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    except Exception as e:
        print(f"[登录] 保存凭证失败: {e}", flush=True)
        return False


def load_credential():
    if not CREDENTIAL_FILE.exists():
        return None
    try:
        from bilibili_api import Credential
        data = json.loads(CREDENTIAL_FILE.read_text(encoding="utf-8"))
        return Credential(
            sessdata=data.get("sessdata", ""),
            bili_jct=data.get("bili_jct", ""),
            buvid3=data.get("buvid3", ""),
            dedeuserid=data.get("dedeuserid", ""),
        )
    except Exception as e:
        print(f"[登录] 加载凭证失败: {e}", flush=True)
        return None


# ============================================================
#  首次运行的完整免责声明对话框
# ============================================================
DISCLAIMER_HTML = """
<h2 style='color:#c0392b; margin: 0 0 12px 0;'>⚠️ 使用前须知</h2>

<p style='font-size:13px; line-height:1.7;'><b>本工具仅供学习和技术研究使用。</b>
请在下载完成后的 <b style='color:#c0392b;'>24 小时内主动删除</b> 所下载的全部内容。
请勿将本工具用于任何商业用途、批量分发或侵犯他人版权的行为。</p>

<h3 style='color:#374151;'>法律提示</h3>
<ul style='line-height:1.7;'>
<li>下载的内容版权归原作者或平台所有，使用者需自行承担因传播、商用、二次分发所产生的法律责任。</li>
<li>请遵守各平台的《用户协议》与《服务条款》。</li>
<li>禁止下载、传播任何违法违规内容。</li>
<li>请勿绕过平台的付费机制获取受版权保护的内容。</li>
<li>本程序已在github上开源，欢迎贡献代码和提出建议。</li>
<li><a href="https://github.com/Rui954/multi-platform-downloader" target="_blank">项目链接</a></li>
</ul>

<h3 style='color:#374151;'>技术注意事项</h3>
<ul style='line-height:1.7;'>
<li>B 站：点击"登录B站"扫码后可以下载 1080P。未登录时最高 480P。</li>
<li>抖音：接口可能随平台更新失效。若解析失败，程序会自动降级到 yt-dlp 再试一次。</li>
<li>番茄小说：本地解析，字体加密自动解密。仅可获取免费章节，付费章节自动跳过。</li>
<li>快手：通过 KS-Downloader 下载，需要 Python 3.12+ 和 curl_cffi 支持。</li>
<li>其他平台：走 yt-dlp 通用解析，稳定性视上游维护情况而定。</li>
</ul>

<h3 style='color:#374151;'>免责声明</h3>
<p style='color:#555; font-size:12px; line-height:1.7;'>
本程序按“现状”提供，不附带任何形式的担保。作者不对使用本程序造成的任何直接或间接损失负责，
包括但不限于数据丢失、账号封禁、法律纠纷。继续使用即表示你已阅读、理解并同意上述条款。
</p>
"""


class DisclaimerDialog(QDialog):
    """首次运行：必须勾选同意才能进入。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用须知与免责声明")
        self.resize(640, 680)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(DISCLAIMER_HTML)
        layout.addWidget(browser, 1)

        self.chk = QCheckBox(
            "我已阅读并同意上述条款，仅用于个人学习，24 小时内删除下载内容"
        )
        layout.addWidget(self.chk)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.btn_cancel = QPushButton("退出")
        self.btn_cancel.setMinimumWidth(90)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_ok = QPushButton("同意并继续")
        self.btn_ok.setObjectName("Primary")
        self.btn_ok.setMinimumWidth(120)
        self.btn_ok.setEnabled(False)
        self.btn_ok.clicked.connect(self.accept)

        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_ok)
        layout.addLayout(btn_row)

        self.chk.toggled.connect(self._on_chk_toggled)

    def _on_chk_toggled(self, checked: bool):
        self.btn_ok.setEnabled(bool(checked))


# ============================================================
#  每次启动的轻量提醒对话框
# ============================================================
STARTUP_NOTICE_HTML = """
<p style='font-size:13px; line-height:1.8; color:#374151;'>
感谢使用本工具。在开始之前，请再次确认以下内容：
</p>

<ul style='font-size:13px; line-height:1.9; color:#374151;'>
<li>本工具 <b>仅供学习与参考</b>，请勿用于任何商业用途。</li>
<li>所有下载内容请在 <b style='color:#c0392b;'>24 小时内主动删除</b>。</li>
<li>请遵守各平台的服务条款，尊重原作者版权。</li>
<li>禁止下载、传播任何违法违规内容。</li>
<li>请勿绕过平台的付费机制获取受版权保护的内容。</li>
<li>使用本工具所产生的任何后果由使用者自行承担。</li>
<li>本程序已在github上开源，欢迎贡献代码和提出建议。</li>
<li><a href="https://github.com/Rui954/multi-platform-downloader" target="_blank">项目链接</a></li>
</ul>

<p style='color:#6B7280; font-size:12px; line-height:1.7; margin-top:16px;'>
继续使用即表示你已阅读、理解并同意上述内容。
</p>
"""


class StartupNoticeDialog(QDialog):
    """每次启动的提醒：点击「我知道了」进入主界面。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("温馨提示")
        self.resize(520, 460)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("⚠️ 温馨提示")
        title.setStyleSheet(
            "font-size:18px; font-weight:600; color:#c0392b; padding:4px 0;"
        )
        layout.addWidget(title)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(STARTUP_NOTICE_HTML)
        layout.addWidget(browser, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.btn_exit = QPushButton("退出")
        self.btn_exit.setMinimumWidth(90)
        self.btn_exit.clicked.connect(self.reject)

        self.btn_ok = QPushButton("我知道了，进入程序")
        self.btn_ok.setObjectName("Primary")
        self.btn_ok.setMinimumWidth(160)
        self.btn_ok.clicked.connect(self.accept)

        btn_row.addWidget(self.btn_exit)
        btn_row.addWidget(self.btn_ok)
        layout.addLayout(btn_row)


# ============================================================
#  B站扫码登录对话框
# ============================================================
class LoginDialog(QDialog):
    qr_bytes_ready = Signal(bytes)
    status_changed = Signal(str)
    login_done = Signal(object)
    login_failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("B站扫码登录")
        self.resize(380, 580)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        self.tip_label = QLabel("请使用 B站 App 扫描下方二维码")
        self.tip_label.setAlignment(Qt.AlignCenter)
        self.tip_label.setStyleSheet(
            "font-size:14px; font-weight:600; color:#111827; padding:4px;"
        )
        layout.addWidget(self.tip_label)

        qr_wrap = QFrame()
        qr_wrap.setObjectName("Card")
        qr_wrap.setFixedSize(320, 320)
        qr_inner = QVBoxLayout(qr_wrap)
        qr_inner.setContentsMargins(10, 10, 10, 10)
        self.qr_label = QLabel("正在生成二维码...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet("color:#9CA3AF; font-size:13px;")
        qr_inner.addWidget(self.qr_label)
        layout.addWidget(qr_wrap, alignment=Qt.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "color:#6B7280; font-size:13px; padding:6px;"
        )
        layout.addWidget(self.status_label)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumHeight(34)
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)

        self.qr_bytes_ready.connect(self._on_qr_ready)
        self.status_changed.connect(self._on_status)
        self.login_done.connect(self._on_login_ok)
        self.login_failed.connect(self._on_login_fail)

        self._login = None
        self._polling = True
        self._start_login()

    def _start_login(self):
        threading.Thread(target=self._login_worker, daemon=True).start()

    def _login_worker(self):
        import asyncio
        try:
            asyncio.run(self._async_login())
        except Exception as e:
            self.login_failed.emit(f"{e}\n{traceback.format_exc()}")

    async def _async_login(self):
        try:
            from bilibili_api.login_v2 import QrCodeLogin
        except ImportError as e:
            self.login_failed.emit(f"导入登录模块失败: {e}")
            return

        try:
            login = QrCodeLogin()
            await login.generate_qrcode()
        except Exception as e:
            self.login_failed.emit(f"生成二维码失败: {e}\n{traceback.format_exc()}")
            return
        self._login = login

        try:
            pic = login.get_qrcode_picture()
        except Exception as e:
            self.login_failed.emit(f"获取二维码图片失败: {e}")
            return

        png_bytes = self._extract_png_bytes(pic)
        if png_bytes is None:
            self.login_failed.emit(f"未知的二维码图片类型: {type(pic)}")
            return

        self.qr_bytes_ready.emit(png_bytes)

        while self._polling:
            try:
                state = await login.check_state()
            except Exception as e:
                self.login_failed.emit(f"轮询状态失败: {e}")
                return

            name = getattr(state, "name", str(state))
            value = getattr(state, "value", state)

            if name == "DONE" or value in (0, "0"):
                self.status_changed.emit("✅ 登录成功")
                try:
                    cred = login.get_credential()
                    self.login_done.emit(cred)
                except Exception as e:
                    self.login_failed.emit(f"获取凭证失败: {e}")
                return
            elif name == "SCAN" or value in (86101, "86101"):
                self.status_changed.emit("等待扫码...")
            elif name == "CONF" or value in (86090, "86090"):
                self.status_changed.emit("已扫码，请在手机上确认")
            elif name == "TIMEOUT" or value in (86038, "86038"):
                self.status_changed.emit("二维码已过期")
                self.login_failed.emit("二维码已过期，请重新登录")
                return
            else:
                self.status_changed.emit(f"等待中... ({name})")

            import asyncio as _a
            await _a.sleep(2)

    def _extract_png_bytes(self, pic):
        from io import BytesIO
        if pic is None:
            return None
        if hasattr(pic, "content"):
            try:
                c = pic.content
                if isinstance(c, bytes):
                    return c
            except Exception:
                pass
        if isinstance(pic, (bytes, bytearray)):
            return bytes(pic)
        if hasattr(pic, "save"):
            try:
                buf = BytesIO()
                try:
                    pic.save(buf, format="PNG")
                except TypeError:
                    pic.save(buf)
                return buf.getvalue()
            except Exception:
                pass
        if hasattr(pic, "read"):
            try:
                pic.seek(0)
            except Exception:
                pass
            try:
                return pic.read()
            except Exception:
                pass
        return None

    def _on_qr_ready(self, png_bytes: bytes):
        pixmap = QPixmap()
        if not pixmap.loadFromData(png_bytes):
            self.status_label.setText("二维码加载失败")
            return
        size = min(self.qr_label.width(), self.qr_label.height())
        if size < 100:
            size = 280
        scaled = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.qr_label.setPixmap(scaled)

    def _on_status(self, text: str):
        self.status_label.setText(text)

    def _on_login_ok(self, credential):
        self._polling = False
        self.accept()

    def _on_login_fail(self, msg: str):
        self._polling = False
        self.status_label.setText(msg.split("\n")[0])
        QMessageBox.warning(self, "登录失败", msg)

    def closeEvent(self, e):
        self._polling = False
        e.accept()


# ============================================================
#  日志与进度信号桥
# ============================================================
class LogEmitter(QObject):
    log = Signal(str)
    progress = Signal(int, int, str)


# ============================================================
#  stdout 捕获
# ============================================================
class _StdoutCapture:
    def __init__(self, log_cb, prefix=""):
        self.log = log_cb
        self.prefix = prefix
        self._buf = ""

    def write(self, s):
        if "\r" in s and "\n" not in s:
            return
        self._buf += s
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            line = line.strip()
            if line:
                self.log(self.prefix + line)

    def flush(self):
        if self._buf.strip():
            self.log(self.prefix + self._buf.strip())
            self._buf = ""


# ============================================================
#  处理器基类
# ============================================================
class BaseHandler:
    def __init__(self, log_cb, progress_cb):
        self.log = log_cb
        self.progress = progress_cb
        self._stop = False

    def stop(self):
        self._stop = True

    def download(self, url: str, out_dir: str) -> bool:
        raise NotImplementedError


# ============================================================
#  B站处理器
# ============================================================
class Bili23Handler(BaseHandler):

    def download(self, url: str, out_dir: str) -> bool:
        credential = load_credential()
        if credential:
            self.log("[B站] 已加载登录凭证，将尝试获取高清画质")
        else:
            self.log("[B站] 未检测到登录凭证，将下载 480P 及以下画质")
            self.log("[B站] 提示：在主界面点击「登录B站」可提升到 1080P")

        ffmpeg_dir = self._ensure_ffmpeg()
        if ffmpeg_dir:
            self.log(f"[B站] 使用 ffmpeg: {ffmpeg_dir}")

        try:
            import asyncio
            cap = _StdoutCapture(self.log, prefix="[B站] ")
            with contextlib.redirect_stdout(cap), contextlib.redirect_stderr(cap):
                ok = asyncio.run(self._async_download(url, out_dir, ffmpeg_dir, credential))
            cap.flush()
            if ok:
                self.log("[B站] ✅ 下载完成")
            return ok
        except Exception as e:
            self.log(f"[B站] ❌ {e}")
            self.log(traceback.format_exc())
            return False

    async def _async_download(self, url, out_dir, ffmpeg_dir, credential):
        from bilibili_api import video
        bvid_match = re.search(r"(BV[0-9A-Za-z]+)", url)
        if not bvid_match:
            self.log("[B站] ❌ 无法从链接中提取 BV 号")
            return False
        bvid = bvid_match.group(1)
        self.log(f"[B站] BV 号: {bvid}")

        v = video.Video(bvid=bvid, credential=credential)
        info = await v.get_info()
        title = info.get("title", bvid)
        self.log(f"[B站] 标题: {title}")

        download_info = await v.get_download_url(0)
        self.log("[B站] 已获取视频流信息")

        dash = download_info.get("dash")
        if not dash:
            durl = download_info.get("durl", [])
            if durl:
                self.log("[B站] 使用 durl 格式下载")
                return await self._download_durl(durl, title, out_dir)
            self.log("[B站] ❌ 无法获取视频流")
            return False

        video_streams = dash.get("video", [])
        audio_streams = dash.get("audio", [])
        if not video_streams or not audio_streams:
            self.log("[B站] ❌ 未找到可用的音视频流")
            return False

        best_video = max(video_streams, key=lambda x: x.get("bandwidth", 0))
        best_audio = max(audio_streams, key=lambda x: x.get("bandwidth", 0))

        v_height = best_video.get("height", "?")
        v_codecs = best_video.get("codecs", "?")
        self.log(f"[B站] 选择视频流: {v_height}P, codec={v_codecs}, "
                 f"bandwidth={best_video.get('bandwidth', 0)}")

        video_url = best_video.get("baseUrl") or best_video.get("base_url")
        audio_url = best_audio.get("baseUrl") or best_audio.get("base_url")
        if not video_url or not audio_url:
            self.log("[B站] ❌ 未找到有效的流地址")
            return False

        import aiohttp
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
        }

        video_tmp = os.path.join(out_dir, f"{bvid}_video.m4s")
        audio_tmp = os.path.join(out_dir, f"{bvid}_audio.m4s")

        async with aiohttp.ClientSession(headers=headers) as session:
            self.log("[B站] 下载视频流...")
            await self._download_stream(session, video_url, video_tmp)
            self.log("[B站] 下载音频流...")
            await self._download_stream(session, audio_url, audio_tmp)

        safe_title = re.sub(r'[\\/*?:"<>|]', '_', title)
        output_path = os.path.join(out_dir, f"{safe_title}.mp4")
        self.log("[B站] 合并音视频...")

        if ffmpeg_dir:
            ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
        else:
            ffmpeg_exe = shutil.which("ffmpeg") or "ffmpeg"

        merge_cmd = [
            ffmpeg_exe, "-y", "-i", video_tmp, "-i", audio_tmp,
            "-c:v", "copy", "-c:a", "copy", output_path,
        ]
        result = subprocess.run(
            merge_cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if result.returncode != 0:
            self.log(f"[B站] ❌ 合并失败: {(result.stderr or '')[:500]}")
            return False

        for tmp in [video_tmp, audio_tmp]:
            try:
                os.remove(tmp)
            except Exception:
                pass

        self.log(f"[B站] ✅ 已保存: {output_path}")
        return True

    async def _download_stream(self, session, url: str, path: str):
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"下载失败，HTTP {resp.status}")
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            last_pct = -1
            with open(path, "wb") as f:
                async for chunk in resp.content.iter_chunked(8192):
                    if self._stop:
                        raise Exception("用户已停止")
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded * 100 // total
                        if pct != last_pct and pct % 10 == 0:
                            last_pct = pct
                            self.log(f"[B站] 进度: {pct}%")

    async def _download_durl(self, durl, title, out_dir):
        import aiohttp
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
        }
        safe_title = re.sub(r'[\\/*?:"<>|]', '_', title)
        output_path = os.path.join(out_dir, f"{safe_title}.mp4")
        async with aiohttp.ClientSession(headers=headers) as session:
            for i, part in enumerate(durl):
                part_url = part.get("url")
                if not part_url:
                    continue
                if len(durl) > 1:
                    part_path = os.path.join(out_dir, f"{safe_title}_part{i}.mp4")
                else:
                    part_path = output_path
                self.log(f"[B站] 下载第 {i+1}/{len(durl)} 部分...")
                await self._download_stream(session, part_url, part_path)
        return True

    def _ensure_ffmpeg(self) -> str:
        if shutil.which("ffmpeg"):
            return ""
        cache = user_data_dir() / "bin"
        cache.mkdir(parents=True, exist_ok=True)
        dst = cache / "ffmpeg.exe"
        if not dst.exists():
            src = resource_path("bin/ffmpeg.exe")
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dst)
                    self.log(f"[B站] ffmpeg 已释放到: {dst}")
                except Exception as e:
                    self.log(f"[B站] ffmpeg 释放失败: {e}")
                    return ""
            else:
                return ""
        return str(cache)


# ============================================================
#  抖音处理器
# ============================================================
_douyin_module_cache = None


class DouyinHandler(BaseHandler):
    def download(self, url: str, out_dir: str) -> bool:
        url = self._normalize_url(url)
        self.log(f"[抖音] 规范化后 URL = {url}")

        mod = self._load_module()
        if mod is None:
            self.log("[抖音] 未找到内嵌脚本，降级到 yt-dlp")
            return YtdlpHandler(self.log, self.progress).download(url, out_dir)

        self.log("[抖音] 调用 douyin-downloader-skill...")
        try:
            cap = _StdoutCapture(self.log, prefix="[抖音] ")
            with contextlib.redirect_stdout(cap), contextlib.redirect_stderr(cap):
                ok = mod.run(url, out_dir)
            cap.flush()
            if ok:
                self.log("[抖音] ✅ 下载完成")
                return True
            self.log("[抖音] ❌ 解析或下载失败，降级到 yt-dlp 再试")
            return YtdlpHandler(self.log, self.progress).download(url, out_dir)
        except Exception as e:
            self.log(f"[抖音] ❌ 调用异常: {e}，降级到 yt-dlp")
            self.log(traceback.format_exc())
            return YtdlpHandler(self.log, self.progress).download(url, out_dir)

    def _normalize_url(self, url: str) -> str:
        url = url.strip()
        m = re.search(r"[?&](modal_id|note_id|item_id|video_id)=(\d+)", url)
        if m and "douyin.com" in url:
            content_id = m.group(2)
            kind = "note" if m.group(1) == "note_id" else "video"
            normalized = f"https://www.douyin.com/{kind}/{content_id}"
            self.log(f"[抖音] URL 已规范化：{url} → {normalized}")
            return normalized
        return url

    def _load_module(self):
        global _douyin_module_cache
        if _douyin_module_cache is not None:
            return _douyin_module_cache
        script = self._locate_script()
        if not script:
            return None
        try:
            spec = importlib.util.spec_from_file_location("douyin_dl_download", script)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["douyin_dl_download"] = mod
            spec.loader.exec_module(mod)
            _douyin_module_cache = mod
            self.log("[抖音] 模块加载成功")
            return mod
        except Exception as e:
            self.log(f"[抖音] 加载脚本失败: {e}")
            self.log(traceback.format_exc())
            return None

    def _locate_script(self):
        base = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            resource_path("douyin_dl/download.py"),
            os.path.join(base, "third_party", "douyin-downloader-skill", "download.py"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return None


# ============================================================
#  番茄小说处理器
# ============================================================
_FANQIE_FONT_MAP_CACHE = None


class FanqieHandler(BaseHandler):

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/133.0.0.0 Safari/537.36"
        ),
    }

    def download(self, url: str, out_dir: str) -> bool:
        try:
            url_type, url_id = self._parse_url(url)
        except ValueError as e:
            self.log(f"[番茄] ❌ {e}")
            return False

        font_map = self._load_font_map()
        if not font_map:
            self.log("[番茄] ❌ 无法加载字体映射表（FONT_MAP）")
            return False
        self.log(f"[番茄] FONT_MAP 已加载，共 {len(font_map)} 条")

        if url_type == "reader":
            self.log("[番茄] 从章节页获取书籍信息...")
            reader_html = self._fetch_url(f"https://fanqienovel.com/reader/{url_id}")
            rstate = self._extract_initial_state(reader_html)
            book_id = rstate["reader"]["chapterData"]["bookId"]
        else:
            book_id = url_id

        self.log("[番茄] 获取小说目录...")
        book_html = self._fetch_url(f"https://fanqienovel.com/page/{book_id}")
        state = self._extract_initial_state(book_html)
        book_name = state["page"]["bookName"]
        chapters = []
        for volume in state["page"]["chapterListWithVolume"]:
            for ch in volume:
                chapters.append({
                    "item_id": ch["itemId"],
                    "title": ch.get("title", ""),
                    "is_locked": ch.get("isChapterLock", False),
                })
        self.log(f"[番茄] 小说: {book_name}")
        self.log(f"[番茄] 共 {len(chapters)} 章")

        safe_book = re.sub(r'[\\/:*?"<>|]', "_", book_name).strip()
        output_dir = os.path.join(out_dir, safe_book)
        os.makedirs(output_dir, exist_ok=True)
        self.log(f"[番茄] 输出目录: {output_dir}")

        downloaded = 0
        skipped = 0
        for i, ch in enumerate(chapters, 1):
            if self._stop:
                self.log("[番茄] 已停止")
                return False

            prefix = f"[{i}/{len(chapters)}]"

            if ch["is_locked"]:
                self.log(f"[番茄] {prefix} 跳过（需付费）: {ch['title']}")
                skipped += 1
                continue

            self.log(f"[番茄] {prefix} 下载: {ch['title']}...")
            try:
                title, content = self._download_chapter(ch["item_id"], font_map)
                md = f"# {title}\n\n{content}\n"
                safe_title = re.sub(r'[\\/:*?"<>|]', "_", title).strip()
                filename = f"{i:03d}-{safe_title}.md"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(md)
                downloaded += 1
            except Exception as e:
                self.log(f"[番茄] {prefix} ❌ 失败: {e}")

            time.sleep(0.5)

        self.log(f"[番茄] ✅ 完成！成功 {downloaded} 章，跳过 {skipped} 章（需付费）")
        self.log(f"[番茄] 文件保存在: {output_dir}")
        return downloaded > 0

    def _parse_url(self, url):
        m = re.search(r"fanqienovel\.com/(reader|page)/(\d+)", url)
        if not m:
            raise ValueError(f"无法解析番茄 URL: {url}")
        return m.group(1), m.group(2)

    def _load_font_map(self):
        global _FANQIE_FONT_MAP_CACHE
        if _FANQIE_FONT_MAP_CACHE is not None:
            return _FANQIE_FONT_MAP_CACHE

        base = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            resource_path("fanqie_dl/download.py"),
            os.path.join(base, "third_party",
                         "fanqiexiaoshuo-Download", "download.py"),
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    spec = importlib.util.spec_from_file_location("_fanqie_map_mod", p)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    font_map = getattr(mod, "FONT_MAP", None)
                    if font_map:
                        _FANQIE_FONT_MAP_CACHE = font_map
                        return font_map
                except Exception as e:
                    self.log(f"[番茄] 加载 {p} 失败: {e}")
        return None

    def _fetch_url(self, url):
        req = urllib.request.Request(url, headers=self.HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")

    def _fetch_bytes(self, url):
        req = urllib.request.Request(url, headers=self.HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()

    def _extract_initial_state(self, html):
        marker = "window.__INITIAL_STATE__="
        start = html.find(marker)
        if start == -1:
            raise ValueError("无法从页面中提取 __INITIAL_STATE__")
        start += len(marker)
        depth = 0
        end = start
        for i in range(start, len(html)):
            if html[i] == "{":
                depth += 1
            elif html[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        return json.loads(html[start:end])

    def _build_font_mapping(self, html, font_map):
        try:
            from fontTools.ttLib import TTFont
        except ImportError:
            self.log("[番茄] ⚠ fontTools 未安装，无法解密字体")
            return {}

        css = ""
        try:
            state = self._extract_initial_state(html)
            css = state.get("common", {}).get("css", "") or ""
        except Exception:
            pass

        font_url = None
        for pattern in [
            r'url\(["\']?(https?://[^)"\']+\.woff2)["\']?\)',
            r'url\(["\']?(https?://[^)"\']+\.woff)["\']?\)',
            r'url\(["\']?(https?://[^)"\']+\.otf)["\']?\)',
            r'(https?://[^"\'\s)]+\.woff2)',
        ]:
            m = re.search(pattern, css)
            if m:
                font_url = m.group(1)
                break

        if not font_url:
            for pattern in [
                r'url\(["\']?(https?://[^)"\']+\.woff2)["\']?\)',
                r'url\(["\']?(https?://[^)"\']+\.woff)["\']?\)',
                r'(https?://[^"\'\s)]+\.woff2)',
            ]:
                m = re.search(pattern, html)
                if m:
                    font_url = m.group(1)
                    break

        if not font_url:
            return {}

        try:
            font_data = self._fetch_bytes(font_url)
            font = TTFont(io.BytesIO(font_data))
            cmap = font.getBestCmap()
        except Exception as e:
            self.log(f"[番茄] ⚠ 字体解析失败: {e}")
            return {}

        mapping = {}
        for pua_codepoint, glyph_name in cmap.items():
            gid = glyph_name.replace("gid", "")
            if gid in font_map:
                mapping[chr(pua_codepoint)] = font_map[gid]
        return mapping

    def _decrypt(self, text, mapping):
        if not mapping:
            return text
        return "".join(mapping.get(ch, ch) for ch in text)

    def _html_to_markdown(self, html_content):
        text = html_content
        text = re.sub(r"<img[^>]*>", "", text)
        text = re.sub(r"</img>", "", text)
        text = re.sub(r"<p[^>]*>", "", text)
        text = re.sub(r"</p>", "\n\n", text)
        text = re.sub(r"<br\s*/?>", "\n", text)
        text = re.sub(r"<[^>]+>", "", text)
        text = text.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")
        text = text.replace("&amp;", "&").replace("&quot;", '"')
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _download_chapter(self, item_id, font_map):
        url = f"https://fanqienovel.com/reader/{item_id}"
        html = self._fetch_url(url)
        state = self._extract_initial_state(html)
        chapter_data = state["reader"]["chapterData"]
        title = chapter_data.get("title", "未知标题")
        content_html = chapter_data.get("content", "")

        mapping = self._build_font_mapping(html, font_map)

        markdown = self._html_to_markdown(content_html)
        markdown = self._decrypt(markdown, mapping)
        title = self._decrypt(title, mapping)
        return title, markdown


# ============================================================
#  快手处理器
# ============================================================
class KuaishouHandler(BaseHandler):

    def download(self, url: str, out_dir: str) -> bool:
        url = self._normalize_url(url)
        self.log(f"[快手] 规范化后 URL = {url}")

        ks_dir = self._locate_ks_dir()
        if not ks_dir:
            self.log("[快手] ❌ 未找到 KS-Downloader 目录")
            return False

        self.log(f"[快手] 使用 KS-Downloader: {ks_dir}")
        self._update_work_path(ks_dir, out_dir)
        return self._run(ks_dir, url)

    def _normalize_url(self, url: str) -> str:
        url = url.strip()
        if "/short-video/" in url or "/fw/photo/" in url:
            return url
        if "kuaishou.com/f/" in url or "v.kuaishou.com/" in url:
            try:
                import requests
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                                  "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                                  "Version/16.0 Mobile/15E148 Safari/604.1",
                }
                self.log(f"[快手] 正在解析短链: {url}")
                resp = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
                final_url = resp.url.split("?")[0]
                if "/short-video/" in final_url or "/fw/photo/" in final_url:
                    self.log(f"[快手] 短链已重定向：{url} → {final_url}")
                else:
                    self.log(f"[快手] 重定向后仍非标准格式: {final_url}")
                return final_url
            except Exception as e:
                self.log(f"[快手] ⚠ 短链重定向失败: {e}")
        return url

    def _locate_ks_dir(self):
        base = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            resource_path("KS-Downloader"),
            os.path.join(base, "third_party", "KS-Downloader"),
        ]
        for p in candidates:
            if os.path.exists(os.path.join(p, "main.py")):
                return p
        return None

    def _update_work_path(self, ks_dir, out_dir):
        cfg_path = os.path.join(ks_dir, "Volume", "config.yaml")
        if not os.path.exists(cfg_path):
            self.log(f"[快手] ⚠ 未找到 {cfg_path}")
            return
        try:
            import yaml
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            cfg["work_path"] = out_dir
            with open(cfg_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
            self.log(f"[快手] 输出目录已设为: {out_dir}")
        except Exception as e:
            self.log(f"[快手] ⚠ 更新 config.yaml 失败: {e}")

    def _run(self, ks_dir, url):
        added = False
        if ks_dir not in sys.path:
            sys.path.insert(0, ks_dir)
            added = True
        old_cwd = os.getcwd()
        try:
            os.chdir(ks_dir)
            import asyncio
            cap = _StdoutCapture(self.log, prefix="[快手] ")
            with contextlib.redirect_stdout(cap), contextlib.redirect_stderr(cap):
                ok = asyncio.run(self._async_download(url))
            cap.flush()
            if ok:
                self.log("[快手] ✅ 下载完成")
            return ok
        except Exception as e:
            self.log(f"[快手] ❌ {e}")
            self.log(traceback.format_exc())
            return False
        finally:
            if added:
                try:
                    sys.path.remove(ks_dir)
                except ValueError:
                    pass
            try:
                os.chdir(old_cwd)
            except Exception:
                pass

    async def _async_download(self, url):
        from source.app.app import KS
        try:
            async with KS() as app:
                result = await app.detail_one(url, download=True)
                return isinstance(result, dict)
        except Exception as e:
            import traceback as tb
            print(f"[快手-内部异常] {e}")
            print(tb.format_exc())
            return False


# ============================================================
#  yt-dlp 通用兜底处理器
# ============================================================
class YtdlpHandler(BaseHandler):
    def download(self, url: str, out_dir: str) -> bool:
        try:
            from yt_dlp import YoutubeDL
        except ImportError:
            self.log("[yt-dlp] ❌ 未安装 yt-dlp")
            return False

        ffmpeg_dir = self._ensure_ffmpeg()
        opts = {
            "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self._hook],
            "noprogress": False,
        }
        if ffmpeg_dir:
            opts["ffmpeg_location"] = ffmpeg_dir
        if "bilibili" in url:
            opts["http_headers"] = {
                "Referer": "https://www.bilibili.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            }
        if "kuaishou" in url:
            opts["http_headers"] = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                              "Mobile/15E148 Safari/604.1",
            }
        self.log(f"[yt-dlp] 解析: {url}")
        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.log("[yt-dlp] ✅ 完成")
            return True
        except Exception as e:
            self.log(f"[yt-dlp] ❌ {e}")
            return False

    def _hook(self, d):
        if self._stop:
            raise Exception("用户已停止")
        if d["status"] == "downloading":
            pct = d.get("_percent_str", "").strip()
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes") or 0
            if total:
                self.progress(int(done), int(total), "下载中")
            elif pct:
                self.log(f"[yt-dlp] {pct}")
        elif d["status"] == "finished":
            self.log("[yt-dlp] 下载完成，正在后处理...")

    def _ensure_ffmpeg(self) -> str:
        if shutil.which("ffmpeg"):
            return ""
        cache = user_data_dir() / "bin"
        cache.mkdir(parents=True, exist_ok=True)
        dst = cache / "ffmpeg.exe"
        if not dst.exists():
            src = resource_path("bin/ffmpeg.exe")
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dst)
                    self.log("[系统] ffmpeg 已释放到用户缓存目录")
                except Exception as e:
                    self.log(f"[系统] ffmpeg 释放失败: {e}")
                    return ""
            else:
                return ""
        return str(cache)


# ============================================================
#  调度器
# ============================================================
class Dispatcher:
    ROUTES = [
        (re.compile(r"(bilibili\.com|b23\.tv)"),                            "bili23"),
        (re.compile(r"(v\.douyin\.com|www\.douyin\.com|douyin\.com)"),      "douyin"),
        (re.compile(r"fanqienovel\.com"),                                   "fanqie"),
        (re.compile(r"(kuaishou\.com|v\.kuaishou\.com|m\.gifshow\.com)"),   "kuaishou"),
    ]

    def resolve(self, url: str) -> str:
        for pattern, name in self.ROUTES:
            if pattern.search(url):
                return name
        return "ytdlp"

    def run(self, url, out_dir, log_cb, progress_cb, stop_event):
        name = self.resolve(url)
        log_cb(f"[调度] 识别为「{name}」处理器")

        handlers = {
            "bili23":   Bili23Handler,
            "douyin":   DouyinHandler,
            "fanqie":   FanqieHandler,
            "kuaishou": KuaishouHandler,
            "ytdlp":    YtdlpHandler,
        }
        cls = handlers.get(name, YtdlpHandler)
        h = cls(log_cb, progress_cb)

        def watch_stop():
            stop_event.wait()
            h.stop()

        threading.Thread(target=watch_stop, daemon=True).start()

        return h.download(url, out_dir)


# ============================================================
#  主窗口
# ============================================================
PLATFORMS = {
    "自动识别（推荐）":   "auto",
    "B站":                "bili23",
    "抖音":               "douyin",
    "番茄小说":           "fanqie",
    "快手":               "kuaishou",
    "其他（yt-dlp 兜底）": "ytdlp",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多平台内容下载器v0.1bata")
        self.resize(880, 760)
        self.setMinimumSize(760, 640)
        self.emitter = LogEmitter()
        self.emitter.log.connect(self._append_log)
        self.emitter.progress.connect(self._update_progress)
        self.stop_event = threading.Event()
        self.worker_thread = None
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        # ---------- 顶部标题栏 ----------
        header = QFrame()
        header.setObjectName("Card")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 14, 20, 14)

        title_wrap = QVBoxLayout()
        title_wrap.setSpacing(2)
        title = QLabel("多平台内容下载器v0.1bata")
        title.setObjectName("Title")
        subtitle = QLabel("B 站 · 抖音 · 番茄小说 · 快手 · 其他")
        subtitle.setObjectName("Subtitle")
        title_wrap.addWidget(title)
        title_wrap.addWidget(subtitle)
        header_layout.addLayout(title_wrap)
        header_layout.addStretch(1)

        self.login_btn = QPushButton("登录 B 站")
        self.login_btn.setObjectName("Login")
        self.login_btn.clicked.connect(self._bili_login)
        header_layout.addWidget(self.login_btn)

        root.addWidget(header)

        # ---------- 警示条 ----------
        banner = QLabel(
            "⚠️ 本工具仅供学习与参考，请在 <b>24 小时内主动删除</b> 下载内容，"
            "不得用于商业或侵权用途。"
        )
        banner.setObjectName("Banner")
        banner.setWordWrap(True)
        root.addWidget(banner)

        # ---------- 输入卡片 ----------
        input_card = QFrame()
        input_card.setObjectName("Card")
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(20, 16, 20, 16)
        input_layout.setSpacing(12)

        link_row = QHBoxLayout()
        link_row.setSpacing(10)
        link_label = QLabel("链接")
        link_label.setFixedWidth(56)
        link_label.setStyleSheet("color:#374151; font-weight:600;")
        self.url = QLineEdit()
        self.url.setPlaceholderText("粘贴视频 / 小说链接，程序会自动识别平台...")
        self.url.setMinimumHeight(38)
        link_row.addWidget(link_label)
        link_row.addWidget(self.url, 1)
        input_layout.addLayout(link_row)

        # 保存目录行 + 打开文件夹
        out_row = QHBoxLayout()
        out_row.setSpacing(10)
        out_label = QLabel("保存到")
        out_label.setFixedWidth(56)
        out_label.setStyleSheet("color:#374151; font-weight:600;")
        self.out = QLineEdit(str(Path.home() / "Downloads"))
        self.out.setMinimumHeight(38)
        browse_btn = QPushButton("浏览")
        browse_btn.setMinimumHeight(38)
        browse_btn.setMinimumWidth(72)
        browse_btn.clicked.connect(self._pick)
        open_folder_btn = QPushButton("打开文件夹")
        open_folder_btn.setMinimumHeight(38)
        open_folder_btn.setMinimumWidth(96)
        open_folder_btn.clicked.connect(self._open_folder)
        out_row.addWidget(out_label)
        out_row.addWidget(self.out, 1)
        out_row.addWidget(browse_btn)
        out_row.addWidget(open_folder_btn)
        input_layout.addLayout(out_row)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        plat_label = QLabel("平台")
        plat_label.setFixedWidth(56)
        plat_label.setStyleSheet("color:#374151; font-weight:600;")
        self.combo = QComboBox()
        self.combo.addItems(list(PLATFORMS.keys()))
        self.combo.setMinimumHeight(38)
        action_row.addWidget(plat_label)
        action_row.addWidget(self.combo, 1)

        self.stopb = QPushButton("停止")
        self.stopb.setObjectName("Danger")
        self.stopb.setMinimumHeight(38)
        self.stopb.setMinimumWidth(88)
        self.stopb.setEnabled(False)
        self.stopb.clicked.connect(self._stop)

        self.start = QPushButton("开始下载")
        self.start.setObjectName("Primary")
        self.start.setMinimumHeight(38)
        self.start.setMinimumWidth(120)
        self.start.clicked.connect(self._go)

        action_row.addWidget(self.stopb)
        action_row.addWidget(self.start)
        input_layout.addLayout(action_row)

        self.bar = QProgressBar()
        self.bar.setValue(0)
        self.bar.setTextVisible(True)
        self.bar.setFormat("就绪")
        input_layout.addWidget(self.bar)

        root.addWidget(input_card)

        # ---------- 日志卡片 ----------
        log_card = QFrame()
        log_card.setObjectName("Card")
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(16, 12, 16, 16)
        log_layout.setSpacing(8)

        log_header = QHBoxLayout()
        log_title = QLabel("运行日志")
        log_title.setStyleSheet("font-weight:600; color:#111827; font-size:13px;")
        log_header.addWidget(log_title)
        log_header.addStretch(1)
        clear_btn = QPushButton("清空")
        clear_btn.setMinimumHeight(28)
        clear_btn.setMaximumWidth(72)
        clear_btn.clicked.connect(self._clear_log)
        log_header.addWidget(clear_btn)
        log_layout.addLayout(log_header)

        self.logbox = QTextEdit()
        self.logbox.setObjectName("LogBox")
        self.logbox.setReadOnly(True)
        log_layout.addWidget(self.logbox, 1)

        root.addWidget(log_card, 1)

    # ---------- 事件处理 ----------

    def _clear_log(self):
        self.logbox.clear()

    def _pick(self):
        d = QFileDialog.getExistingDirectory(self, "选择保存目录", self.out.text())
        if d:
            self.out.setText(d)

    def _open_folder(self):
        path = self.out.text().strip()
        if not path:
            QMessageBox.warning(self, "提示", "保存路径为空")
            return
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                QMessageBox.warning(self, "提示", f"目录不存在且无法创建:\n{e}")
                return
        try:
            if sys.platform == "win32":
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "提示", f"无法打开目录:\n{e}")

    def _append_log(self, m):
        self.logbox.append(m)
        sb = self.logbox.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _update_progress(self, cur, total, desc):
        if total > 0:
            self.bar.setMaximum(total)
            self.bar.setValue(cur)
            self.bar.setFormat(f"{desc} {cur * 100 // total}%")
        else:
            self.bar.setFormat(desc)

    def _bili_login(self):
        self.emitter.log.emit("[登录] 打开 B站扫码登录窗口...")
        dlg = LoginDialog(self)
        dlg.login_done.connect(self._on_login_success)
        dlg.exec()

    def _on_login_success(self, credential):
        ok = save_credential(credential)
        if ok:
            self.emitter.log.emit("[登录] ✅ B站登录成功，凭证已保存")
            self.emitter.log.emit(f"[登录] 凭证文件: {CREDENTIAL_FILE}")
            QMessageBox.information(self, "登录成功",
                                    "B站登录成功！\n现在可以下载 1080P 高清视频了。")
        else:
            self.emitter.log.emit("[登录] ⚠ 登录成功但保存凭证失败")
            QMessageBox.warning(self, "提示", "登录成功，但凭证保存失败。")

    def _go(self):
        url = self.url.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "请先粘贴链接")
            return
        out_dir = self.out.text().strip()
        os.makedirs(out_dir, exist_ok=True)

        self.logbox.clear()
        self.bar.setValue(0)
        self.bar.setFormat("准备中...")
        self.stop_event.clear()
        self.emitter.log.emit("===== 开始处理 =====")

        dispatcher = Dispatcher()

        def worker():
            try:
                dispatcher.run(
                    url, out_dir,
                    log_cb=lambda m: self.emitter.log.emit(m),
                    progress_cb=lambda c, t, d: self.emitter.progress.emit(c, t, d),
                    stop_event=self.stop_event,
                )
            except Exception:
                self.emitter.log.emit(traceback.format_exc())
            finally:
                self.emitter.log.emit("===== 任务结束 =====")
                self.start.setEnabled(True)
                self.stopb.setEnabled(False)

        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()
        self.start.setEnabled(False)
        self.stopb.setEnabled(True)

    def _stop(self):
        self.stop_event.set()
        self.emitter.log.emit("[系统] 停止信号已发出")
        self.stopb.setEnabled(False)

    def closeEvent(self, e):
        self.stop_event.set()
        e.accept()


# ============================================================
#  入口
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)

    try:
        from bilibili_api.utils.network import register_client
        for backend in ("httpx", "curl_cffi", "aiohttp"):
            try:
                register_client(backend)
                print(f"[bilibili-api] 已注册后端: {backend}", flush=True)
                break
            except Exception:
                continue
    except Exception as e:
        print(f"[bilibili-api] 注册后端失败: {e}", flush=True)

    flag = user_data_dir() / ".accepted"

    if not flag.exists():
        # 首次运行：强制勾选免责声明
        dlg = DisclaimerDialog()
        if dlg.exec() != QDialog.Accepted:
            sys.exit(0)
        try:
            flag.write_text("accepted", encoding="utf-8")
        except Exception:
            pass
    else:
        # 之后每次启动：轻量提醒
        notice = StartupNoticeDialog()
        if notice.exec() != QDialog.Accepted:
            sys.exit(0)

    try:
        win = MainWindow()
        win.show()
    except Exception:
        tb = traceback.format_exc()
        try:
            (user_data_dir() / "startup_error.log").write_text(tb, encoding="utf-8")
        except Exception:
            pass
        QMessageBox.critical(None, "启动失败", tb)
        sys.exit(1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()