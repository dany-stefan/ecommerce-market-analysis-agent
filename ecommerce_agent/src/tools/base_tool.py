"""
Base Tool Interface
Simple abstract class that all tools inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class ToolInput(BaseModel):
    """Base class for tool inputs - ensures consistent data structure"""
    pass


class ToolOutput(BaseModel):
    """Base class for tool outputs - ensures consistent data structure"""
    success: bool
    data: Dict[str, Any]
    error: str = ""


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    Design Decision: Keep it simple - each tool has:
    - A name (for identification)
    - A description (for the agent to understand what it does)
    - An execute method (the actual work)
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @property
    @abstractmethod
    def description(self) -> str:
        """What does this tool do? Used by agent for decision making."""
        pass
    
    @abstractmethod
    def execute(self, input_data: ToolInput) -> ToolOutput:
        """
        Execute the tool's functionality.
        
        Args:
            input_data: Validated input data
            
        Returns:
            ToolOutput with success status and results
        """
        pass
    
    def run(self, input_data: ToolInput) -> ToolOutput:
        """
        Public method to run the tool with error handling.
        """
        try:
            return self.execute(input_data)
        except Exception as e:
            return ToolOutput(
                success=False,
                data={},
                error=f"Tool {self.name} failed: {str(e)}"
            )
