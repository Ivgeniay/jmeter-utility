from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel

from llm.models.llm_models import LLMModel
from payloads.console import SLog


class AgentRole(Enum):
    WORKER = "worker"
    VALIDATOR = "validator"


@dataclass
class Message:
    role: str
    content: str


@dataclass 
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    
    def to_feedback(self) -> str:
        lines = []
        if self.errors:
            lines.append("Ошибки:")
            for err in self.errors:
                lines.append(f"  - {err}")
        if self.suggestions:
            lines.append("Предложения:")
            for sug in self.suggestions:
                lines.append(f"  - {sug}")
        return "\n".join(lines)


def create_llm(model: LLMModel | None = None, temperature: float = 0.0) -> BaseChatModel:
    if model is None:
        model = LLMModel.default()
    
    if model.is_openai:
        return ChatOpenAI(model=model.value, temperature=temperature)
    elif model.is_anthropic:
        return ChatAnthropic(model=model.value, temperature=temperature)
    else:
        raise ValueError(f"Неизвестный провайдер для модели: {model.value}")


class BaseAgent[InputT, OutputT](ABC):
    
    def __init__(
        self,
        name: str,
        system_prompt: str,
        llm: BaseChatModel | None = None,
        model: LLMModel = LLMModel.GPT_4O_MINI,
        temperature: float = 0.0,
        max_iterations: int = 3,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.history: list[Message] = []
        
        if llm is not None:
            self.llm = llm
        else:
            self.llm = create_llm(model, temperature)
    
    @property
    @abstractmethod
    def role(self) -> AgentRole:
        pass
    
    @abstractmethod
    def _build_user_prompt(self, input_data: InputT) -> str:
        pass
    
    @abstractmethod
    def _parse_response(self, response: str) -> OutputT:
        pass
    
    def _invoke_llm(self, user_message: str) -> str:
        self.history.append(Message(role="user", content=user_message))
        
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in self.history:
            messages.append({"role": msg.role, "content": msg.content})
        
        response = self.llm.invoke(messages)
        response_text = response.content
        
        self.history.append(Message(role="assistant", content=response_text))
        
        return response_text
    
    def run(self, input_data: InputT) -> OutputT:
        self.history.clear()
        
        user_prompt = self._build_user_prompt(input_data)
        response = self._invoke_llm(user_prompt)
        
        return self._parse_response(response)
    
    def run_with_feedback(self, feedback: str) -> OutputT:
        if not self.history:
            raise ValueError("Нет истории. Сначала вызовите run().")
        
        response = self._invoke_llm(feedback)
        return self._parse_response(response)
    
    def get_history(self) -> list[Message]:
        return self.history.copy()
    
    def clear_history(self):
        self.history.clear()


class BaseWorker[InputT, OutputT](BaseAgent[InputT, OutputT]):
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.WORKER


class BaseValidator[InputT](BaseAgent[InputT, ValidationResult]):
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.VALIDATOR
    
    def _parse_response(self, response: str) -> ValidationResult:
        response_lower = response.lower()
        
        is_valid = "valid" in response_lower and "invalid" not in response_lower
        
        errors = []
        suggestions = []
        
        lines = response.strip().split("\n")
        current_section = None
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            line_lower = line_stripped.lower()
            if "ошибк" in line_lower or "error" in line_lower:
                current_section = "errors"
            elif "предложен" in line_lower or "suggestion" in line_lower or "рекомендац" in line_lower:
                current_section = "suggestions"
            elif line_stripped.startswith("-") or line_stripped.startswith("•"):
                content = line_stripped.lstrip("-•").strip()
                if current_section == "errors":
                    errors.append(content)
                elif current_section == "suggestions":
                    suggestions.append(content)
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            suggestions=suggestions,
        )


