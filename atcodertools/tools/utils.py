from colorama import init, Fore

init()


def with_color(msg, color):
    return "{}{}{}".format(color, msg, Fore.RESET)
