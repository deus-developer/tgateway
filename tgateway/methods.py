from collections.abc import Generator
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Optional,
)

from pydantic import (
    BaseModel,
    model_validator,
)
from typing_extensions import Self

from tgateway.constants import (
    CODE_LENGTH_MAX,
    CODE_LENGTH_MIN,
    PAYLOAD_LENGTH_MAX,
    PAYLOAD_LENGTH_MIN,
    TTL_MAX,
    TTL_MIN,
)
from tgateway.exceptions import ValidationCodeLengthError
from tgateway.types import (
    RequestStatus,
    TelegramGatewayContextMixin,
    TelegramGatewayResultT,
)

if TYPE_CHECKING:
    from tgateway.client import TelegramGateway


class TelegramGatewayMethod(
    TelegramGatewayContextMixin, BaseModel, Generic[TelegramGatewayResultT]
):
    __returning__: ClassVar[type]
    __api_method__: ClassVar[str]

    async def emit(self, client: "TelegramGateway") -> TelegramGatewayResultT:
        return await client.make_request(self)

    def __await__(self) -> Generator[Any, None, TelegramGatewayResultT]:
        if self._client is None:
            raise RuntimeError(
                "This method is not mounted to any TelegramGateway instance, please call it explicitly "
                "with TelegramGateway instance `await client.make_request(method)`\n"
                "or mount method to a TelegramGateway instance `method.as_(client)` "
                "and then call it `await method()`",
            )

        return self.emit(self._client).__await__()


class SendVerificationMessage(TelegramGatewayMethod[RequestStatus]):
    """Use this method to send a verification message.

    Charges will apply according to the pricing plan for each successful message delivery.
    Note that this method is always free of charge when used to send codes to your own phone number.
    On success, returns a RequestStatus object.

    Source: https://core.telegram.org/gateway/api#sendverificationmessage
    """

    __returning__ = RequestStatus
    __api_method__ = "sendVerificationMessage"

    phone_number: str
    """The phone number to which you want to send a verification message, in the E.164 format."""
    request_id: Optional[str] = None
    """The unique identifier of a previous request from checkSendAbility. If provided, this request will be free of charge."""
    sender_username: Optional[str] = None
    """Username of the Telegram channel from which the code will be sent. The specified channel, if any, must be verified and owned by the same account who owns the Gateway API token."""
    code: Optional[str] = None
    """The verification code. Use this parameter if you want to set the verification code yourself. Only fully numeric strings between 4 and 8 characters in length are supported. If this parameter is set, code_length is ignored."""
    code_length: Optional[int] = None
    """The length of the verification code if Telegram needs to generate it for you. Supported values are from 4 to 8. This is only relevant if you are not using the code parameter to set your own code. Use the checkVerificationStatus method with the code parameter to verify the code entered by the user."""
    callback_url: Optional[str] = None
    """A URL where you want to receive delivery reports related to the sent message."""
    payload: Optional[str] = None
    """Custom payload, 0-128 bytes. This will not be displayed to the user, use it for your internal processes."""
    ttl: Optional[int] = None
    """Time-to-live (in seconds) before the message expires and is deleted. The message will not be deleted if it has already been read. If not specified, the message will not be deleted."""

    @model_validator(mode="after")
    def _validator(self) -> Self:
        if self.code is not None:
            if not (CODE_LENGTH_MIN <= len(self.code) <= CODE_LENGTH_MAX):
                raise ValidationCodeLengthError(field_name="code")
        elif self.code_length is not None:
            if not (CODE_LENGTH_MIN <= self.code_length <= CODE_LENGTH_MAX):
                raise ValidationCodeLengthError(field_name="code_length")
        else:
            raise ValueError("code or code_length must be specified")

        if not (self.callback_url is None or self.callback_url.startswith("https")):
            raise ValueError("callback_url must be an https url")

        if not (
            self.payload is None
            or PAYLOAD_LENGTH_MIN <= len(self.payload) <= PAYLOAD_LENGTH_MAX
        ):
            raise ValueError("payload must be less than 128 bytes")

        if not (self.ttl is None or TTL_MIN <= self.ttl <= TTL_MAX):
            raise ValueError("ttl must be less than 86400 seconds")

        return self


class CheckSendAbilityMethod(TelegramGatewayMethod[RequestStatus]):
    """Use this method to check the ability to send a verification message to the specified phone number.

    If the ability to send is confirmed, a fee will apply according to the pricing plan.
    After checking, you can send a verification message using the sendVerificationMessage method, providing the request_id from this response.
    Within the scope of a request_id, only one fee can be charged.
    Calling sendVerificationMessage once with the returned request_id will be free of charge, while repeated calls will result in an error.
    Conversely, calls that don't include a request_id will spawn new requests and incur the respective fees accordingly.
    Note that this method is always free of charge when used to send codes to your own phone number.
    In case the message can be sent, returns a RequestStatus object.
    Otherwise, an appropriate error will be returned.

    Source: https://core.telegram.org/gateway/api#checksendability
    """

    __returning__ = RequestStatus
    __api_method__ = "checkSendAbility"

    phone_number: str
    """The phone number for which you want to check our ability to send a verification message, in the E.164 format."""


class CheckVerificationStatus(TelegramGatewayMethod[RequestStatus]):
    """Use this method to check the status of a verification message that was sent previously.

    If the code was generated by Telegram for you, you can also verify the correctness of the code entered by the user using this method.
    Even if you set the code yourself, it is recommended to call this method after the user has successfully entered the code, passing the correct code in the code parameter, so that we can track the conversion rate of your verifications.
    On success, returns a RequestStatus object.

    Source: https://core.telegram.org/gateway/api#checkverificationstatus
    """

    __returning__ = RequestStatus
    __api_method__ = "checkVerificationStatus"

    request_id: str
    """The unique identifier of the verification request whose status you want to check."""
    code: Optional[str] = None
    """The code entered by the user. If provided, the method checks if the code is valid for the relevant request."""

    @model_validator(mode="after")
    def _validator(self) -> Self:
        if not (
            self.code is None or CODE_LENGTH_MIN <= len(self.code) <= CODE_LENGTH_MAX
        ):
            raise ValidationCodeLengthError(field_name="code")

        return self


class RevokeVerificationMessage(TelegramGatewayMethod[bool]):
    """Use this method to revoke a verification message that was sent previously.

    Returns True if the revocation request was received.
    However, this does not guarantee that the message will be deleted.
    For example, it will not be removed if the recipient has already read it.

    Source: https://core.telegram.org/gateway/api#revokeverificationmessage
    """

    __returning__ = bool
    __api_method__ = "revokeVerificationMessage"

    request_id: str
    """The unique identifier of the request whose verification message you want to revoke."""
