"""XML tool call parser for LLM output."""

from __future__ import annotations

import json
import re

from src.models import ToolCall

# Regex to extract <tool_call>...</tool_call> blocks
TOOL_CALL_RE = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL)
# Regex to extract <tool>name</tool> (including tolerant mismatched closing tags)
TOOL_NAME_RE = re.compile(
    r"<tool>\s*([\w-]+)\s*</(?:tool|parameter|function|invoke)>", re.DOTALL
)
INVOKE_NAME_RE = re.compile(r"<invoke\s+name=[\"']([\w-]+)[\"']\s*>", re.DOTALL)
# Regex to extract <parameters>...</parameters> (or unclosed/mismatched <parameters> to end of block)
PARAMS_BLOCK_RE = re.compile(r"<parameters>(.*?)</parameters>", re.DOTALL)
PARAMS_OPEN_RE = re.compile(r"<parameters>(.*)", re.DOTALL)
# Standard <param_name>value</param_name> pairs
PARAM_RE = re.compile(r"<(\w+)>(.*?)</\1>", re.DOTALL)
# Attribute-style <parameter name="param_name">value</parameter> pairs
NAMED_PARAM_RE = re.compile(
    r"<parameter\s+name=[\"'](\w+)[\"']\s*>(.*?)</parameter>", re.DOTALL
)
# Fallback for inner tags closed by mismatched </parameter> or </function>
MISMATCHED_PARAM_RE = re.compile(
    r"<(\w+)>(.*?)</(?:parameter|function|parameters)>", re.DOTALL
)
_WRAPPER_TAGS = {"tool", "parameters", "parameter", "function", "invoke", "tool_call"}


def _convert_value(value: str) -> int | float | bool | str | list | dict:
    """Smart type conversion: try int, float, bool, JSON (list/dict), else str."""
    stripped = value.strip()
    # bool
    if stripped.lower() == "true":
        return True
    if stripped.lower() == "false":
        return False
    # int
    try:
        return int(stripped)
    except ValueError:
        pass
    # float
    try:
        return float(stripped)
    except ValueError:
        pass
    # JSON list or dict
    if stripped.startswith(("[", "{")):
        try:
            return json.loads(stripped)
        except (json.JSONDecodeError, ValueError):
            pass
    # str (preserve original whitespace-stripped value)
    return stripped


def _extract_parameters(params_text: str) -> dict:
    """Extract parameter key-value pairs tolerating minor LLM XML tag slips."""
    params: dict = {}

    def _consume(pattern: re.Pattern[str], text: str) -> str:
        kept_parts: list[str] = []
        last_end = 0
        for match in pattern.finditer(text):
            key, val = match.group(1), match.group(2)
            if key in _WRAPPER_TAGS:
                continue
            if key not in params:
                params[key] = _convert_value(val)
            kept_parts.append(text[last_end:match.start()])
            last_end = match.end()
        kept_parts.append(text[last_end:])
        return "".join(kept_parts)

    remaining = _consume(NAMED_PARAM_RE, params_text)
    remaining = _consume(PARAM_RE, remaining)
    _consume(MISMATCHED_PARAM_RE, remaining)

    if not params:
        stripped = params_text.strip()
        if stripped.startswith("{"):
            try:
                loaded = json.loads(stripped)
                if isinstance(loaded, dict):
                    params.update(loaded)
            except (json.JSONDecodeError, ValueError):
                pass
    return params


def _extract_tool_call_blocks(text: str) -> list[str]:
    """Extract <tool_call> blocks, tolerating missing </tool_call> or </invoke> endings."""
    starts = [m.end() for m in re.finditer(r"<tool_call>", text)]
    blocks: list[str] = []
    for idx, start in enumerate(starts):
        limit = starts[idx + 1] - len("<tool_call>") if idx + 1 < len(starts) else len(text)
        segment = text[start:limit]
        end_tag = segment.find("</tool_call>")
        if end_tag != -1:
            blocks.append(segment[:end_tag])
        else:
            blocks.append(segment)
    return blocks


def parse_tool_calls(text: str) -> list[ToolCall]:
    """Parse all <tool_call> blocks from LLM output text.

    Returns a list of ToolCall objects. Gracefully handles malformed blocks
    by skipping them and continuing.
    """
    results = []
    blocks = _extract_tool_call_blocks(text)

    for block in blocks:
        name_match = TOOL_NAME_RE.search(block) or INVOKE_NAME_RE.search(block)
        if not name_match:
            continue
        tool_name = name_match.group(1).strip()

        params_match = PARAMS_BLOCK_RE.search(block) or PARAMS_OPEN_RE.search(block)
        params_text = params_match.group(1) if params_match else block[name_match.end():]
        params = _extract_parameters(params_text)

        results.append(ToolCall(tool=tool_name, parameters=params))

    return results
