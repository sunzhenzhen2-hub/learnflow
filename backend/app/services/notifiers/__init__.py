"""Notification service - unified interface for all notification channels."""
from typing import Tuple


def send_notification(channel: str, title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """
    Send notification through the specified channel.

    Args:
        channel: feishu, dingtalk, or windows
        title: Notification title
        body: Notification body
        **kwargs: Channel-specific options

    Returns:
        (success: bool, message: str)
    """
    if channel == "feishu":
        return _send_feishu(title, body, **kwargs)
    elif channel == "dingtalk":
        return _send_dingtalk(title, body, **kwargs)
    elif channel == "windows":
        return _send_windows(title, body, **kwargs)
    else:
        return False, f"Unknown channel: {channel}"


def _send_feishu(title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """Send notification via Feishu (Lark) using lark-cli."""
    import subprocess, json

    try:
        # Use lark-cli to send a message to self
        cmd = [
            r"C:\Users\Administrator\.qoderworkcn\bin\lark-cli.cmd",
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


def _send_dingtalk(title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """Send notification via DingTalk using dws."""
    import subprocess

    try:
        # Use dws to send a message
        cmd = [
            "dws", "message", "send",
            "--title", title,
            "--content", body,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=10)
        if r.returncode == 0:
            return True, "DingTalk notification sent"
        return False, f"DingTalk error: {r.stderr[:200]}"
    except Exception as e:
        return False, f"DingTalk error: {str(e)[:200]}"


def _send_windows(title: str, body: str, **kwargs) -> Tuple[bool, str]:
    """Send desktop notification (Windows/Linux)."""
    try:
        from win11toast import toast
        toast(title, body, icon="LearnFlow")
        return True, "Windows notification sent"
    except ImportError:
        try:
            import subprocess
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
        except Exception:
            try:
                subprocess.run(["notify-send", title, body, "--app-name", "LearnFlow"], capture_output=True, timeout=10)
                return True, "Linux notification sent (notify-send)"
            except Exception as e:
                return False, f"Notification error: {str(e)[:200]}"
    except Exception as e:
        return False, f"Windows notification error: {str(e)[:200]}"
