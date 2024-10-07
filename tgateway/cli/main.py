import asyncio
import json
from typing import Optional

import typer
from pydantic_core import to_jsonable_python

from tgateway import TelegramGateway
from tgateway.__about__ import __version__
from tgateway.methods import (
    CheckSendAbilityMethod,
    CheckVerificationStatus,
    RevokeVerificationMessage,
    SendVerificationMessage,
    TelegramGatewayMethod,
)
from tgateway.types import (
    TelegramGatewayResult,
    TelegramGatewayResultT,
)

cli = typer.Typer(pretty_exceptions_short=True)


def version_callback(version: bool) -> None:
    """Callback function for displaying version information."""
    if version:
        import platform

        typer.echo(
            f"Running TGateway {__version__} with {platform.python_implementation()} "
            f"{platform.python_version()} on {platform.system()}",
        )

        raise typer.Exit()


@cli.callback()
def main(
    version: Optional[bool] = typer.Option(
        False,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show current platform, python and TGateway version.",
    ),
) -> None:
    pass


@cli.command(name="send")
def send_verification_message(
    access_token: str = typer.Option(
        help="Telegram Gateway API access token. You can get it from https://gateway.telegram.org/account/api.",
    ),
    phone_number: str = typer.Option(
        help="The phone number to which you want to send a verification message, in the E.164 format."
    ),
    request_id: Optional[str] = typer.Option(
        default=None,
        help="The unique identifier of a previous request from checkSendAbility. If provided, this request will be free of charge.",
    ),
    sender_username: Optional[str] = typer.Option(
        default=None,
        help="Username of the Telegram channel from which the code will be sent. The specified channel, if any, must be verified and owned by the same account who owns the Telegram Gateway API token.",
    ),
    code: Optional[str] = typer.Option(
        default=None,
        help="The verification code. Use this parameter if you want to set the verification code yourself. Only fully numeric strings between 4 and 8 characters in length are supported. If this parameter is set, code_length is ignored.",
    ),
    code_length: Optional[int] = typer.Option(
        default=None,
        help="The length of the verification code if Telegram needs to generate it for you. Supported values are from 4 to 8. This is only relevant if you are not using the code parameter to set your own code. Use the checkVerificationStatus method with the code parameter to verify the code entered by the user.",
    ),
    callback_url: Optional[str] = typer.Option(
        default=None,
        help="A URL where you want to receive delivery reports related to the sent message.",
    ),
    payload: Optional[str] = typer.Option(
        default=None,
        help="Custom payload, 0-128 bytes. This will not be displayed to the user, use it for your internal processes.",
    ),
    ttl: Optional[int] = typer.Option(
        default=None,
        help="Time-to-live (in seconds) before the message expires and is deleted. The message will not be deleted if it has already been read. If not specified, the message will not be deleted.",
    ),
) -> None:
    emit_telegram_gateway_method(
        access_token=access_token,
        method=SendVerificationMessage(
            phone_number=phone_number,
            request_id=request_id,
            sender_username=sender_username,
            code=code,
            code_length=code_length,
            callback_url=callback_url,
            payload=payload,
            ttl=ttl,
        ),
    )


@cli.command(name="ability")
def check_send_ability(
    access_token: str = typer.Option(
        help="Telegram Gateway API access token. You can get it from https://gateway.telegram.org/account/api.",
    ),
    phone_number: str = typer.Option(
        help="The phone number for which you want to check our ability to send a verification message, in the E.164 format."
    ),
) -> None:
    emit_telegram_gateway_method(
        access_token=access_token,
        method=CheckSendAbilityMethod(
            phone_number=phone_number,
        ),
    )


@cli.command(name="check")
def check_verification_status(
    access_token: str = typer.Option(
        help="Telegram Gateway API access token. You can get it from https://gateway.telegram.org/account/api.",
    ),
    request_id: str = typer.Option(
        help="The unique identifier of the verification request whose status you want to check."
    ),
    code: Optional[str] = typer.Option(
        default=None,
        help="The code entered by the user. If provided, the method checks if the code is valid for the relevant request.",
    ),
) -> None:
    emit_telegram_gateway_method(
        access_token=access_token,
        method=CheckVerificationStatus(
            request_id=request_id,
            code=code,
        ),
    )


@cli.command(name="revoke")
def revoke_verification_message(
    access_token: str = typer.Option(
        help="Telegram Gateway API access token. You can get it from https://gateway.telegram.org/account/api.",
    ),
    request_id: str = typer.Option(
        help="The unique identifier of the request whose verification message you want to revoke."
    ),
) -> None:
    emit_telegram_gateway_method(
        access_token=access_token,
        method=RevokeVerificationMessage(
            request_id=request_id,
        ),
    )


def emit_telegram_gateway_method(
    access_token: str, method: TelegramGatewayMethod[TelegramGatewayResultT]
) -> None:
    result = asyncio.run(
        _emit_telegram_gateway_method(
            access_token=access_token,
            method=method,
        )
    )

    content = to_jsonable_python(result)
    typer.echo(
        json.dumps(
            content,
            indent=4,
        )
    )


async def _emit_telegram_gateway_method(
    access_token: str,
    method: TelegramGatewayMethod[TelegramGatewayResultT],
) -> TelegramGatewayResult[TelegramGatewayResultT]:
    async with TelegramGateway(access_token=access_token) as gateway:
        return await gateway.make_request_raw(method)


if __name__ == "__main__":
    cli()
