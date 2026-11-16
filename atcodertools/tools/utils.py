from colorama import init, Fore

init()


def with_color(msg: str, color: str) -> str:
    return "{}{}{}".format(color, msg, Fore.RESET)
