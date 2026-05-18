from dataclasses import asdict, dataclass, field


@dataclass
class AgentMeta:
    key: str
    name: str
    role: str
    description: str
    input_fields: list[str] = field(default_factory=list)
    output_fields: list[str] = field(default_factory=list)
    stage: str = ""
    enabled: bool = True
    version: str = "1.0"

    def to_dict(self) -> dict:
        return asdict(self)
