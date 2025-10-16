"""
Dexter Financial Agent - Streamlit Web Interface
財務分析 AI 助理網頁介面
"""

import streamlit as st
import os
from typing import Optional
import sys
sys.path.insert(0, 'src')

from dexter.agent import Agent
from dexter.streamlit_ui import StreamlitUI
import time

# 設定頁面配置
st.set_page_config(
    page_title="Dexter 財務分析助理",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'ui' not in st.session_state:
    st.session_state.ui = None
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""
if 'financial_api_key' not in st.session_state:
    st.session_state.financial_api_key = ""

# 側邊欄 - API 金鑰設定
with st.sidebar:
    st.title("🔐 API 設定")
    st.markdown("請輸入您的 API 金鑰以開始使用")

    # OpenAI API Key
    openai_key = st.text_input(
        "OpenAI API Key",
        value=st.session_state.openai_api_key,
        type="password",
        placeholder="sk-...",
        help="從 https://platform.openai.com/api-keys 取得"
    )

    # Financial Datasets API Key
    financial_key = st.text_input(
        "Financial Datasets API Key",
        value=st.session_state.financial_api_key,
        type="password",
        placeholder="您的 Financial Datasets API 金鑰",
        help="從 https://financialdatasets.ai 取得"
    )

    # 儲存 API 金鑰按鈕
    if st.button("💾 儲存設定", use_container_width=True, type="primary"):
        if openai_key and financial_key:
            st.session_state.openai_api_key = openai_key
            st.session_state.financial_api_key = financial_key

            # 設定環境變數
            os.environ["OPENAI_API_KEY"] = openai_key
            os.environ["FINANCIAL_DATASETS_API_KEY"] = financial_key

            # 初始化 Agent 和 UI
            try:
                st.session_state.agent = Agent(
                    max_steps=20,
                    max_steps_per_task=5,
                    use_chinese=True  # 使用繁體中文
                )
                st.session_state.ui = StreamlitUI()
                st.success("✅ API 金鑰設定成功！可以開始使用了。")
            except Exception as e:
                st.error(f"❌ 初始化失敗: {str(e)}")
        else:
            st.error("請輸入所有必要的 API 金鑰")

    # 分隔線
    st.divider()

    # 範例問題
    st.subheader("📝 範例問題")
    example_questions = [
        "蘋果公司過去四季的營收成長如何？",
        "比較微軟和Google在2023年的營業利潤率",
        "分析特斯拉過去一年的現金流趨勢",
        "亞馬遜最近的負債權益比是多少？",
        "台積電(TSM)的財務狀況如何？"
    ]

    for question in example_questions:
        if st.button(f"💡 {question}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()

    # 分隔線
    st.divider()

    # 清除對話按鈕
    if st.button("🗑️ 清除對話記錄", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # 關於區塊
    st.divider()
    st.subheader("ℹ️ 關於")
    st.markdown("""
    **Dexter 財務分析助理**

    基於 GPT-4 的智能財務分析工具，能夠：
    - 📊 分析上市公司財務報表
    - 📈 比較多家公司財務指標
    - 💰 提供即時市場數據
    - 🎯 自動規劃和執行分析任務

    [GitHub](https://github.com/zinojeng/financial_agent) |
    [原始專案](https://github.com/virattt/dexter)
    """)

# 主要內容區域
st.title("🤖 Dexter 財務分析助理")
st.markdown("智能財務研究代理，協助您分析上市公司財務數據")

# 檢查是否已設定 API 金鑰
if not st.session_state.agent:
    st.info("👈 請先在側邊欄設定您的 API 金鑰")
    st.markdown("""
    ### 快速開始指南：
    1. 在側邊欄輸入您的 **OpenAI API Key**
    2. 輸入您的 **Financial Datasets API Key**
    3. 點擊「儲存設定」按鈕
    4. 開始詢問財務相關問題！

    ### 需要 API 金鑰？
    - 🔗 [取得 OpenAI API Key](https://platform.openai.com/api-keys)
    - 🔗 [取得 Financial Datasets API Key](https://financialdatasets.ai)
    """)
else:
    # 顯示對話歷史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 用戶輸入
    if prompt := st.chat_input("請輸入您的財務分析問題..."):
        # 添加用戶消息到對話歷史
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 顯示用戶消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 顯示助理回應
        with st.chat_message("assistant"):
            # 創建一個容器來顯示進度
            response_container = st.container()

            with response_container:
                # 顯示思考中的狀態
                with st.status("🤔 正在分析您的問題...", expanded=True) as status:
                    try:
                        # 執行 Dexter agent
                        ui = st.session_state.ui
                        ui.reset()  # 重置 UI 狀態

                        # 設定 UI 的狀態顯示區域
                        ui.set_status_container(status)

                        # 執行分析
                        st.session_state.agent.ui = ui
                        answer = st.session_state.agent.run(prompt)

                        # 更新狀態
                        status.update(label="✅ 分析完成！", state="complete", expanded=False)

                        # 顯示最終答案
                        st.markdown(answer)

                        # 添加助理回應到對話歷史
                        st.session_state.messages.append({"role": "assistant", "content": answer})

                    except Exception as e:
                        status.update(label="❌ 發生錯誤", state="error", expanded=True)
                        error_msg = f"抱歉，處理您的請求時發生錯誤：{str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

# 頁尾
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    Powered by OpenAI GPT-4 | Data from Financial Datasets API | Built with Streamlit
</div>
""", unsafe_allow_html=True)