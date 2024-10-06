import hashlib
import hmac
import time


class ReportIntegrityError(Exception):
    pass


class TimestampOutOfRangeError(ReportIntegrityError):
    pass


class SignatureInvalidError(ReportIntegrityError):
    pass


def validate_report_integrity(
    access_token: str,
    timestamp: int,
    signature: str,
    body: bytes,
) -> None:
    excepted_timestamp = int(time.time())

    if abs(excepted_timestamp - timestamp) > 300:
        raise TimestampOutOfRangeError

    post_body = body.decode("utf-8")
    data_check_string = f"{timestamp}\n{post_body}"
    secret_key = hashlib.sha256(access_token.encode("utf-8")).digest()

    excepted_signature = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, excepted_signature):
        raise SignatureInvalidError
