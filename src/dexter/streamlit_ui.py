"""
Streamlit UI adapter for Dexter agent
將 Dexter 的終端 UI 轉換為 Streamlit 元件
"""

import streamlit as st
from typing import List, Optional, Any
from dexter.schemas import Task
import time


class StreamlitUI:
    """Streamlit UI implementation for Dexter agent"""

    def __init__(self):
        self.status_container = None
        self.current_tasks = []
        self.current_step = 0
        self.max_steps = 20
        self.task_progress = {}

    def set_status_container(self, container):
        """設定狀態顯示容器"""
        self.status_container = container

    def reset(self):
        """重置 UI 狀態"""
        self.current_tasks = []
        self.current_step = 0
        self.task_progress = {}

    def show_tasks(self, tasks: List[Task]):
        """顯示任務列表"""
        self.current_tasks = tasks

        if self.status_container:
            # 在狀態容器中顯示任務
            self.status_container.write("📋 **任務規劃：**")
            for task in tasks:
                status_icon = "✅" if task.done else "⏳"
                self.status_container.write(f"{status_icon} {task.description}")
                self.task_progress[task.id] = task.done

    def show_step_progress(self, step: int, max_steps: int):
        """顯示步驟進度"""
        self.current_step = step
        self.max_steps = max_steps

        if self.status_container:
            progress = step / max_steps if max_steps > 0 else 0
            self.status_container.progress(progress, text=f"步驟 {step}/{max_steps}")

    def show_tool_execution(self, tool_name: str, tool_input: dict):
        """顯示工具執行"""
        if self.status_container:
            # 顯示正在執行的工具
            tool_display_names = {
                "get_income_statements": "📊 取得損益表",
                "get_balance_sheets": "📈 取得資產負債表",
                "get_cash_flow_statements": "💰 取得現金流量表"
            }

            display_name = tool_display_names.get(tool_name, f"🔧 {tool_name}")

            # 顯示工具執行訊息
            ticker = tool_input.get('ticker', '')
            period = tool_input.get('period', '')

            if ticker:
                self.status_container.write(f"{display_name}")
                self.status_container.write(f"  • 股票代碼: **{ticker}**")
                if period:
                    period_names = {
                        'quarterly': '季度',
                        'annual': '年度',
                        'ttm': '近四季'
                    }
                    period_display = period_names.get(period, period)
                    self.status_container.write(f"  • 期間: {period_display}")

            # 模擬載入動畫
            time.sleep(0.5)

    def show_tool_result(self, tool_name: str, result: Any):
        """顯示工具結果"""
        if self.status_container:
            # 簡單顯示工具執行成功
            if result:
                self.status_container.success(f"✓ 成功取得資料")
            else:
                self.status_container.warning(f"⚠ 未取得資料")

    def show_task_completed(self, task_id: int):
        """顯示任務完成"""
        if task_id in self.task_progress:
            self.task_progress[task_id] = True

        if self.status_container:
            # 更新任務列表顯示
            completed = sum(1 for done in self.task_progress.values() if done)
            total = len(self.task_progress)

            if completed < total:
                self.status_container.write(f"📈 進度: {completed}/{total} 任務完成")
            else:
                self.status_container.write(f"🎉 所有任務完成！")

    def show_answer(self, answer: str):
        """顯示最終答案（由主應用程式處理）"""
        # 這個方法在 Streamlit 版本中由主應用程式處理
        # 保留此方法以保持介面相容性
        pass

    def show_error(self, error: str):
        """顯示錯誤訊息"""
        if self.status_container:
            self.status_container.error(f"❌ 錯誤: {error}")

    def show_warning(self, warning: str):
        """顯示警告訊息"""
        if self.status_container:
            self.status_container.warning(f"⚠️ 警告: {warning}")

    def show_info(self, info: str):
        """顯示資訊訊息"""
        if self.status_container:
            self.status_container.info(f"ℹ️ {info}")

    def show_loop_detected(self, last_actions: List[str]):
        """顯示偵測到循環"""
        if self.status_container:
            self.status_container.warning(
                f"🔄 偵測到重複動作，自動跳過任務。\n"
                f"最近的動作: {', '.join(last_actions[-2:]) if len(last_actions) >= 2 else '無'}"
            )

    def show_max_steps_reached(self, task_description: str):
        """顯示達到最大步驟限制"""
        if self.status_container:
            self.status_container.warning(
                f"⏱️ 任務「{task_description}」已達到最大步驟限制，標記為完成。"
            )

    def show_planning_started(self):
        """顯示開始規劃"""
        if self.status_container:
            self.status_container.write("🧠 正在分析您的問題並規劃任務...")

    def show_planning_completed(self, num_tasks: int):
        """顯示規劃完成"""
        if self.status_container:
            self.status_container.write(f"✨ 規劃完成！已建立 {num_tasks} 個任務。")

    def show_no_tasks(self):
        """顯示沒有任務"""
        if self.status_container:
            self.status_container.info(
                "這個問題可能超出了財務分析的範圍，或無法用可用的財務數據工具來回答。"
            )

    def show_working_on_task(self, task_description: str):
        """顯示正在處理的任務"""
        if self.status_container:
            self.status_container.write(f"🔍 正在處理: **{task_description}**")

    def show_validation_check(self, task_description: str):
        """顯示驗證檢查"""
        if self.status_container:
            self.status_container.write(f"✔️ 檢查任務是否完成: {task_description}")

    def show_generating_answer(self):
        """顯示正在生成答案"""
        if self.status_container:
            self.status_container.write("✍️ 正在整理分析結果並生成答案...")