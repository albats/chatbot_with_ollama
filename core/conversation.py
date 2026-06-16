from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List

from chatbot_with_ollama.experts.expert_prompts import DEFAULT_EXPERT, EXPERT_LABELS, EXPERT_PROMPTS

Message = Dict[str, str]


@dataclass
class ConversationManager:
    active_expert: str = DEFAULT_EXPERT
    histories: Dict[str, List[Message]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._initialize_histories()
        if self.active_expert not in EXPERT_PROMPTS:
            self.active_expert = DEFAULT_EXPERT

    def _initialize_histories(self) -> None:
        for expert_key, prompt in EXPERT_PROMPTS.items():
            if expert_key not in self.histories:
                self.histories[expert_key] = [self._system_message(prompt)]

    @staticmethod
    def _system_message(prompt: str) -> Message:
        return {"role": "system", "content": prompt}

    def list_experts(self) -> Dict[str, str]:
        return dict(EXPERT_LABELS)

    def get_active_expert_key(self) -> str:
        return self.active_expert

    def get_active_expert_label(self) -> str:
        return EXPERT_LABELS[self.active_expert]

    def switch_expert(self, expert_key: str, reset_history: bool = False) -> str:
        self._validate_expert(expert_key)
        self.active_expert = expert_key
        if reset_history:
            self.reset_current_expert()
        return self.get_active_expert_label()

    def add_user_message(self, content: str) -> None:
        self._append_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        self._append_message("assistant", content)

    def _append_message(self, role: str, content: str) -> None:
        clean_content = content.strip()
        if clean_content:
            self.histories[self.active_expert].append({"role": role, "content": clean_content})

    def get_messages(self) -> List[Message]:
        return deepcopy(self.histories[self.active_expert])

    def reset_current_expert(self) -> None:
        prompt = EXPERT_PROMPTS[self.active_expert]
        self.histories[self.active_expert] = [self._system_message(prompt)]

    def reset_all(self) -> None:
        self.histories = {
            expert_key: [self._system_message(prompt)]
            for expert_key, prompt in EXPERT_PROMPTS.items()
        }

    def count_visible_messages(self, expert_key: str | None = None) -> int:
        key = expert_key or self.active_expert
        self._validate_expert(key)
        messages_without_system = [
            message for message in self.histories[key]
            if message.get("role") != "system"
        ]
        return len(messages_without_system)

    def _validate_expert(self, expert_key: str) -> None:
        if expert_key not in EXPERT_PROMPTS:
            available = ", ".join(EXPERT_PROMPTS.keys())
            raise ValueError(f"Experto no válido: {expert_key}. Opciones disponibles: {available}")
