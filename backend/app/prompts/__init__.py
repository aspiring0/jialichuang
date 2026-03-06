"""
Prompts module for Multi-Agent Data Analysis System
Contains prompt templates for all agents

Prompts are loaded from markdown (.md) files for easy editing.
The .py files are kept for backward compatibility.
"""

from app.prompts.loader import (
    load_prompt_md,
    extract_section,
    get_system_prompt,
    get_prompt_template,
    get_prompts,
)

# Lazy load prompts from .md files
# These are exposed as module-level attributes via __getattr__ in loader.py

# For explicit imports, use the get_prompts() function
# Example:
#   from app.prompts import get_prompts
#   prompts = get_prompts()
#   system_prompt = prompts['SUPERVISOR_SYSTEM_PROMPT']

# Or use the convenience functions:
#   from app.prompts import get_system_prompt
#   prompt = get_system_prompt('supervisor')

__all__ = [
    # Functions
    "load_prompt_md",
    "extract_section",
    "get_system_prompt",
    "get_prompt_template",
    "get_prompts",
    # Backward compatible variable names (lazy loaded)
    "SUPERVISOR_SYSTEM_PROMPT",
    "SUPERVISOR_INTENT_PROMPT",
    "SUPERVISOR_AGGREGATION_PROMPT",
    "DATA_PARSER_SYSTEM_PROMPT",
    "DATA_PARSER_PROMPT",
    "ANALYSIS_SYSTEM_PROMPT",
    "ANALYSIS_PROMPT",
    "VISUALIZATION_SYSTEM_PROMPT",
    "VISUALIZATION_PROMPT",
    "DEBUGGER_SYSTEM_PROMPT",
    "DEBUGGER_PROMPT",
]

def __getattr__(name: str):
    """Lazy load prompt variables from markdown files."""
    from app.prompts.loader import get_prompts
    prompts = get_prompts()
    if name in prompts:
        return prompts[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")