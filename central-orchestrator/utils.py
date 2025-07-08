try:
    from langchain_core.tools import tool as langchain_tool
    LANGCHAIN_TOOL_DECORATOR_AVAILABLE = True
except ImportError:
    LANGCHAIN_TOOL_DECORATOR_AVAILABLE = False

def tool_wrapper(func):
    """Decorator that works with or without LangChain tools"""
    if LANGCHAIN_TOOL_DECORATOR_AVAILABLE:
        return langchain_tool(func)
    else:
        # Just return the function with some metadata
        func.name = func.__name__
        func.description = func.__doc__ or f"Tool: {func.__name__}"
        return func 