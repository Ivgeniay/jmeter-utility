from enum import Enum


class LLMModel(Enum):
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"
    
    O1 = "o1"
    O1_MINI = "o1-mini"
    O1_PREVIEW = "o1-preview"
    
    CLAUDE_35_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_35_HAIKU = "claude-3-5-haiku-20241022"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    
    @property
    def is_openai(self) -> bool:
        return self.value.startswith(("gpt-", "o1"))
    
    @property
    def is_anthropic(self) -> bool:
        return self.value.startswith("claude-")
    
    @classmethod
    def default(cls) -> "LLMModel":
        return cls.GPT_4O_MINI