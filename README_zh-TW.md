# Dexter 財務分析助理 🤖

Dexter 是一個自主的財務研究代理，具備思考、規劃和學習能力。它使用任務規劃、自我反思和即時市場數據進行分析。可以把它想像成專為財務研究而建立的 Claude Code。

## 功能特色

- 🤖 **智能任務規劃**：自動將複雜查詢分解為結構化的研究步驟
- 🚀 **自主執行**：選擇並執行正確的工具來收集財務數據
- ✅ **自我驗證**：檢查自己的工作並迭代直到任務完成
- 📊 **即時財務數據**：訪問損益表、資產負債表和現金流量表
- 🛡️ **安全功能**：內建循環檢測和步驟限制以防止失控執行
- 🌐 **繁體中文介面**：完整的繁體中文使用者介面和回應
- 💻 **網頁介面**：使用 Streamlit 建立的友善使用者介面

## 快速開始

### 環境需求

- Python 3.10 或更高版本
- OpenAI API 金鑰
- Financial Datasets API 金鑰（在 [financialdatasets.ai](https://financialdatasets.ai) 取得）

### 本地安裝

1. 複製儲存庫：
```bash
git clone https://github.com/zinojeng/financial_agent.git
cd financial_agent
```

2. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

3. 執行應用程式：
```bash
streamlit run app.py
```

4. 在瀏覽器中開啟 `http://localhost:8501`

5. 在側邊欄輸入您的 API 金鑰並開始使用！

## 部署至 Zeabur

### 方法一：使用 GitHub 整合

1. Fork 這個儲存庫到您的 GitHub 帳號

2. 登入 [Zeabur](https://zeabur.com)

3. 創建新專案並選擇「從 GitHub 部署」

4. 選擇您 fork 的儲存庫

5. 在環境變數中設定（選擇性，使用者也可在介面中輸入）：
   - `OPENAI_API_KEY`：您的 OpenAI API 金鑰
   - `FINANCIAL_DATASETS_API_KEY`：您的 Financial Datasets API 金鑰

6. Zeabur 會自動識別為 Streamlit 應用並部署

### 方法二：使用 Zeabur CLI

```bash
# 安裝 Zeabur CLI
npm install -g @zeabur/cli

# 登入 Zeabur
zeabur auth login

# 在專案目錄中初始化
zeabur init

# 部署應用
zeabur deploy
```

## 使用方式

### 網頁介面

1. **設定 API 金鑰**：
   - 在側邊欄輸入 OpenAI API Key
   - 輸入 Financial Datasets API Key
   - 點擊「儲存設定」

2. **詢問問題**：
   - 在聊天框輸入您的財務分析問題
   - 系統會自動規劃任務並執行

3. **範例問題**：
   - 「蘋果公司過去四季的營收成長如何？」
   - 「比較微軟和Google在2023年的營業利潤率」
   - 「分析特斯拉過去一年的現金流趨勢」
   - 「台積電(TSM)的財務狀況如何？」

### CLI 介面（原版）

如果您想使用命令列介面：

```bash
# 安裝額外依賴
pip install prompt-toolkit

# 設定環境變數
export OPENAI_API_KEY=your-key
export FINANCIAL_DATASETS_API_KEY=your-key

# 執行 CLI 版本
python -m dexter.cli
```

## 專案結構

```
dexter/
├── app.py                    # Streamlit 網頁應用主程式
├── requirements.txt          # Python 依賴套件
├── zbpack.json              # Zeabur 部署配置
├── Procfile                 # 替代部署選項
├── .streamlit/
│   └── config.toml          # Streamlit 設定
├── src/
│   └── dexter/
│       ├── agent.py         # 主要代理協調邏輯
│       ├── model.py         # LLM 介面
│       ├── tools.py         # 財務數據工具
│       ├── prompts.py       # 英文系統提示
│       ├── prompts_zh_tw.py # 繁體中文系統提示
│       ├── streamlit_ui.py  # Streamlit UI 適配器
│       ├── schemas.py       # Pydantic 模型
│       └── cli.py           # CLI 入口點
└── README_zh-TW.md          # 繁體中文說明文件
```

## 配置選項

### Agent 配置

```python
from dexter.agent import Agent

agent = Agent(
    max_steps=20,              # 全域安全限制
    max_steps_per_task=5,      # 每個任務的迭代限制
    use_chinese=True           # 使用繁體中文
)
```

### 環境變數

可以在 `.env` 檔案或部署平台設定：

```bash
OPENAI_API_KEY=your-openai-api-key
FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key
```

## 技術架構

### 多代理架構

Dexter 使用專門的組件：

- **規劃代理**：分析查詢並創建結構化任務列表
- **行動代理**：選擇適當的工具並執行研究步驟
- **驗證代理**：驗證任務完成和數據充足性
- **回答代理**：將發現綜合成全面的回應

### 可用工具

- `get_income_statements`：獲取收入、支出和淨利潤數據
- `get_balance_sheets`：獲取資產、負債和股東權益
- `get_cash_flow_statements`：獲取現金流數據

### 安全功能

- 全域步驟限制（預設 20 步）
- 每個任務步驟限制（預設 5 步）
- 循環檢測機制
- 自動任務完成標記

## 貢獻指南

1. Fork 儲存庫
2. 創建功能分支
3. 提交您的更改
4. 推送到分支
5. 創建 Pull Request

**重要**：請保持您的 Pull Request 小而專注，這將使審查和合併更容易。

## 授權

本專案採用 MIT 授權。

## 致謝

- 原始專案：[virattt/dexter](https://github.com/virattt/dexter)
- 基於 OpenAI GPT-4 和 LangChain
- 財務數據來自 [Financial Datasets](https://financialdatasets.ai)
- 使用 [Streamlit](https://streamlit.io) 建立介面

## 支援

如有問題或建議，請在 [GitHub Issues](https://github.com/zinojeng/financial_agent/issues) 提出。