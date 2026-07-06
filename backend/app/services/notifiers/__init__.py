"""Notification service - unified interface for all notification channels.

Supports cross-platform desktop notifications (Windows/macOS/Linux),
Feishu (Lark), and DingTalk.
"""
import os
import sys
import shutil
import subprocess
from typing import Tuple


def send_notification(channel: str, title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """
    Send notification through the specified channel.

    Args:
        channel: desktop, feishu, dingtalk, or windows (alias for desktop)
        title: Notification title
        body: Notification body
        **kwargs: Channel-specific options

    Returns:
        (success: bool, message: str)
    """
    if channel in ("desktop", "windows"):
        return _send_desktop(title, body, **kwargs)
    elif channel == "feishu":
        return _send_feishu(title, body, **kwargs)
    elif channel == "dingtalk":
        return _send_dingtalk(title, body, **kwargs)
    else:
        return False, f"Unknown channel: {channel}"


def _send_feishu(title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """Send notification via Feishu (Lark) using lark-cli."""
    import json

    try:
        # Support configurable lark-cli path via env var
        lark_cli = os.environ.get("LARK_CLI_PATH", _find_lark_cli())
        if not lark_cli or not os.path.isfile(lark_cli):
            return False, "Feishu error: lark-cli not found. Set LARK_CLI_PATH env var."

        cmd = [
            lark_cli,
            "im", "message", "create",
            "--receive_id_type", "open_id",
            "--receive_id", kwargs.get("user_id", "me"),
            "--msg_type", "text",
            "--content", json.dumps({"text": f"[LearnFlow] {title}\n\n{body}"}),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=10)
        if r.returncode == 0:
            return True, "Feishu notification sent"
        return False, f"Feishu error: {r.stderr[:200]}"
    except Exception as e:
        return False, f"Feishu error: {str(e)[:200]}"


def _find_lark_cli() -> str:
    """Find lark-cli binary across platforms."""
    # Check PATH first
    found = shutil.which("lark-cli")
    if found:
        return found

    # Check common locations per platform
    home = os.path.expanduser("~")
    candidates = []
    if sys.platform == "win32":
        candidates = [
            os.path.join(home, ".qoderworkcn", "bin", "lark-cli.cmd"),
            os.path.join(home, ".qoderworkcn", "bin", "lark-cli.exe"),
        ]
    else:
        candidates = [
            os.path.join(home, ".qoderworkcn", "bin", "lark-cli"),
            "/usr/local/bin/lark-cli",
        ]

    for path in candidates:
        if os.path.isfile(path):
            return path
    return ""


def _send_dingtalk(title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """Send notification via DingTalk using dws."""
    try:
        dws_cmd = os.environ.get("DWS_CLI_PATH", shutil.which("dws") or "dws")
        cmd = [
            dws_cmd, "message", "send",
            "--title", title,
            "--content", body,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=10)
        if r.returncode == 0:
            return True, "DingTalk notification sent"
        return False, f"DingTalk error: {r.stderr[:200]}"
    except Exception as e:
        return False, f"DingTalk error: {str(e)[:200]}"


def _send_desktop(title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """Send desktop notification using platform-native APIs.

    Supports:
    - Windows: win11toast library or PowerShell fallback
    - macOS: osascript (built-in) or terminal-notifier (brew)
    - Linux: notify-send (libnotify)
    """
    platform = sys.platform

    if platform == "win32":
        return _send_windows(title, body, **kwargs)
    elif platform == "darwin":
        return _send_macos(title, body, **kwargs)
    else:
        return _send_linux(title, body, **kwargs)


def _send_windows(title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """Send Windows toast notification."""
    try:
        from win11toast import toast
        toast(title, body)
        return True, "Windows notification sent"
    except Exception:
        pass

    # Fallback to PowerShell notification
    try:
        ps_cmd = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $textNodes = $template.GetElementsByTagName("text")
        $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) > $null
        $textNodes.Item(1).AppendChild($template.CreateTextNode("{body}")) > $null
        $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("LearnFlow").Show($toast)
        '''
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=10)
        return True, "Windows notification sent (PowerShell fallback)"
    except Exception as e:
        return False, f"Windows notification error: {str(e)[:200]}"


def _send_macos(title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """Send macOS notification using osascript or terminal-notifier."""
    # Try terminal-notifier first (richer notifications)
    notifier = shutil.which("terminal-notifier")
    if notifier:
        try:
            cmd = [notifier, "-title", title, "-message", body, "-group", "LearnFlow"]
            r = subprocess.run(cmd, capture_output=True, timeout=10)
            if r.returncode == 0:
                return True, "macOS notification sent (terminal-notifier)"
        except Exception:
            pass

    # Fallback to osascript (always available on macOS)
    try:
        escaped_title = title.replace('"', '\\"')
        escaped_body = body.replace('"', '\\"')
        script = (
            f'display notification "{escaped_body}" '
            f'with title "{escaped_title}" '
            f'subtitle "LearnFlow"'
        )
        r = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, timeout=10
        )
        if r.returncode == 0:
            return True, "macOS notification sent (osascript)"
        return False, f"macOS notification error: {r.stderr.decode()[:200]}"
    except Exception as e:
        return False, f"macOS notification error: {str(e)[:200]}"


def _send_linux(title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """Send Linux desktop notification using notify-send."""
    notify_send = shutil.which("notify-send")
    if notify_send:
        try:
            cmd = [notify_send, "--app-name=LearnFlow", title, body]
            r = subprocess.run(cmd, capture_output=True, timeout=10)
            if r.returncode == 0:
                return True, "Linux notification sent (notify-send)"
            return False, f"Linux notification error: {r.stderr.decode()[:200]}"
        except Exception as e:
            return False, f"Linux notification error: {str(e)[:200]}"

    # Fallback: try zenity as a dialog
    zenity = shutil.which("zenity")
    if zenity:
        try:
            cmd = [zenity, "--notification", f"--text={title}\n{body}"]
            subprocess.run(cmd, capture_output=True, timeout=10)
            return True, "Linux notification sent (zenity)"
        except Exception:
            pass

    return False, "No notification daemon found. Install libnotify (notify-send) or terminal-notifier."

