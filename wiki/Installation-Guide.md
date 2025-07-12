# 安裝指南

本指南將幫助您在您的系統上安裝 async-mc-launcher-core。

## 📋 系統要求

### Python 版本要求
- **Python 3.10 或以上版本**
- 支援 CPython 和 PyPy 實作

### 作業系統支援
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, CentOS 8+, 其他主流發行版)

### 硬體要求
- RAM: 至少 512MB 可用記憶體
- 磁碟空間: 至少 100MB 用於函式庫和依賴項

## 🔧 安裝方式

### 方式一：使用 pip（標準安裝）

```bash
pip install async-mc-launcher-core
```

### 方式二：使用 uv（推薦，速度更快）

首先安裝 uv：
```bash
pip install uv
```

然後安裝 async-mc-launcher-core：
```bash
uv pip install async-mc-launcher-core
```

### 方式三：從原始碼安裝（開發者）

1. 複製儲存庫：
```bash
git clone https://github.com/JaydenChao101/async-mc-launcher-core.git
cd async-mc-launcher-core
```

2. 安裝開發依賴：
```bash
pip install -e .
```

或使用 uv：
```bash
uv pip install -e .
```

## 📦 依賴項

async-mc-launcher-core 會自動安裝以下依賴項：

### 核心依賴
- **aiohttp** (≥3.11.18) - 異步 HTTP 客戶端
- **aiofiles** (≥24.1.0) - 異步文件操作
- **cryptography** (≥45.0.2) - 加密功能
- **PyJWT** (≥2.10.1) - JWT token 處理
- **tomli-w** (≥1.2.0) - TOML 文件寫入

### 開發依賴（可選）
- **pytest** (≥8.4.1) - 測試框架
- **requests-mock** (≥1.12.1) - HTTP 請求模擬

## ✅ 驗證安裝

### 基本驗證
在 Python 控制台中執行以下代碼來驗證安裝：

```python
import launcher_core
print(f"async-mc-launcher-core 版本: {launcher_core.__version__}")
print("安裝成功！")
```

### 功能驗證
運行以下完整測試來確保所有功能正常：

```python
import asyncio
from launcher_core import microsoft_account, utils
from launcher_core.setting import setup_logger

async def test_installation():
    """測試基本功能是否正常"""
    try:
        # 測試日誌系統
        logger = setup_logger(enable_console=True)
        logger.info("日誌系統測試成功")
        
        # 測試 Microsoft 認證模組
        azure_app = microsoft_account.AzureApplication()
        print(f"Azure 應用程式 ID: {azure_app.client_id}")
        
        # 測試工具模組
        minecraft_dir = utils.get_minecraft_directory()
        print(f"Minecraft 目錄: {minecraft_dir}")
        
        print("✅ 所有功能測試通過！")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_installation())
    if success:
        print("🎉 async-mc-launcher-core 安裝完成並通過驗證！")
    else:
        print("⚠️  安裝可能有問題，請檢查錯誤訊息")
```

## 🚨 常見安裝問題

### 問題 1: Python 版本不相容
**錯誤訊息**: `python_requires`
**解決方案**: 升級到 Python 3.10 或以上版本

### 問題 2: 網路連接問題
**錯誤訊息**: `Could not fetch URL`
**解決方案**: 
- 檢查網路連接
- 使用國內鏡像源：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple async-mc-launcher-core
```

### 問題 3: 權限錯誤
**錯誤訊息**: `Permission denied`
**解決方案**: 
- Windows: 以管理員身份運行命令提示字元
- macOS/Linux: 使用 `sudo` 或虛擬環境

### 問題 4: 依賴衝突
**錯誤訊息**: `Dependency conflict`
**解決方案**: 
1. 建立新的虛擬環境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

2. 在乾淨環境中重新安裝：
```bash
pip install async-mc-launcher-core
```

## 🔄 升級指南

### 升級到最新版本
```bash
pip install --upgrade async-mc-launcher-core
```

### 檢查版本
```python
import launcher_core
print(launcher_core.__version__)
```

## 🐍 虛擬環境建議

為了避免依賴衝突，建議使用虛擬環境：

### 使用 venv
```bash
python -m venv minecraft-launcher-env
source minecraft-launcher-env/bin/activate  # Linux/macOS
minecraft-launcher-env\Scripts\activate     # Windows
pip install async-mc-launcher-core
```

### 使用 conda
```bash
conda create -n minecraft-launcher python=3.11
conda activate minecraft-launcher
pip install async-mc-launcher-core
```

## 🎯 下一步

安裝完成後，您可以：

1. 閱讀 [快速開始指南](Quick-Start.md) 學習基本用法
2. 查看 [範例代碼](https://github.com/JaydenChao101/async-mc-launcher-core/tree/main/examples)
3. 探索 [API 參考](API-Reference.md) 了解詳細功能

---

**提示**: 如果遇到任何安裝問題，請查看 [故障排除指南](Troubleshooting.md) 或在 [GitHub Issues](https://github.com/JaydenChao101/async-mc-launcher-core/issues) 提出問題。