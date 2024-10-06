from enum import Enum


class DeliveryStatusEnum(str, Enum):
    """This object represents the delivery  status of the message.

    Source: https://core.telegram.org/gateway/api#deliverystatus
    """

    SENT = "sent"
    """The message has been sent to the recipient's device(s)."""
    READ = "read"
    """The message has been read by the recipient."""
    REVOKED = "revoked"
    """The message has been revoked."""


class VerificationStatusEnum(str, Enum):
    """This object represents the verification status of the verification process.

    Source: https://core.telegram.org/gateway/api#verificationstatus
    """

    CODE_VALID = "code_valid"
    """The code entered by the user is correct."""
    CODE_INVALID = "code_invalid"
    """The code entered by the user is incorrect."""
    CODE_MAX_ATTEMPTS_EXCEEDED = "code_max_attempts_exceeded"
    """The maximum number of attempts to enter the code has been exceeded."""
    EXPIRED = "expired"
    """The code has expired and can no longer be used for verification."""
