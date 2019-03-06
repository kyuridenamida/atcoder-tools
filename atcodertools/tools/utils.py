from colorama import init, Fore

init(convert=True)


def with_color(msg, color):
    return "{}{}{}".format(color, msg, Fore.RESET)