def run_with_validation[InputT, OutputT](
    worker: BaseWorker[InputT, OutputT],
    validator: BaseValidator[OutputT],
    input_data: InputT,
    max_iterations: int = 3,
    verbose: bool = True,
    mega_verbose: bool = False,
) -> tuple[OutputT, bool]:
    from payloads.console import SLog
    
    if verbose:
        SLog.log(f"[{worker.name}] Запуск...")
    
    if mega_verbose:
        SLog.log(f"[{worker.name}] System prompt:")
        SLog.log("-" * 40)
        SLog.log(worker.system_prompt[:500] + "..." if len(worker.system_prompt) > 500 else worker.system_prompt)
        SLog.log("-" * 40)
    
    output = worker.run(input_data)
    
    if verbose:
        SLog.log(f"[{worker.name}] Получен ответ")
    
    if mega_verbose:
        SLog.log(f"[{worker.name}] User prompt отправленный в LLM:")
        SLog.log("-" * 40)
        last_user_msg = next((m for m in reversed(worker.history) if m.role == "user"), None)
        if last_user_msg:
            SLog.log(last_user_msg.content[:1000] + "..." if len(last_user_msg.content) > 1000 else last_user_msg.content)
        SLog.log("-" * 40)
        SLog.log(f"[{worker.name}] Ответ LLM:")
        SLog.log("-" * 40)
        last_assistant_msg = next((m for m in reversed(worker.history) if m.role == "assistant"), None)
        if last_assistant_msg:
            SLog.log(last_assistant_msg.content[:1500] + "..." if len(last_assistant_msg.content) > 1500 else last_assistant_msg.content)
        SLog.log("-" * 40)
    
    for iteration in range(max_iterations):
        if hasattr(validator, 'update_worker_history'):
            validator.update_worker_history(worker.get_history())
        
        if verbose:
            SLog.log(f"[{validator.name}] Валидация (итерация {iteration + 1}/{max_iterations})...")
        
        if mega_verbose:
            SLog.log(f"[{validator.name}] Отправка на проверку...")
        
        validation = validator.run(output)
        
        if mega_verbose:
            SLog.log(f"[{validator.name}] Prompt отправленный в LLM:")
            SLog.log("-" * 40)
            last_user_msg = next((m for m in reversed(validator.history) if m.role == "user"), None)
            if last_user_msg:
                SLog.log(last_user_msg.content[:1500] + "..." if len(last_user_msg.content) > 1500 else last_user_msg.content)
            SLog.log("-" * 40)
            SLog.log(f"[{validator.name}] Ответ LLM:")
            SLog.log("-" * 40)
            last_assistant_msg = next((m for m in reversed(validator.history) if m.role == "assistant"), None)
            if last_assistant_msg:
                SLog.log(last_assistant_msg.content)
            SLog.log("-" * 40)
        
        if validation.is_valid:
            if verbose:
                SLog.log(f"[{validator.name}] ✓ Валидация пройдена")
            return output, True
        
        if verbose:
            SLog.log(f"[{validator.name}] ✗ Найдены проблемы ({len(validation.errors)} ошибок, {len(validation.suggestions)} рекомендаций):")
            for err in validation.errors:
                SLog.log(f"    ✗ {err}")
            for sug in validation.suggestions:
                SLog.log(f"    → {sug}")
        
        if iteration < max_iterations - 1:
            feedback = validation.to_feedback()
            
            if verbose:
                SLog.log(f"[{worker.name}] Исправление по feedback (итерация {iteration + 2})...")
            
            if mega_verbose:
                SLog.log(f"[{worker.name}] Feedback отправляемый воркеру:")
                SLog.log("-" * 40)
                SLog.log(feedback)
                SLog.log("-" * 40)
            
            output = worker.run_with_feedback(feedback)
            
            if verbose:
                SLog.log(f"[{worker.name}] Получен исправленный ответ")
            
            if mega_verbose:
                SLog.log(f"[{worker.name}] Исправленный ответ LLM:")
                SLog.log("-" * 40)
                last_assistant_msg = next((m for m in reversed(worker.history) if m.role == "assistant"), None)
                if last_assistant_msg:
                    SLog.log(last_assistant_msg.content[:1500] + "..." if len(last_assistant_msg.content) > 1500 else last_assistant_msg.content)
                SLog.log("-" * 40)
    
    if verbose:
        SLog.log(f"[{worker.name}] ⚠ Достигнут лимит итераций ({max_iterations})")
    
    return output, False