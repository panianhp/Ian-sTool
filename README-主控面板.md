# Ian's Tool 主控面板

## 概述
统一的主控面板，可以快速访问所有工具和诊断功能。

## 功能特性

### 🏠 主頁
- 所有工具的快速访问卡片
- 系统状态概览
- 快速链接

### 🔍 系統診斷
- 完整的系统健康检查
- 实时资源监控
- 问题告警和修复建议
- 所有工具状态概览

### 🗣️ 桌面即時翻譯
- 快速访问翻译工具（Python应用）

### 📊 DevOps儀表板
- 集成DevOps仪表板到主面板

### 📧 Outlook工具
- 集成Outlook邮件和日历工具

### 📈 台灣股票
- 集成台湾股市行情

### 📚 教材生成器
- 集成教材生成工具

## 快速開始

### 方法1：使用批处理文件（推荐）
```bash
# 双击运行
啟動-主控面板.bat
```

该脚本会：
1. 检查Python环境
2. 激活虚拟环境
3. 安装必要依赖
4. 启动诊断服务
5. 自动打开主控面板

### 方法2：手动启动

#### 1. 启动诊断服务
```powershell
cd c:\Users\panian\Ian-sTool
python diagnosis_service.py
```

#### 2. 打开浏览器访问
```
http://localhost:5555/index.html
```

## 页面布局

### 左侧导航栏
- 主页
- 系统诊断
- 工具列表（翻译、DevOps、Outlook、股票、教材）
- 其他工具

### 右上角
- 系统状态指示灯
- 刷新按钮

### 主内容区
- 动态显示选定工具的内容
- 支持iFrame嵌入各工具

## 使用提示

### 📌 快速访问
1. 点击左侧导航菜单快速切换工具
2. 或在主页点击工具卡片进入

### 🔄 系统诊断
1. 点击"系統診斷"查看系统状态
2. 自动显示问题告警
3. 点击"執行完整診斷"重新检查

### ⚙️ 工具使用
1. 大多数工具已集成到主面板（嵌入iframe）
2. 翻译工具为Python应用，需要在命令行启动
3. 所有工具都可以在新窗口中单独打开

## 系統要求

- Python 3.10 或更高版本
- 现代浏览器（Chrome、Firefox、Edge等）
- 网络连接（用于API服务）

## 依賴套件

```
flask
flask-cors
psutil
soundcard（用于翻译工具）
faster-whisper（用于翻译工具）
deep-translator（用于翻译工具）
```

## 故障排除

### 主页无法加载
1. 确保诊断服务已启动
2. 检查浏览器是否可以访问 `http://localhost:5555`
3. 检查防火墙设置

### 诊断面板无法连接
1. 确保 `diagnosis_service.py` 正在运行
2. 查看终端中的错误消息
3. 尝试重启服务

### iframe工具无法加载
1. 确保HTML文件在正确的位置
2. 检查浏览器控制台（F12）中的错误
3. 尝试在新窗口中打开工具

### 5555端口被占用
```powershell
# 查找占用端口的进程
netstat -ano | findstr :5555

# 终止进程
Stop-Process -Id <PID> -Force
```

## 文件結構

```
c:\Users\panian\Ian-sTool\
├── index.html                      # 主控面板（新增）
├── diagnosis_dashboard.html        # 诊断面板
├── diagnosis_service.py            # 诊断服务
├── devops_dashboard.html          # DevOps工具
├── outlook-tool.html              # Outlook工具
├── taiwan-stocks-top10.html       # 股票工具
├── 教材生成器主控台.html          # 教材生成器
├── desktop_realtime_translator.py # 翻译工具
├── 啟動-主控面板.bat              # 主控面板启动脚本（新增）
├── 啟動-診斷面板.bat              # 诊断面板启动脚本
└── README-主控面板.md             # 本文件
```

## 快速命令參考

| 任务 | 命令 |
|------|------|
| 启动主控面板 | 双击 `啟動-主控面板.bat` |
| 启动诊断面板 | 双击 `啟動-診斷面板.bat` |
| 启动翻译工具 | `python desktop_realtime_translator.py` |
| 启动诊断服务 | `python diagnosis_service.py` |
| 打开主控面板网址 | `http://localhost:5555/index.html` |

## 下一步建议

1. **自动化启动** - 将批处理文件添加到Windows任务计划器
2. **快捷方式** - 为常用工具创建桌面快捷方式
3. **系统托盘** - 开发系统托盘应用快速启动各工具
4. **数据库** - 使用SQLite存储工具历史和配置

## 许可证
MIT License

## 版本历史

### v1.0 (2026-09-09)
- 初始版本
- 集成所有工具的主控面板
- 系统诊断功能
