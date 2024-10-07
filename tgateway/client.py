import datetime
from types import TracebackType
from typing import (
    Optional,
    Union,
    cast,
)

from aiohttp import (
    ClientSession,
)

from tgateway.exceptions import (
    validate_telegram_gateway_api_error,
)
from tgateway.integrity import validate_report_integrity
from tgateway.methods import (
    CheckSendAbilityMethod,
    CheckVerificationStatus,
    RevokeVerificationMessage,
    SendVerificationMessage,
    TelegramGatewayMethod,
)
from tgateway.types import (
    RequestStatus,
    TelegramGatewayResult,
    TelegramGatewayResultT,
)


class TelegramGateway:
    """A client for interacting with the Telegram Gateway API."""

    def __init__(self, access_token: str) -> None:
        """Initialize the TelegramGateway client with an access token.

        Args:
            access_token (str): The API access token required for authentication.

        Example:
            >>> gateway = TelegramGateway(access_token="<access-token>")
        """
        self._access_token = access_token
        self._session = ClientSession(
            base_url="https://gatewayapi.telegram.org",
            headers={
                "Authorization": f"Bearer {self._access_token}",
            },
        )

    async def make_request_raw(
        self, method: TelegramGatewayMethod[TelegramGatewayResultT]
    ) -> TelegramGatewayResult[TelegramGatewayResultT]:
        """Send a raw request to the Telegram Gateway API using the specified method.

        Args:
            method (TelegramGatewayMethod[TelegramGatewayResultT]):
                An instance of a TelegramGatewayMethod, representing the API method to be executed.
                This instance contains all necessary parameters and settings for the request.

        Returns:
            TelegramGatewayResult[TelegramGatewayResultT]:
                A `TelegramGatewayResult` object containing the result of the API call.
                If the request is successful, it contains the desired result. Otherwise,
                it will include the error details from the API response.

        Example:
            >>> async def main() -> None:
            >>>     async with TelegramGateway(access_token="<access-token>") as gateway:
            >>>         result = await gateway.make_request_raw(SendVerificationMessage(phone_number="+1234567890", code_length=6))
            >>>         print(result.result)  # Access the actual response content
        """
        payload = method.model_dump(
            mode="json",
            by_alias=True,
            exclude_none=True,
        )
        model = TelegramGatewayResult[method.__returning__]

        async with self._session.post(
            url=f"/{method.__api_method__}",
            json=payload,
        ) as response:
            content = await response.read()
            box = model.model_validate_json(content, context={"client": self})
            return box

    async def make_request(
        self, method: TelegramGatewayMethod[TelegramGatewayResultT]
    ) -> TelegramGatewayResultT:
        """Make a request to the Telegram Gateway API.

        Args:
            method (TelegramGatewayMethod[TelegramGatewayResultT]): The method to be executed.

        Returns:
            TelegramGatewayResultT: The result returned by the API method, if successful.

        Raises:
            TelegramGatewayAPIError: If the API returns an error.
        """
        box = await self.make_request_raw(method)
        if box.error is None:
            return cast(TelegramGatewayResultT, box.result)

        raise validate_telegram_gateway_api_error(
            error_code=box.error,
            endpoint=method.__api_method__,
        )

    async def send_verification_message(
        self,
        phone_number: str,
        request_id: Optional[str] = None,
        sender_username: Optional[str] = None,
        code: Optional[str] = None,
        code_length: Optional[int] = None,
        callback_url: Optional[str] = None,
        payload: Optional[str] = None,
        ttl: Optional[Union[int, datetime.timedelta]] = None,
    ) -> RequestStatus:
        """Send a verification message to the specified phone number.

        Args:
            phone_number (str): The target phone number in E.164 format.
            request_id (Optional[str]): Optional. The ID of a previous request.
            sender_username (Optional[str]): Optional. The username of a verified channel to send the message.
            code (Optional[str]): Optional. Custom code to send. If not provided, Telegram generates one.
            code_length (Optional[int]): Optional. Length of the code to generate if code is not provided.
            callback_url (Optional[str]): Optional. HTTPs URL to receive delivery reports.
            payload (Optional[str]): Optional. Custom payload (0-128 bytes) for internal tracking.
            ttl (Optional[Union[int, datetime.timedelta]]): Optional. Time-to-live for the message before expiration.

        Returns:
            RequestStatus: The status of the sent message.

        Raises:
            ValidationCodeLengthError: If the provided code length is invalid.

        Example:
            >>> async def main() -> None:
            >>>     async with TelegramGateway(access_token="<access-token>") as gateway:
            >>>         await gateway.send_verification_message(phone_number="+1234567890", code_length=6)
        """
        method = SendVerificationMessage(
            phone_number=phone_number,
            request_id=request_id,
            sender_username=sender_username,
            code=code,
            code_length=code_length,
            callback_url=callback_url,
            payload=payload,
            ttl=ttl,
        )
        return await self.make_request(method)

    async def check_send_ability(
        self,
        phone_number: str,
    ) -> RequestStatus:
        """Check the ability to send a verification message to a given phone number.

        Args:
            phone_number (str): The target phone number in E.164 format.

        Returns:
            RequestStatus: Status indicating whether sending is possible or not.

        Example:
            >>> async def main() -> None:
            >>>     async with TelegramGateway(access_token="<access-token>") as gateway:
            >>>         await gateway.check_send_ability(phone_number="+1234567890")
        """
        method = CheckSendAbilityMethod(phone_number=phone_number)
        return await self.make_request(method)

    async def check_verification_status(
        self,
        request_id: str,
        code: Optional[str] = None,
    ) -> RequestStatus:
        """Check the status of a previously sent verification message.

        Args:
            request_id (str): The unique identifier of the verification request.
            code (Optional[str]): Optional. The verification code to check its validity.

        Returns:
            RequestStatus: The status of the verification request.

        Raises:
            ValidationCodeLengthError: If the provided code length is invalid.

        Example:
            >>> async def main() -> None:
            >>>     async with TelegramGateway(access_token="<access-token>") as gateway:
            >>>         await gateway.check_verification_status(request_id="abc123", code="1234")
        """
        method = CheckVerificationStatus(request_id=request_id, code=code)
        return await self.make_request(method)

    async def revoke_verification_message(
        self,
        request_id: str,
    ) -> bool:
        """Revoke a previously sent verification message.

        Args:
            request_id (str): The unique identifier of the request to revoke.

        Returns:
            bool: True if the revocation was successful, otherwise False.

        Example:
            >>> async def main() -> None:
            >>>     async with TelegramGateway(access_token="<access-token>") as gateway:
            >>>         await gateway.revoke_verification_message(request_id="abc123")
        """
        method = RevokeVerificationMessage(request_id=request_id)
        return await self.make_request(method)

    def validate_report_integrity(
        self,
        timestamp: int,
        signature: str,
        body: bytes,
    ) -> None:
        """Validate the integrity of a report received from Telegram Gateway.

        Args:
            timestamp (int): The X-Request-Timestamp header of the report.
            signature (str): The X-Request-Signature header of the report.
            body (bytes): The body of the report.

        Returns:
            None: This function raises exceptions for any validation issues.

        Example:
            >>> async def main() -> None:
            >>>     async with TelegramGateway(access_token="<access-token>") as gateway:
            >>>         gateway.validate_report_integrity(timestamp=123456789, signature="xyz", body=b'{}')
        """
        return validate_report_integrity(
            access_token=self._access_token,
            timestamp=timestamp,
            signature=signature,
            body=body,
        )

    async def aclose(self) -> None:
        """Close the underlying aiohttp ClientSession.

        This method should be called to properly clean up and release the resources associated
        with the `TelegramGateway` instance, especially if it was created outside of a context
        manager. It ensures that the HTTP session is closed and no further requests can be made.

        Example:
            >>> async def main() -> None:
            >>>     gateway = TelegramGateway(access_token="<access-token>")
            >>>     await gateway.send_verification_message(phone_number="+1234567890", code_length=6)
            >>>     await gateway.aclose()  # Properly close the session after making requests.

        Note:
            This method is useful when the `TelegramGateway` is not used within an async context manager
            (`async with`). It should be called manually to prevent resource leaks.
        """
        await self._session.close()

    async def __aenter__(self) -> "TelegramGateway":
        """Enter the context manager for the TelegramGateway client.

        Returns:
            TelegramGateway: The initialized client instance.

        Example:
            >>> async def main() -> None:
            >>>     async with TelegramGateway(access_token="<access-token>") as gateway:
            >>>         await gateway.send_verification_message(phone_number="+1234567890", code_length=6)
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        await self.aclose()
