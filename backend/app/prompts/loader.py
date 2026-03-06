"""
Prompt Loader - Load prompts from markdown files
"""

import os
from pathlib import Path
from typing import Dict, Optional


# Get the directory containing prompt files
PROMPTS_DIR = Path(__file__).parent


def load_prompt_md(filename: str) -> str:
    """
    Load a markdown file and return its content.
    
    Args:
        filename: Name of the markdown file (e.g., 'supervisor.md')
    
    Returns:
        Content of the markdown file as string
    """
    file_path = PROMPTS_DIR / filename
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_section(content: str, section_title: str) -> str:
    """
    Extract a specific section from markdown content.
    
    Args:
        content: Full markdown content
        section_title: Title of the section to extract (e.g., 'System Prompt')
    
    Returns:
        Content of the section
    """
    lines = content.split('\n')
    in_section = False
    section_content = []
    
    for line in lines:
        # Check for section header (## Title)
        if line.startswith('## '):
            if in_section:
                # End of current section
                break
            if section_title.lower() in line.lower():
                in_section = True
                continue
        
        if in_section:
            # Skip the separator line
            if line.strip() == '---':
                continue
            section_content.append(line)
    
    return '\n'.join(section_content).strip()


def get_system_prompt(agent_name: str) -> str:
    """
    Get the system prompt for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., 'supervisor', 'data_parser')
    
    Returns:
        System prompt content
    """
    content = load_prompt_md(f'{agent_name}.md')
    return extract_section(content, 'System Prompt')


def get_prompt_template(agent_name: str, template_name: str) -> str:
    """
    Get a specific prompt template from an agent's markdown file.
    
    Args:
        agent_name: Name of the agent
        template_name: Name of the template section
    
    Returns:
        Template content
    """
    content = load_prompt_md(f'{agent_name}.md')
    return extract_section(content, template_name)


# Pre-loaded prompts for backward compatibility
# These load from .md files but expose as module-level variables

def _load_all_prompts() -> Dict[str, str]:
    """Load all prompts from markdown files."""
    prompts = {}
    
    # Supervisor prompts
    supervisor_content = load_prompt_md('supervisor.md')
    prompts['SUPERVISOR_SYSTEM_PROMPT'] = extract_section(supervisor_content, 'System Prompt')
    prompts['SUPERVISOR_INTENT_PROMPT'] = extract_section(supervisor_content, 'Intent Analysis Prompt')
    prompts['SUPERVISOR_AGGREGATION_PROMPT'] = extract_section(supervisor_content, 'Aggregation Prompt')
    
    # DataParser prompts
    data_parser_content = load_prompt_md('data_parser.md')
    prompts['DATA_PARSER_SYSTEM_PROMPT'] = extract_section(data_parser_content, 'System Prompt')
    prompts['DATA_PARSER_PROMPT'] = extract_section(data_parser_content, 'Data Parsing Prompt')
    
    # Analysis prompts
    analysis_content = load_prompt_md('analysis.md')
    prompts['ANALYSIS_SYSTEM_PROMPT'] = extract_section(analysis_content, 'System Prompt')
    prompts['ANALYSIS_PROMPT'] = extract_section(analysis_content, 'Analysis Prompt')
    
    # Visualization prompts
    visualization_content = load_prompt_md('visualization.md')
    prompts['VISUALIZATION_SYSTEM_PROMPT'] = extract_section(visualization_content, 'System Prompt')
    prompts['VISUALIZATION_PROMPT'] = extract_section(visualization_content, 'Visualization Prompt')
    
    # Debugger prompts
    debugger_content = load_prompt_md('debugger.md')
    prompts['DEBUGGER_SYSTEM_PROMPT'] = extract_section(debugger_content, 'System Prompt')
    prompts['DEBUGGER_PROMPT'] = extract_section(debugger_content, 'Debug Prompt')
    
    return prompts


# Lazy load prompts
_prompts_cache: Optional[Dict[str, str]] = None


def get_prompts() -> Dict[str, str]:
    """Get all prompts (cached)."""
    global _prompts_cache
    if _prompts_cache is None:
        _prompts_cache = _load_all_prompts()
    return _prompts_cache


# Expose as module-level variables for backward compatibility
def __getattr__(name: str) -> str:
    """Lazy load prompt variables."""
    prompts = get_prompts()
    if name in prompts:
        return prompts[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")