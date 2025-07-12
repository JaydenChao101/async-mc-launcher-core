# async-mc-launcher-core 開發者 Wiki

## 歡迎來到 async-mc-launcher-core 📚

這是一個現代化的異步 Python 函式庫，專為構建 Minecraft 啟動器而設計。本 Wiki 提供完整的開發者文檔，幫助您快速上手並充分利用這個強大的工具。

## 🚀 主要特色

- **全異步支持**：基於 asyncio 的現代異步程式設計
- **Microsoft 認證**：完整的 Microsoft 帳號登入流程
- **模組載入器支持**：支援 Forge、Fabric、Quilt 等主流模組載入器
- **模組包管理**：支援 mrpack 格式的模組包
- **類型註解**：完整的類型註解，提供更好的開發體驗
- **內建日誌系統**：靈活的日誌配置和管理
- **配置管理**：基於 TOML 的配置文件支持

## 📖 文檔導航

### 🛠️ 基礎設置
- [**安裝指南**](Installation-Guide.md) - 安裝要求、不同安裝方式和驗證
- [**快速開始**](Quick-Start.md) - 基本使用示例和 Microsoft 登入流程

### 📚 深入了解
- [**API 參考**](API-Reference.md) - 所有主要模組的詳細說明
- [**高級示例**](Advanced-Examples.md) - 複雜使用場景和最佳實踐
- [**Microsoft 認證**](Microsoft-Authentication.md) - 詳細的登入流程和認證管理

### 🔧 專業功能
- [**模組支持**](Modding-Support.md) - Forge、Fabric、Quilt 的安裝和使用
- [**配置管理**](Configuration.md) - TOML 配置文件和啟動器設定

### 🆘 支援與疑難排解
- [**故障排除**](Troubleshooting.md) - 常見錯誤及解決方案
- [**遷移指南**](Migration-Guide.md) - 從原版 minecraft-launcher-lib 遷移

## 🎯 快速入門

如果您是第一次使用 async-mc-launcher-core，建議按以下順序閱讀：

1. **[安裝指南](Installation-Guide.md)** - 設置您的開發環境
2. **[快速開始](Quick-Start.md)** - 運行您的第一個示例
3. **[Microsoft 認證](Microsoft-Authentication.md)** - 了解認證流程
4. **[API 參考](API-Reference.md)** - 深入了解可用功能

## 💡 實用連結

- [GitHub 儲存庫](https://github.com/JaydenChao101/async-mc-launcher-core)
- [問題回報](https://github.com/JaydenChao101/async-mc-launcher-core/issues)
- [範例代碼](https://github.com/JaydenChao101/async-mc-launcher-core/tree/main/examples)

## 🤝 參與貢獻

歡迎參與專案貢獻！請查看 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解如何參與開發。

## 📝 版本資訊

- **當前版本**：0.3
- **Python 要求**：3.10+
- **主要依賴**：aiohttp, aiofiles, cryptography

---

**注意**：本專案為 [JakobDev/minecraft-launcher-lib](https://codeberg.org/JakobDev/minecraft-launcher-lib) 的分支版本，專注於異步編程和現代 Python 特性。