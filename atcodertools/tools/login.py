#!/usr/bin/python3
import argparse
import os
import sys
from http.cookiejar import Cookie

from atcodertools.client.atcoder import (
    AtCoderClient,
    LoginError,
    default_cookie_supplier,
    save_cookie,
)
from atcodertools.common.logging import logger

REVEL_SESSION_ENV_VAR = "ATCODER_REVEL_SESSION"


def _cookie_from_value(cookie_value: str) -> Cookie:
    return Cookie(
        version=0,
        name='REVEL_SESSION',
        value=cookie_value,
        port=None,
        port_specified=False,
        domain='atcoder.jp',
        domain_specified=True,
        domain_initial_dot=False,
        path='/',
        path_specified=True,
        secure=True,
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False
    )


def main(prog, args, client=None) -> bool:
    parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--cookie",
                        help="REVEL_SESSION cookie value\n"
                             "[Default] ${} environment variable, "
                             "or interactive prompt".format(REVEL_SESSION_ENV_VAR),
                        type=str,
                        default=None)

    args = parser.parse_args(args)

    cookie_value = args.cookie or os.environ.get(REVEL_SESSION_ENV_VAR)

    if client is None:
        client = AtCoderClient()

    if cookie_value is not None:
        try:
            client.login(
                cookie_supplier=lambda: _cookie_from_value(cookie_value),
                use_local_session_cache=False,
                save_session_cache=False)
        except LoginError as e:
            logger.error(e)
            return False
        save_cookie(client._session)
    else:
        try:
            client.login(save_session_cache=True)
        except LoginError as e:
            logger.error(e)
            return False

    logger.info("Login successful. Session cache is saved.")
    return True


if __name__ == "__main__":
    main(sys.argv[0], sys.argv[1:])
