import ctypes
import winreg


def _set_win_proxy(enable: bool, host_port: str = "127.0.0.1:8080"):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(key, "ProxyServer",   0, winreg.REG_SZ,    host_port)
            winreg.SetValueEx(key, "ProxyEnable",   0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ,    "<local>")
        else:
            winreg.SetValueEx(key, "ProxyEnable",   0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        ctypes.windll.wininet.InternetSetOptionW(0, 37, 0, 0)
        ctypes.windll.wininet.InternetSetOptionW(0, 39, 0, 0)
    except Exception:
        pass
