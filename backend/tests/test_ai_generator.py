"""Tests for AIGenerator sequential tool-calling loop."""
import pytest
from unittest.mock import MagicMock, patch, call
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_generator import AIGenerator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_text_response(text="answer"):
    block = MagicMock()
    block.type = "text"
    block.text = text
    r = MagicMock()
    r.stop_reason = "end_turn"
    r.content = [block]
    return r


def make_tool_use_response(tool_name="search_course_content", tool_id="tool_1", tool_input=None):
    block = MagicMock()
    block.type = "tool_use"
    block.name = tool_name
    block.id = tool_id
    block.input = tool_input or {"query": "test"}
    r = MagicMock()
    r.stop_reason = "tool_use"
    r.content = [block]
    return r


def make_generator():
    with patch("anthropic.Anthropic"):
        gen = AIGenerator(api_key="test-key", model="test-model")
    return gen


# ---------------------------------------------------------------------------
# 1. No tool use — direct text response
# ---------------------------------------------------------------------------

def test_no_tool_use_single_api_call():
    gen = make_generator()
    text_resp = make_text_response("direct answer")
    gen.client.messages.create = MagicMock(return_value=text_resp)

    tool_manager = MagicMock()
    result = gen.generate_response("What is Python?", tools=["fake_tool"], tool_manager=tool_manager)

    assert result == "direct answer"
    gen.client.messages.create.assert_called_once()
    tool_manager.execute_tool.assert_not_called()


# ---------------------------------------------------------------------------
# 2. Single tool round — 2 API calls
# ---------------------------------------------------------------------------

def test_single_tool_round_two_api_calls():
    gen = make_generator()
    tool_resp = make_tool_use_response("search_course_content", "id_1", {"query": "loops"})
    text_resp = make_text_response("loops explanation")
    gen.client.messages.create = MagicMock(side_effect=[tool_resp, text_resp])

    tool_manager = MagicMock()
    tool_manager.execute_tool.return_value = "Loops are ..."

    result = gen.generate_response("Explain loops", tools=["fake_tool"], tool_manager=tool_manager)

    assert result == "loops explanation"
    assert gen.client.messages.create.call_count == 2
    tool_manager.execute_tool.assert_called_once_with("search_course_content", query="loops")

    # Second API call is round 0 (intermediate) — tools ARE included
    second_call_kwargs = gen.client.messages.create.call_args_list[1][1]
    assert "tools" in second_call_kwargs

    # Second API call messages must include the tool_result
    second_messages = second_call_kwargs["messages"]
    tool_result_msg = second_messages[-1]
    assert tool_result_msg["role"] == "user"
    assert tool_result_msg["content"][0]["type"] == "tool_result"
    assert tool_result_msg["content"][0]["tool_use_id"] == "id_1"


# ---------------------------------------------------------------------------
# 3. Two sequential rounds — 3 API calls
# ---------------------------------------------------------------------------

def test_two_sequential_rounds_three_api_calls():
    gen = make_generator()
    tool_resp_1 = make_tool_use_response("get_course_outline", "id_1", {"course_name": "Python 101"})
    tool_resp_2 = make_tool_use_response("search_course_content", "id_2", {"query": "lesson 3"})
    text_resp = make_text_response("final synthesis")

    gen.client.messages.create = MagicMock(side_effect=[tool_resp_1, tool_resp_2, text_resp])

    tool_manager = MagicMock()
    tool_manager.execute_tool.side_effect = ["outline data", "lesson content"]

    result = gen.generate_response("Tell me about lesson 3", tools=["fake_tool"], tool_manager=tool_manager)

    assert result == "final synthesis"
    assert gen.client.messages.create.call_count == 3
    assert tool_manager.execute_tool.call_count == 2

    calls = gen.client.messages.create.call_args_list

    # Second call (round 0): MUST include tools (intermediate round, no error)
    second_kwargs = calls[1][1]
    assert "tools" in second_kwargs

    # Third call (round 1, last): must NOT include tools
    third_kwargs = calls[2][1]
    assert "tools" not in third_kwargs

    # Final messages array has 5 entries:
    # [user-query, assistant-R0, user-results-R0, assistant-R1, user-results-R1]
    final_messages = third_kwargs["messages"]
    assert len(final_messages) == 5


# ---------------------------------------------------------------------------
# 4. Early termination — text after round 0 → only 2 total calls
# ---------------------------------------------------------------------------

def test_early_termination_after_round_zero():
    gen = make_generator()
    tool_resp = make_tool_use_response("search_course_content", "id_1", {"query": "x"})
    text_resp = make_text_response("early answer")

    gen.client.messages.create = MagicMock(side_effect=[tool_resp, text_resp])

    tool_manager = MagicMock()
    tool_manager.execute_tool.return_value = "some result"

    result = gen.generate_response("question", tools=["fake_tool"], tool_manager=tool_manager)

    assert result == "early answer"
    assert gen.client.messages.create.call_count == 2  # not 3


# ---------------------------------------------------------------------------
# 5. Tool execution error — no tools on final call, no exception propagated
# ---------------------------------------------------------------------------

def test_tool_execution_error_handled_gracefully():
    gen = make_generator()
    tool_resp = make_tool_use_response("search_course_content", "id_err", {"query": "bad"})
    text_resp = make_text_response("error response")

    gen.client.messages.create = MagicMock(side_effect=[tool_resp, text_resp])

    tool_manager = MagicMock()
    tool_manager.execute_tool.side_effect = RuntimeError("DB connection failed")

    result = gen.generate_response("question", tools=["fake_tool"], tool_manager=tool_manager)

    assert result == "error response"
    assert gen.client.messages.create.call_count == 2

    # Final call must NOT include tools (execution_failed=True)
    final_kwargs = gen.client.messages.create.call_args_list[1][1]
    assert "tools" not in final_kwargs

    # Tool result content must contain the error message
    final_messages = final_kwargs["messages"]
    tool_result_content = final_messages[-1]["content"][0]["content"]
    assert "DB connection failed" in tool_result_content


# ---------------------------------------------------------------------------
# 6. Conversation history — appears in system across all calls
# ---------------------------------------------------------------------------

def test_conversation_history_in_system_param():
    gen = make_generator()
    tool_resp = make_tool_use_response("search_course_content", "id_h", {"query": "q"})
    text_resp = make_text_response("answer with history")

    gen.client.messages.create = MagicMock(side_effect=[tool_resp, text_resp])

    tool_manager = MagicMock()
    tool_manager.execute_tool.return_value = "result"

    history = "User: hi\nAssistant: hello"
    gen.generate_response("follow-up", conversation_history=history, tools=["t"], tool_manager=tool_manager)

    for c in gen.client.messages.create.call_args_list:
        system_arg = c[1]["system"]
        assert history in system_arg
