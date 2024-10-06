from decimal import Decimal
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Optional,
    TypeVar,
)

from pydantic import (
    BaseModel,
    PrivateAttr,
)
from typing_extensions import Self

from tgateway.enums import (
    DeliveryStatusEnum,
    VerificationStatusEnum,
)

if TYPE_CHECKING:
    from tgateway.client import TelegramGateway
    from tgateway.methods import (
        CheckVerificationStatus,
        RevokeVerificationMessage,
        SendVerificationMessage,
    )


TelegramGatewayResultT = TypeVar("TelegramGatewayResultT")


class TelegramGatewayResult(BaseModel, Generic[TelegramGatewayResultT]):
    ok: bool
    error: Optional[str] = None
    result: Optional[TelegramGatewayResultT] = None


class TelegramGatewayContextMixin(BaseModel):
    _client: Optional["TelegramGateway"] = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        self._client = __context.get("client") if __context else None

    def as_(self, client: Optional["TelegramGateway"]) -> Self:
        """Bind object to a TelegramGateway instance.

        :param client: TelegramGateway instance
        :return: self
        """
        self._client = client
        return self

    @property
    def client(self) -> Optional["TelegramGateway"]:
        """Get client instance.

        :return: TelegramGateway instance
        """
        return self._client


class DeliveryStatus(BaseModel):
    """This object represents the delivery status of a message.

    Source: https://core.telegram.org/gateway/api#deliverystatus
    """

    status: DeliveryStatusEnum
    """The current status of the message."""
    updated_at: int
    """The timestamp when the status was last updated."""


class VerificationStatus(BaseModel):
    """This object represents the verification status of a code.

    Source: https://core.telegram.org/gateway/api#verificationstatus
    """

    status: VerificationStatusEnum
    """The current status of the verification process."""
    updated_at: int
    """The timestamp for this particular status. Represents the time when the status was last updated."""
    code_entered: Optional[str] = None
    """Optional. The code entered by the user."""


class RequestStatus(TelegramGatewayContextMixin, BaseModel):
    """This object represents the status of a verification message request.

    Source: https://core.telegram.org/gateway/api#requeststatus
    """

    request_id: str
    """Unique identifier of the verification request."""
    phone_number: str
    """The phone number to which the verification code was sent, in the E.164 format."""
    request_cost: Decimal
    """Total request cost incurred by either checkSendAbility or sendVerificationMessage."""
    remaining_balance: Optional[Decimal] = None
    """Optional. Remaining balance in credits. Returned only in response to a request that incurs a charge."""
    delivery_status: Optional[DeliveryStatus] = None
    """Optional. The current message delivery status. Returned only if a verification message was sent to the user."""
    verification_status: Optional[VerificationStatus] = None
    """Optional. The current status of the verification process."""
    payload: Optional[str] = None
    """Optional. Custom payload if it was provided in the request, 0-256 bytes."""

    def send(
        self,
        sender_username: Optional[str] = None,
        code: Optional[str] = None,
        code_length: Optional[int] = None,
        callback_url: Optional[str] = None,
        payload: Optional[str] = None,
        ttl: Optional[int] = None,
    ) -> "SendVerificationMessage":
        from tgateway.methods import SendVerificationMessage

        if self.delivery_status is not None:
            raise ValueError("This request is already delivered")

        return SendVerificationMessage(
            phone_number=self.phone_number,
            request_id=self.request_id,
            sender_username=sender_username,
            code=code,
            code_length=code_length,
            callback_url=callback_url,
            payload=payload,
            ttl=ttl,
        ).as_(self._client)

    def check(
        self,
        code: Optional[str] = None,
    ) -> "CheckVerificationStatus":
        from tgateway.methods import CheckVerificationStatus

        return CheckVerificationStatus(
            request_id=self.request_id,
            code=code,
        ).as_(self._client)

    def revoke(self) -> "RevokeVerificationMessage":
        from tgateway.methods import RevokeVerificationMessage

        if self.delivery_status is None:
            raise ValueError("This request is not delivered")

        if self.delivery_status.status == "revoked":
            raise ValueError("This request is already revoked")

        return RevokeVerificationMessage(
            request_id=self.request_id,
        ).as_(self._client)
