from typing import Final, Literal

from tgateway.constants import (
    CODE_LENGTH_MAX,
    CODE_LENGTH_MIN,
)


class TelegramGatewayError(Exception):
    pass


class ValidationCodeLengthError(TelegramGatewayError):
    def __init__(self, field_name: Literal["code", "code_length"]):
        super().__init__(
            f"{field_name} length must be between {CODE_LENGTH_MIN} and {CODE_LENGTH_MAX} characters",
        )


class TelegramGatewayAPIError(TelegramGatewayError):
    def __init__(self, error_code: str, endpoint: str):
        self.error_code = error_code
        self.endpoint = endpoint

    def __str__(self) -> str:
        return f"Telegram Gateway error at {self.endpoint}: {self.error_code}"


class AccessTokenInvalidError(TelegramGatewayAPIError):
    pass


class AccessTokenRequiredError(TelegramGatewayAPIError):
    pass


class BalanceNotEnoughError(TelegramGatewayAPIError):
    pass


class CallbackUrlInvalidError(TelegramGatewayAPIError):
    pass


class CodeInvalidError(TelegramGatewayAPIError):
    pass


class CodeLengthInvalidError(TelegramGatewayAPIError):
    pass


class CodeLengthRequiredError(TelegramGatewayAPIError):
    pass


class PayloadInvalidError(TelegramGatewayAPIError):
    pass


class PhoneNumberInvalidError(TelegramGatewayAPIError):
    pass


class PhoneNumberNotFoundError(TelegramGatewayAPIError):
    pass


class RequestIdInvalidError(TelegramGatewayAPIError):
    pass


class RequestIdRequiredError(TelegramGatewayAPIError):
    pass


class SenderNotOwnedError(TelegramGatewayAPIError):
    pass


class SenderNotVerifiedError(TelegramGatewayAPIError):
    pass


class SenderUsernameInvalidError(TelegramGatewayAPIError):
    pass


class TtlInvalidError(TelegramGatewayAPIError):
    pass


class UnknownMethodError(TelegramGatewayAPIError):
    pass


class FloodWaitError(TelegramGatewayAPIError):
    def __init__(self, error_code: str, endpoint: str, value: int = 0):
        super().__init__(error_code, endpoint)
        self.value = value


api_error_code_to_exception: Final[dict[str, type[TelegramGatewayAPIError]]] = {
    "ACCESS_TOKEN_INVALID": AccessTokenInvalidError,
    "ACCESS_TOKEN_REQUIRED": AccessTokenRequiredError,
    "BALANCE_NOT_ENOUGH": BalanceNotEnoughError,
    "CALLBACK_URL_INVALID": CallbackUrlInvalidError,
    "CODE_INVALID": CodeInvalidError,
    "CODE_LENGTH_INVALID": CodeLengthInvalidError,
    "CODE_LENGTH_REQUIRED": CodeLengthRequiredError,
    "PAYLOAD_INVALID": PayloadInvalidError,
    "PHONE_NUMBER_INVALID": PhoneNumberInvalidError,
    "PHONE_NUMBER_NOT_FOUND": PhoneNumberNotFoundError,
    "REQUEST_ID_INVALID": RequestIdInvalidError,
    "REQUEST_ID_REQUIRED": RequestIdRequiredError,
    "SENDER_NOT_OWNED": SenderNotOwnedError,
    "SENDER_NOT_VERIFIED": SenderNotVerifiedError,
    "SENDER_USERNAME_INVALID": SenderUsernameInvalidError,
    "TTL_INVALID": TtlInvalidError,
    "UNKNOWN_METHOD": UnknownMethodError,
    "FLOOD_WAIT_%d": FloodWaitError,
}


def validate_telegram_gateway_api_error(
    error_code: str,
    endpoint: str,
) -> TelegramGatewayAPIError:
    if error_code.startswith("FLOOD_WAIT_"):
        return FloodWaitError(
            error_code=error_code,
            endpoint=endpoint,
            value=int(error_code.removeprefix("FLOOD_WAIT_")),
        )

    subclass = api_error_code_to_exception.get(error_code, TelegramGatewayAPIError)
    return subclass(error_code=error_code, endpoint=endpoint)
