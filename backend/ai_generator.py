import anthropic
from typing import List, Optional

class AIGenerator:
    """Handles interactions with Anthropic's Claude API for generating responses"""

    MAX_TOOL_ROUNDS = 2

    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to two tools for course information.

Tool Selection:
- **get_course_outline**: Use this when the user asks what lessons or topics a course contains, wants a list of lessons, a table of contents, or an overview of what a course covers. Always include the course URL and list every lesson number and title in your response.
- **search_course_content**: Use this for questions about specific course content, explanations, examples, or detailed educational material within a course.
- **Up to 2 sequential tool-call rounds per query**: You may call a tool, see its results, then call another tool if more information is needed. Stop calling tools as soon as you have enough to answer fully.
- **Sequential example**: First call get_course_outline to find the lesson title, then call search_course_content for that lesson's content.
- Do not use search_course_content when the user only wants the lesson list — use get_course_outline instead
- Synthesize tool results into accurate, fact-based responses
- If a tool yields no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without using any tool
- **Course structure questions**: Use get_course_outline, then present the full lesson list with the course link
- **Course content questions**: Use search_course_content, then answer
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, tool usage explanations, or question-type analysis
 - Do not mention "based on the search results"


All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""

    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

        # Pre-build base API parameters
        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }

    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None) -> str:
        """
        Generate AI response with optional tool usage and conversation context.

        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools

        Returns:
            Generated response as string
        """
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history
            else self.SYSTEM_PROMPT
        )
        messages = [{"role": "user", "content": query}]
        api_params = {**self.base_params, "messages": messages, "system": system_content}
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = {"type": "auto"}

        response = self.client.messages.create(**api_params)

        # Path A: direct text response
        if response.stop_reason != "tool_use" or not tool_manager:
            return response.content[0].text

        # Path B: delegate to loop
        messages.append({"role": "assistant", "content": response.content})
        return self._run_tool_loop(messages, system_content, tools, tool_manager)

    def _run_tool_loop(self, messages, system_content, tools, tool_manager):
        """
        Execute sequential tool-call rounds (up to MAX_TOOL_ROUNDS).

        Args:
            messages: Message history including the first assistant tool_use response
            system_content: System prompt string
            tools: Tool definitions for intermediate rounds
            tool_manager: Manager to execute tools

        Returns:
            Final response text
        """
        for round_num in range(self.MAX_TOOL_ROUNDS):
            # Execute all tool_use blocks from last assistant message
            tool_results = []
            execution_failed = False
            for block in messages[-1]["content"]:
                if block.type == "tool_use":
                    try:
                        result = tool_manager.execute_tool(block.name, **block.input)
                    except Exception as e:
                        result = f"Tool execution error: {e}"
                        execution_failed = True
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})

            is_last_round = (round_num == self.MAX_TOOL_ROUNDS - 1)
            next_params = {**self.base_params, "messages": messages, "system": system_content}

            # Include tools on intermediate rounds unless a tool error occurred
            if not is_last_round and not execution_failed:
                next_params["tools"] = tools
                next_params["tool_choice"] = {"type": "auto"}

            response = self.client.messages.create(**next_params)

            # Termination: Claude returned text — stop immediately
            if response.stop_reason != "tool_use":
                return response.content[0].text

            # Last round or error — return what we got
            if is_last_round or execution_failed:
                return response.content[0].text

            messages.append({"role": "assistant", "content": response.content})

        return ""  # defensive fallback
