from typing import List, Optional

from langchain_core.messages import AIMessage

from dexter.model import call_llm
from dexter.prompts import (
    ACTION_SYSTEM_PROMPT,
    ANSWER_SYSTEM_PROMPT,
    PLANNING_SYSTEM_PROMPT,
    VALIDATION_SYSTEM_PROMPT,
)
from dexter.schemas import Answer, IsDone, Task, TaskList
from dexter.tools import TOOLS
from dexter.utils.logger import Logger
from dexter.utils.ui import show_progress


class Agent:
    def __init__(self, max_steps: int = 20, max_steps_per_task: int = 5, use_chinese: bool = False, ui=None, model_name: str = None):
        self.logger = Logger()
        self.max_steps = max_steps            # global safety cap
        self.max_steps_per_task = max_steps_per_task
        self.use_chinese = use_chinese
        self.ui = ui  # Optional UI adapter (e.g., StreamlitUI)
        self.model_name = model_name  # OpenAI model to use

        # Load Chinese prompts if needed
        if self.use_chinese:
            from dexter.prompts_zh_tw import (
                ACTION_SYSTEM_PROMPT_ZH,
                ANSWER_SYSTEM_PROMPT_ZH,
                PLANNING_SYSTEM_PROMPT_ZH,
                VALIDATION_SYSTEM_PROMPT_ZH,
            )
            self.planning_prompt = PLANNING_SYSTEM_PROMPT_ZH
            self.action_prompt = ACTION_SYSTEM_PROMPT_ZH
            self.validation_prompt = VALIDATION_SYSTEM_PROMPT_ZH
            self.answer_prompt = ANSWER_SYSTEM_PROMPT_ZH
        else:
            self.planning_prompt = PLANNING_SYSTEM_PROMPT
            self.action_prompt = ACTION_SYSTEM_PROMPT
            self.validation_prompt = VALIDATION_SYSTEM_PROMPT
            self.answer_prompt = ANSWER_SYSTEM_PROMPT

    # ---------- task planning ----------
    def plan_tasks(self, query: str) -> List[Task]:
        if self.ui:
            self.ui.show_planning_started()

        tool_descriptions = "\n".join([f"- {t.name}: {t.description}" for t in TOOLS])

        if self.use_chinese:
            prompt = f"""
            給定用戶查詢："{query}"，
            創建一個需要完成的任務列表。
            範例：{{"tasks": [{{"id": 1, "description": "某個任務", "done": false}}]}}
            """
        else:
            prompt = f"""
            Given the user query: "{query}",
            Create a list of tasks to be completed.
            Example: {{"tasks": [{{"id": 1, "description": "some task", "done": false}}]}}
            """

        system_prompt = self.planning_prompt.format(tools=tool_descriptions)
        try:
            response = call_llm(prompt, system_prompt=system_prompt, output_schema=TaskList, model_name=self.model_name)
            tasks = response.tasks
        except Exception as e:
            if not self.ui:
                self.logger._log(f"Planning failed: {e}")
            else:
                self.ui.show_error(f"規劃失敗: {e}" if self.use_chinese else f"Planning failed: {e}")
            tasks = [Task(id=1, description=query, done=False)]

        if self.ui:
            if tasks:
                self.ui.show_planning_completed(len(tasks))
                self.ui.show_tasks(tasks)
            else:
                self.ui.show_no_tasks()
        else:
            task_dicts = [task.dict() for task in tasks]
            self.logger.log_task_list(task_dicts)

        return tasks

    # ---------- ask LLM what to do ----------
    def ask_for_actions(self, task_desc: str, last_outputs: str = "") -> AIMessage:
        # last_outputs = textual feedback of what we just tried
        if self.use_chinese:
            prompt = f"""
            我們正在處理："{task_desc}"。
            以下是到目前為止工具輸出的歷史記錄：{last_outputs}

            基於任務和輸出，下一步應該是什麼？
            """
        else:
            prompt = f"""
            We are working on: "{task_desc}".
            Here is a history of tool outputs from the session so far: {last_outputs}

            Based on the task and the outputs, what should be the next step?
            """
        try:
            return call_llm(prompt, system_prompt=self.action_prompt, tools=TOOLS, model_name=self.model_name)
        except Exception as e:
            if self.ui:
                self.ui.show_error(f"獲取操作失敗: {e}" if self.use_chinese else f"ask_for_actions failed: {e}")
            else:
                self.logger._log(f"ask_for_actions failed: {e}")
            return AIMessage(content="Failed to get actions.")

    # ---------- ask LLM if task is done ----------
    def ask_if_done(self, task_desc: str, recent_results: str) -> bool:
        if self.ui:
            self.ui.show_validation_check(task_desc)

        if self.use_chinese:
            prompt = f"""
            我們試圖完成任務："{task_desc}"。
            以下是到目前為止工具輸出的歷史記錄：{recent_results}

            任務完成了嗎？
            """
        else:
            prompt = f"""
            We were trying to complete the task: "{task_desc}".
            Here is a history of tool outputs from the session so far: {recent_results}

            Is the task done?
            """
        try:
            resp = call_llm(prompt, system_prompt=self.validation_prompt, output_schema=IsDone, model_name=self.model_name)
            return resp.done
        except:
            return False

    # ---------- tool execution ----------
    def _execute_tool(self, tool, tool_name: str, inp_args):
        """Execute a tool with progress indication."""
        if self.ui:
            self.ui.show_tool_execution(tool_name, inp_args)
            result = tool.run(inp_args)
            self.ui.show_tool_result(tool_name, result)
            return result
        else:
            # Create a dynamic decorator with the tool name
            @show_progress(f"Executing {tool_name}...", "")
            def run_tool():
                return tool.run(inp_args)
            return run_tool()
    
    # ---------- confirm action ----------
    def confirm_action(self, tool: str, input_str: str) -> bool:
        # In production you'd ask the user; here we just log and auto-confirm
        # Risky tools are not implemented in this version.
        return True

    # ---------- main loop ----------
    def run(self, query: str):
        # Reset state
        step_count = 0
        last_actions = []
        session_outputs = []  # accumulate outputs for the whole session

        # Plan tasks
        tasks = self.plan_tasks(query)

        # If no tasks were created, query is out of scope - answer directly
        if not tasks:
            answer = self._generate_answer(query, session_outputs)
            self.logger.log_summary(answer)
            return answer

        # Main agent loop
        while any(not t.done for t in tasks):
            if step_count >= self.max_steps:
                self.logger._log("Global max steps reached — aborting to avoid runaway loop.")
                break

            task = next(t for t in tasks if not t.done)
            if self.ui:
                self.ui.show_working_on_task(task.description)
            else:
                self.logger.log_task_start(task.description)

            per_task_steps = 0
            while per_task_steps < self.max_steps_per_task:
                if step_count >= self.max_steps:
                    self.logger._log("Global max steps reached — stopping.")
                    return

                ai_message = self.ask_for_actions(task.description, last_outputs="\n".join(session_outputs))
                
                if not ai_message.tool_calls:
                    # No tool calls means either the task is done or cannot be done with tools
                    # Always mark as done to avoid infinite loops
                    # The final answer generation will provide an appropriate response
                    task.done = True
                    if self.ui:
                        self.ui.show_task_completed(task.id)
                    else:
                        self.logger.log_task_done(task.description)
                    break

                for tool_call in ai_message.tool_calls:
                    if step_count >= self.max_steps:
                        break

                    tool_name = tool_call["name"]
                    inp_args = tool_call["args"]
                    action_sig = f"{tool_name}:{inp_args}"

                    # stuck detection
                    last_actions.append(action_sig)
                    if len(last_actions) > 4:
                        last_actions = last_actions[-4:]
                    if len(set(last_actions)) == 1 and len(last_actions) == 4:
                        self.logger._log("Detected repeating action — aborting to avoid loop.")
                        return
                    
                    tool_to_run = next((t for t in TOOLS if t.name == tool_name), None)
                    if tool_to_run and self.confirm_action(tool_name, str(inp_args)):
                        try:
                            result = self._execute_tool(tool_to_run, tool_name, inp_args)
                            self.logger.log_tool_run(tool_name, f"{result}")
                            session_outputs.append(f"Output of {tool_name} with args {inp_args}: {result}")
                        except Exception as e:
                            self.logger._log(f"Tool execution failed: {e}")
                            session_outputs.append(f"Error from {tool_name} with args {inp_args}: {e}")
                    else:
                        self.logger._log(f"Invalid tool: {tool_name}")

                    step_count += 1
                    per_task_steps += 1

                # check after this batch if task seems done
                if self.ask_if_done(task.description, "\n".join(session_outputs)):
                    task.done = True
                    self.logger.log_task_done(task.description)
                    break

        # Generate answer based on all collected data
        answer = self._generate_answer(query, session_outputs)
        self.logger.log_summary(answer)
        return answer
    
    # ---------- answer generation ----------
    def _generate_answer(self, query: str, session_outputs: list) -> str:
        """Generate the final answer based on collected data."""
        if self.ui:
            self.ui.show_generating_answer()

        all_results = "\n\n".join(session_outputs) if session_outputs else (
            "沒有收集到數據。" if self.use_chinese else "No data was collected."
        )

        if self.use_chinese:
            answer_prompt = f"""
            原始用戶查詢："{query}"

            從工具收集的數據和結果：
            {all_results}

            基於以上數據，為用戶的查詢提供全面的答案。
            包含具體數字、計算和洞察。
            請用繁體中文回答。
            """
        else:
            answer_prompt = f"""
            Original user query: "{query}"

            Data and results collected from tools:
            {all_results}

            Based on the data above, provide a comprehensive answer to the user's query.
            Include specific numbers, calculations, and insights.
            """

        answer_obj = call_llm(answer_prompt, system_prompt=self.answer_prompt, output_schema=Answer, model_name=self.model_name)
        return answer_obj.answer
