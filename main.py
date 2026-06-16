from __future__ import annotations

import shutil
import sys
import textwrap
from typing import Callable

from chatbot_with_ollama.core.chatbot import (
    DEFAULT_MODEL,
    OllamaConnectionError,
    OllamaGenerationError,
    OllamaModelNotAvailableError,
    ThematicChatbot,
)
from chatbot_with_ollama.core.conversation import ConversationManager

COMMANDS = {
    "/experto": "cambiar de experto",
    "/reiniciar": "reiniciar el historial del experto activo",
    "/reiniciar_todo": "reiniciar el historial de todos los expertos",
    "/estado": "ver experto activo e historial",
    "/ayuda": "mostrar opciones disponibles",
    "/salir": "finalizar la aplicación",
}


def main() -> None:
    print_header()
    conversation = ConversationManager()

    try:
        chatbot = ThematicChatbot(model=DEFAULT_MODEL)
        print("Comprobando conexión local con Ollama...")
        chatbot.ensure_ready()
    except OllamaConnectionError as exc:
        print_error(str(exc))
        sys.exit(1)
    except OllamaModelNotAvailableError as exc:
        print_error(str(exc))
        sys.exit(1)

    print_success(f"Sistema listo. Modelo local activo: {DEFAULT_MODEL}")
    select_initial_expert(conversation)
    print_help()
    run_chat_loop(chatbot, conversation)


def print_header() -> None:
    line = "=" * 72
    print(line)
    print("Chatbot de Expertos Temáticos con Ollama SDK y gemma3:1b")
    print("Funcionamiento local y offline mediante el servicio Ollama del equipo")
    print(line)


def print_success(message: str) -> None:
    print(f"[OK] {message}")


def print_error(message: str) -> None:
    print(f"[ERROR] {message}")


def print_info(message: str) -> None:
    print(f"[INFO] {message}")


def select_initial_expert(conversation: ConversationManager) -> None:
    print("\nSelecciona el experto inicial:")
    expert_key = ask_expert_key(conversation)
    conversation.switch_expert(expert_key, reset_history=False)
    print_success(f"Experto activo: {conversation.get_active_expert_label()}")


def ask_expert_key(conversation: ConversationManager) -> str:
    experts = list(conversation.list_experts().items())
    while True:
        for index, (_, label) in enumerate(experts, start=1):
            print(f"  {index}. {label}")
        choice = input("Opción: ").strip()
        if choice.isdigit():
            selected_index = int(choice)
            if 1 <= selected_index <= len(experts):
                return experts[selected_index - 1][0]
        matching_key = normalize_expert_alias(choice)
        if matching_key in conversation.list_experts():
            return matching_key
        print_error("Opción no válida. Elige 1, 2, 3 o escribe el nombre del experto.")


def normalize_expert_alias(value: str) -> str:
    normalized = value.strip().lower()
    aliases = {
        "1": "programacion",
        "programación": "programacion",
        "programacion": "programacion",
        "software": "programacion",
        "2": "marketing",
        "mercadeo": "marketing",
        "marketing": "marketing",
        "3": "legal",
        "juridico": "legal",
        "jurídico": "legal",
        "juridico-legal": "legal",
        "jurídico-legal": "legal",
        "legal": "legal",
    }
    return aliases.get(normalized, normalized)


def print_help() -> None:
    print("\nOpciones disponibles durante la conversación:")
    for command, description in COMMANDS.items():
        print(f"  {command:<16} {description}")


def run_chat_loop(chatbot: ThematicChatbot, conversation: ConversationManager) -> None:
    while True:
        show_prompt_context(conversation)
        user_input = input("Tú: ").strip()

        if not user_input:
            print_info("Escribe un mensaje o usa /ayuda para ver las opciones.")
            continue

        if user_input.startswith("/"):
            should_continue = handle_command(user_input, conversation)
            if not should_continue:
                break
            continue

        conversation.add_user_message(user_input)
        try:
            response = chatbot.generate_response(conversation.get_messages())
        except OllamaGenerationError as exc:
            print_error(str(exc))
            continue

        conversation.add_assistant_message(response)
        print_wrapped_response(conversation.get_active_expert_label(), response)


def show_prompt_context(conversation: ConversationManager) -> None:
    active_expert = conversation.get_active_expert_label()
    visible_messages = conversation.count_visible_messages()
    print(f"\n[{active_expert}] Historial: {visible_messages} mensajes. Comando: /ayuda")


def handle_command(command: str, conversation: ConversationManager) -> bool:
    normalized = command.strip().lower()
    handlers: dict[str, Callable[[ConversationManager], bool]] = {
        "/experto": change_expert,
        "/reiniciar": reset_current_expert,
        "/reiniciar_todo": reset_all_experts,
        "/estado": show_state,
        "/ayuda": show_help_command,
        "/salir": exit_chat,
    }
    handler = handlers.get(normalized)
    if handler is None:
        print_error("Comando no reconocido. Usa /ayuda para ver las opciones disponibles.")
        return True
    return handler(conversation)


def change_expert(conversation: ConversationManager) -> bool:
    print("\nSelecciona el nuevo experto:")
    expert_key = ask_expert_key(conversation)
    keep_history = ask_yes_no("¿Mantener el historial existente de ese experto?", default=True)
    conversation.switch_expert(expert_key, reset_history=not keep_history)
    status = "historial conservado" if keep_history else "historial reiniciado"
    print_success(f"Experto activo: {conversation.get_active_expert_label()} ({status}).")
    return True


def ask_yes_no(question: str, default: bool = True) -> bool:
    suffix = "S/n" if default else "s/N"
    answer = input(f"{question} [{suffix}]: ").strip().lower()
    if not answer:
        return default
    return answer in {"s", "si", "sí", "y", "yes"}


def reset_current_expert(conversation: ConversationManager) -> bool:
    conversation.reset_current_expert()
    print_success(f"Historial reiniciado para {conversation.get_active_expert_label()}.")
    return True


def reset_all_experts(conversation: ConversationManager) -> bool:
    conversation.reset_all()
    print_success("Historial reiniciado para todos los expertos.")
    return True


def show_state(conversation: ConversationManager) -> bool:
    print("\nEstado de la conversación:")
    print(f"  Experto activo: {conversation.get_active_expert_label()}")
    for expert_key, label in conversation.list_experts().items():
        print(f"  {label}: {conversation.count_visible_messages(expert_key)} mensajes de historial")
    return True


def show_help_command(conversation: ConversationManager) -> bool:
    print_help()
    print(f"\nExperto activo: {conversation.get_active_expert_label()}")
    return True


def exit_chat(conversation: ConversationManager) -> bool:
    print_success("Conversación finalizada.")
    return False


def print_wrapped_response(expert_label: str, response: str) -> None:
    terminal_width = shutil.get_terminal_size((88, 20)).columns
    width = max(60, min(terminal_width, 100))
    print(f"\n{expert_label}:")
    for paragraph in response.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            print()
            continue
        print(textwrap.fill(paragraph, width=width, replace_whitespace=False))


if __name__ == "__main__":
    main()
