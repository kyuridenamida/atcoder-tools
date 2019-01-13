from colorama import Fore


def with_color(msg, color):
    return "{}{}{}".format(color, msg, Fore.RESET)
