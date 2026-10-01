"""
診斷服務 - 檢查所有工具的健康狀態
使用 Flask 提供 REST API
"""

import json
import os
import sys
import subprocess
import socket
import time
from pathlib import Path
from datetime import datetime

try:
    import psutil
except ImportError:
    psutil = None

try:
    from flask import Flask, jsonify
    from flask_cors import CORS
except ImportError:
    Flask = None


class ToolsDiagnostics:
    def __init__(self):
        self.workspace = Path(__file__).parent
        self.alerts = []
        self.summary = {
            "total_checks": 0,
            "passed": 0,
            "warnings": 0,
            "errors": 0
        }

    def diagnose(self):
        """執行完整診斷"""
        self.alerts = []
        self.summary = {"total_checks": 0, "passed": 0, "warnings": 0, "errors": 0}

        result = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.summary,
            "alerts": self.alerts,
            "tools": self._check_tools(),
            "python": self._check_python(),
            "dependencies": self._check_dependencies(),
            "resources": self._check_resources(),
            "audio_devices": self._check_audio_devices(),
            "services": self._check_services(),
        }

        return result

    def _check_tools(self):
        """檢查各工具狀態"""
        tools = {}

        # 翻譯工具
        translator_py = self.workspace / "desktop_realtime_translator.py"
        tools["桌面即時翻譯"] = {
            "icon": "🗣️",
            "status": "ok" if translator_py.exists() else "error",
            "version": "1.0",
            "message": None if translator_py.exists() else "文件不存在"
        }

        # DevOps面板
        devops_html = self.workspace / "devops_dashboard.html"
        tools["DevOps儀表板"] = {
            "icon": "📊",
            "status": "ok" if devops_html.exists() else "error",
            "version": "1.0",
            "message": None if devops_html.exists() else "文件不存在"
        }

        # Outlook工具
        outlook_html = self.workspace / "outlook-tool.html"
        tools["Outlook工具"] = {
            "icon": "📧",
            "status": "ok" if outlook_html.exists() else "error",
            "version": "1.0",
            "message": None if outlook_html.exists() else "文件不存在"
        }

        # 股票工具
        stocks_html = self.workspace / "taiwan-stocks-top10.html"
        tools["台灣股票"] = {
            "icon": "📈",
            "status": "ok" if stocks_html.exists() else "error",
            "version": "1.0",
            "message": None if stocks_html.exists() else "文件不存在"
        }

        return tools

    def _check_python(self):
        """檢查Python環境"""
        self.summary["total_checks"] += 1

        python_info = {
            "installed": True,
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "executable": sys.executable,
            "pip_version": self._get_pip_version(),
            "venv": hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        }

        if python_info["installed"]:
            self.summary["passed"] += 1

        return python_info

    def _get_pip_version(self):
        """取得pip版本"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # 解析: "pip 24.0 from /path"
                return result.stdout.split()[1]
        except Exception as e:
            pass
        return None

    def _check_dependencies(self):
        """檢查依賴包"""
        required_packages = {
            "whisper": "faster-whisper",
            "soundcard": "soundcard",
            "deep_translator": "deep-translator",
            "numpy": "numpy",
            "tkinter": None,  # 內建
            "flask": "flask",
            "flask_cors": "flask-cors",
        }

        dependencies = []

        for import_name, package_name in required_packages.items():
            self.summary["total_checks"] += 1

            try:
                module = __import__(import_name)
                version = getattr(module, '__version__', 'unknown')
                dependencies.append({
                    "name": package_name or import_name,
                    "status": "ok",
                    "version": version
                })
                self.summary["passed"] += 1
            except ImportError:
                status = "warning"
                message = f"未安裝 (pip install {package_name})" if package_name else "需要重新安裝"

                dependencies.append({
                    "name": package_name or import_name,
                    "status": status,
                    "message": message
                })
                self.summary["warnings"] += 1

                if package_name and package_name not in ["tkinter"]:
                    self.alerts.append({
                        "level": "warning",
                        "title": f"缺少依賴: {package_name}",
                        "message": f"請執行: pip install {package_name}"
                    })

        return dependencies

    def _check_resources(self):
        """檢查系統資源"""
        resources = {
            "cpu": 0,
            "memory": 0,
            "memory_detail": "0GB/0GB",
            "disk": 0,
            "disk_detail": "0GB/0GB"
        }

        if psutil:
            self.summary["total_checks"] += 3

            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            resources["cpu"] = int(cpu_percent)
            self.summary["passed"] += 1

            # Memory
            mem = psutil.virtual_memory()
            resources["memory"] = int(mem.percent)
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
            resources["memory_detail"] = f"{used_gb:.1f}GB/{total_gb:.1f}GB"

            if mem.percent > 85:
                self.summary["errors"] += 1
                self.alerts.append({
                    "level": "error",
                    "title": "記憶體緊張",
                    "message": f"記憶體使用率: {mem.percent}%，建議清理或升級"
                })
            else:
                self.summary["passed"] += 1

            # Disk
            disk = psutil.disk_usage('/')
            resources["disk"] = int(disk.percent)
            used_gb = disk.used / (1024 ** 3)
            total_gb = disk.total / (1024 ** 3)
            resources["disk_detail"] = f"{used_gb:.1f}GB/{total_gb:.1f}GB"

            if disk.percent > 90:
                self.summary["errors"] += 1
                self.alerts.append({
                    "level": "error",
                    "title": "磁碟空間不足",
                    "message": f"磁碟使用率: {disk.percent}%，建議清理磁碟"
                })
            else:
                self.summary["passed"] += 1
        else:
            # psutil not installed
            resources = {
                "cpu": -1,
                "memory": -1,
                "memory_detail": "psutil未安裝",
                "disk": -1,
                "disk_detail": "psutil未安裝"
            }
            self.alerts.append({
                "level": "info",
                "title": "無法取得資源信息",
                "message": "請安裝: pip install psutil"
            })

        return resources

    def _check_audio_devices(self):
        """檢查音訊設備"""
        devices = []
        self.summary["total_checks"] += 1

        try:
            import soundcard as sc
            mics = sc.all_microphones()

            loopback_found = False
            for mic in mics:
                device_info = {
                    "name": mic.name,
                    "type": "Loopback" if "Loopback" in mic.name or "Stereo Mix" in mic.name else "Standard"
                }
                devices.append(device_info)

                if "Loopback" in mic.name or "Stereo Mix" in mic.name:
                    loopback_found = True

            if devices:
                self.summary["passed"] += 1

            if not loopback_found:
                self.alerts.append({
                    "level": "warning",
                    "title": "未檢測到Loopback設備",
                    "message": "翻譯工具需要Loopback設備。建議安裝VB-CABLE或使用Stereo Mix"
                })

        except ImportError:
            self.summary["warnings"] += 1
            self.alerts.append({
                "level": "warning",
                "title": "無法檢查音訊設備",
                "message": "soundcard模組未安裝。請執行: pip install soundcard"
            })
        except Exception as e:
            self.summary["errors"] += 1
            self.alerts.append({
                "level": "error",
                "title": "音訊設備檢查失敗",
                "message": str(e)
            })

        return devices

    def _check_services(self):
        """檢查外部服務連接"""
        services = []
        self.summary["total_checks"] += 4

        # Google Translate API
        google_status, google_latency = self._check_connectivity("translate.googleapis.com", 443)
        services.append({
            "name": "Google翻譯API",
            "status": google_status,
            "latency": f"{google_latency}ms" if google_latency else "無法連接"
        })
        if google_status == "ok":
            self.summary["passed"] += 1
        else:
            self.summary["warnings"] += 1

        # Outlook API
        outlook_status, outlook_latency = self._check_connectivity("graph.microsoft.com", 443)
        services.append({
            "name": "Microsoft Graph API",
            "status": outlook_status,
            "latency": f"{outlook_latency}ms" if outlook_latency else "無法連接"
        })
        if outlook_status == "ok":
            self.summary["passed"] += 1
        else:
            self.summary["warnings"] += 1

        # Network connectivity
        internet_status, internet_latency = self._check_connectivity("8.8.8.8", 53)
        services.append({
            "name": "網路連接",
            "status": internet_status,
            "latency": f"{internet_latency}ms" if internet_latency else "無法連接"
        })
        if internet_status == "ok":
            self.summary["passed"] += 1
        else:
            self.summary["errors"] += 1
            self.alerts.append({
                "level": "error",
                "title": "網路連接失敗",
                "message": "無法連接互聯網，翻譯和郵件功能將不可用"
            })

        # Local API service
        local_status = self._check_local_service("http://localhost:5555/health")
        services.append({
            "name": "本地診斷服務",
            "status": local_status,
            "latency": "運行中" if local_status == "ok" else "未運行"
        })
        if local_status == "ok":
            self.summary["passed"] += 1
        else:
            self.summary["warnings"] += 1

        return services

    def _check_connectivity(self, host, port, timeout=3):
        """檢查主機連接"""
        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            elapsed = int((time.time() - start_time) * 1000)
            if result == 0:
                return "ok", elapsed
            else:
                return "error", None
        except socket.gaierror:
            return "error", None
        except Exception:
            return "error", None

    def _check_local_service(self, url):
        """檢查本地服務"""
        try:
            import urllib.request
            response = urllib.request.urlopen(url, timeout=2)
            return "ok" if response.status == 200 else "error"
        except Exception:
            return "error"


def create_app():
    """建立Flask應用"""
    if Flask is None:
        raise RuntimeError("Flask未安裝。請執行: pip install flask flask-cors")

    app = Flask(__name__)
    CORS(app)

    diagnostics = ToolsDiagnostics()

    @app.route('/api/diagnose', methods=['GET'])
    def diagnose():
        """執行診斷"""
        result = diagnostics.diagnose()
        return jsonify(result)

    @app.route('/health', methods=['GET'])
    def health():
        """健康檢查"""
        return jsonify({"status": "ok"}), 200

    return app


if __name__ == '__main__':
    try:
        app = create_app()
        print("🔍 診斷服務正在啟動...")
        print("📍 訪問: http://localhost:5555/diagnosis_dashboard.html")
        print("🔗 API: http://localhost:5555/api/diagnose")
        print("\n按 Ctrl+C 停止服務\n")
        app.run(host='0.0.0.0', port=5555, debug=False)
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        print("\n請確保已安裝必要的套件:")
        print("pip install flask flask-cors psutil soundcard")
        sys.exit(1)
