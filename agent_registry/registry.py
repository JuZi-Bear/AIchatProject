from agent_registry.agent_meta import AgentMeta


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, AgentMeta] = {}

    def register(self, agent_meta: AgentMeta):
        if not agent_meta.key:
            raise ValueError("agent_meta.key 不能为空")

        self._agents[agent_meta.key] = agent_meta
        return agent_meta

    def get_agent(self, key: str):
        return self._agents.get(key)

    def list_agents(self):
        return list(self._agents.values())

    def list_enabled_agents(self):
        return [agent for agent in self.list_agents() if agent.enabled]

    def to_dict_list(self):
        return [agent.to_dict() for agent in self.list_agents()]
