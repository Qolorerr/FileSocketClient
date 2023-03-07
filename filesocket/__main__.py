import logging
import socket
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Tuple
import requests

from .config import PATH, SIGN_UP_PATH, GET_TOKEN_PATH, SHOW_ALL_PC_PATH, DEVICE_TYPE, store_keeper
from .exceptions import ServerError, TokenRequired


logger = logging.getLogger("app")


def _on_server_error(error: Exception) -> None:
    logger.info(f"Server error {error.args}")
    print(f"Server error {error.args}\n")
    sys.exit()


def sign_up(login: str, email: str, password: str) -> None:
    json = {"login": login, "email": email, "password": password}
    try:
        response = requests.post(f'http://{PATH}{SIGN_UP_PATH}', json=json)
    except Exception as e:
        raise ServerError(e)
    if response.status_code == 201:
        get_token(login, password)
    else:
        message = response.headers['message'] if 'message' in response.headers else ''
        raise ServerError(f"{response.status_code} {message}")


def sign_up_ui(args: Namespace) -> None:
    try:
        sign_up(args.login, args.email, args.password)
        print("Signed up successfully")
    except ServerError as e:
        _on_server_error(e)


def sign_in(login: str, password: str) -> None:
    get_token(login, password)


def sign_in_ui(args: Namespace) -> None:
    try:
        sign_in(args.login, args.password)
        print("Signed in successfully")
    except ServerError as e:
        _on_server_error(e)


def get_token(login: str, password: str) -> None:
    pc_name = socket.gethostname()
    json = {"login_or_email": login, "password": password, "name": pc_name, "type": DEVICE_TYPE}
    try:
        response = requests.get(f'http://{PATH}{GET_TOKEN_PATH}', json=json)
    except Exception as e:
        raise ServerError(e)
    if response.status_code == 201 and 'token' in response.json():
        store_keeper.add_token(response.json()['token'])
    else:
        message = response.headers['message'] if 'message' in response.headers else ''
        raise ServerError(f"{response.status_code} {message}")


def get_token_ui(args: Namespace) -> None:
    try:
        get_token(args.login, args.password)
        print("Got new token")
    except ServerError as e:
        _on_server_error(e)


@dataclass
class PCEntity:
    id: int
    name: str


def show_all_pc() -> Tuple[PCEntity]:
    token = store_keeper.get_token()
    if token is None:
        raise TokenRequired()
    json = {"token": token}
    try:
        response = requests.get(f'http://{PATH}{SHOW_ALL_PC_PATH}', json=json)
    except Exception as e:
        raise ServerError(e)
    json = response.json()
    if response.status_code == 200 and 'devices' in json:
        return tuple(PCEntity(device['id'], device['name']) for device in json['devices'])
    else:
        message = response.headers['message'] if 'message' in response.headers else ''
        raise ServerError(f"{response.status_code} {message}")


def show_all_pc_ui(args: Namespace | None = None) -> None:
    try:
        pc_entities = show_all_pc()
        logger.debug(f"Got new list of pc")
        print("Your PCs:")
        for device in pc_entities:
            print(f"{device.id}\t{device.name}")
    except (ServerError, TokenRequired) as e:
        _on_server_error(e)


def run(args: Namespace) -> None:
    if args.manage is None:
        from .managed_device_client import ManagedClient
        client = ManagedClient(require_token=args.token)
    else:
        from .managing_device_client import ManagingClient
        client = ManagingClient(str(args.manage), device_secure_token=args.token)
    try:
        client.run()
    except TokenRequired as e:
        print(e)


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    subparsers = arg_parser.add_subparsers(help='Methods')

    if not store_keeper.get_token():
        sign_up_parser = subparsers.add_parser('sign_up', help='Create new account')
        sign_up_parser.add_argument('-login', type=str, help='Your unique name', required=True)
        sign_up_parser.add_argument('-email', type=str, help='Your email', required=True)
        sign_up_parser.add_argument('-password', type=str, help='Your password', required=True)
        sign_up_parser.set_defaults(func=sign_up_ui)

        sign_in_parser = subparsers.add_parser('sign_in', help='Sign in')
        sign_in_parser.add_argument('-login', type=str, help='Your login or email', required=True)
        sign_in_parser.add_argument('-password', type=str, help='Your password', required=True)
        sign_in_parser.set_defaults(func=sign_in_ui)
    else:
        run_parser = subparsers.add_parser('run', help="Run filesocket client")
        run_parser.add_argument('-manage', type=int, help='Id of managing device')
        run_parser.add_argument('-token', type=str, help='Secure token')
        run_parser.set_defaults(func=run)

        show_all_pc_parser = subparsers.add_parser('show_pc', help="Show your PCs (For managing device)")
        show_all_pc_parser.set_defaults(func=show_all_pc_ui)

    arguments = arg_parser.parse_args()
    try:
        arguments.func(arguments)
    except AttributeError:
        print("Use filesocket -h\n")
