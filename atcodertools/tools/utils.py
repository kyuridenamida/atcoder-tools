from colorama import Fore, init

init()


def with_color(msg: str, color: str) -> str:
    return f"{color}{msg}{Fore.RESET}"
