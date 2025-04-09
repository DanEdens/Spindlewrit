from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ProjectType(str, Enum):
    PYTHON = "python"
    RUST = "rust"
    COMMON = "common"


class ProjectConfig(BaseModel):
    name: str
    description: str
    project_type: ProjectType
    path: str
    additional_details: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    success: bool
    message: str
    project_path: Optional[str] = None
    errors: Optional[List[str]] = None 
