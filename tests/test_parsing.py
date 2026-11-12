"""Unit tests for fault-tolerant XML tool call parsing in SILO-BENCH."""

import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SILO_BENCH_ROOT = WORKSPACE_ROOT / "silo-bench"
if str(SILO_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(SILO_BENCH_ROOT))

from src.utils.parsing import parse_tool_calls  # type: ignore[import-not-found]


def test_standard_xml_tool_call():
    text = """
    <tool_call>
      <tool>send_message</tool>
      <parameters>
        <target_id>1</target_id>
        <content>My local max is 827</content>
      </parameters>
    </tool_call>
    """
    calls = parse_tool_calls(text)
    assert len(calls) == 1
    assert calls[0].tool == "send_message"
    assert calls[0].parameters == {"target_id": 1, "content": "My local max is 827"}


def test_mismatched_parameter_and_function_closing_tags():
    text = """
    <tool_call>
      <tool>send_message</tool>
      <parameters>
        <target_id>1</target_id>
        <content>Please send your data list for distributed sorting.</parameter>
      </function>
    </tool_call>
    """
    calls = parse_tool_calls(text)
    assert len(calls) == 1
    assert calls[0].tool == "send_message"
    assert calls[0].parameters == {
        "target_id": 1,
        "content": "Please send your data list for distributed sorting.",
    }


def test_named_parameter_attribute_syntax():
    text = """
    <tool_call>
      <tool>send_message</parameter>
    </invoke>
    <invoke name="send_message">
    <parameter name="target_id">0</parameter>
    <parameter name="content">Hello from agent 1</parameter>
    </invoke>
    </tool_call>
    """
    calls = parse_tool_calls(text)
    assert len(calls) == 1
    assert calls[0].tool == "send_message"
    assert calls[0].parameters == {"target_id": 0, "content": "Hello from agent 1"}


def test_submit_result_list_with_mismatched_closing_tag():
    text = """
    <tool_call>
      <tool>submit_result</tool>
      <parameters>
        <answer>[12, 15, 41]</parameter>
      </parameters>
    </tool_call>
    """
    calls = parse_tool_calls(text)
    assert len(calls) == 1
    assert calls[0].tool == "submit_result"
    assert calls[0].parameters == {"answer": [12, 15, 41]}


def test_tool_call_closed_with_invoke_instead_of_tool_call():
    text = """
    Message sent. Now let me wait.
    <tool_call>
      <tool>wait</tool>
    </invoke>
    """
    calls = parse_tool_calls(text)
    assert len(calls) == 1
    assert calls[0].tool == "wait"
    assert calls[0].parameters == {}


def test_send_message_missing_closing_tool_call_tag():
    text = """
    <tool_call>
      <tool>send_message</tool>
      <parameters>
        <target_id>1</target_id>
        <content>Hello world</parameter>
      </invoke>
    </parameter>
    </invoke>
    """
    calls = parse_tool_calls(text)
    assert len(calls) == 1
    assert calls[0].tool == "send_message"
    assert calls[0].parameters == {"target_id": 1, "content": "Hello world"}

