from colorama import init, Fore

init()


def with_color(msg, color):
    return "{}{}{}".format(color, msg, Fore.RESET)


class ConflictingLoginOptionsError(Exception):
    pass


def decide_download_without_login(args, etc_config) -> bool:
    """Decide whether downloads should be performed without login.

    Priority: CLI flags > config file > default (without login).
    Raises ConflictingLoginOptionsError when contradictory options
    are specified at the same level.
    """
    if args.with_login and args.without_login:
        raise ConflictingLoginOptionsError(
            "--with-login and --without-login cannot be used together.")
    if args.with_login:
        return False
    if args.without_login:
        return True
    if etc_config.download_with_login and etc_config.download_without_login:
        raise ConflictingLoginOptionsError(
            "download_with_login and download_without_login cannot "
            "both be true in the config file.")
    if etc_config.download_with_login:
        return False
    return True
