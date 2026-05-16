from typing import List

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    requirement: str = Field(..., description="User requirement for one AI workflow run.")
    model_provider: str = Field("deepseek", description="Model provider key, such as deepseek/qwen/zhipu.")
    enabled_plugins: List[str] = Field(default_factory=list)
    max_retry_count: int = 3
    require_human_approval: bool = True
    demo_mode: bool = True
    offline_mode: bool = False
