import logging
import os
from contextlib import asynccontextmanager
from typing import cast

from fastapi import (
    FastAPI,
    HTTPException,
    Header,
    Request,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from tgateway import TelegramGateway
from tgateway.integrity import (
    SignatureInvalidError,
    TimestampOutOfRangeError,
)
from tgateway.types import (
    RequestStatus,
)

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    access_token = os.getenv("TELEGRAM_GATEWAY_ACCESS_TOKEN")
    if access_token is None:
        raise RuntimeError("Missing TELEGRAM_GATEWAY_ACCESS_TOKEN")

    async with TelegramGateway(
        access_token=access_token,
    ) as gateway:
        yield {"gateway": gateway}


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def webhook_handler(
    request: Request,
    x_request_timestamp: int = Header(alias="X-Request-Timestamp"),
    x_request_signature: str = Header(alias="X-Request-Signature"),
):
    gateway = cast(TelegramGateway, request.state.gateway)
    body = await request.body()

    logging.info(
        dict(
            event="new_incoming_request",
            x_request_timestamp=x_request_timestamp,
            x_request_signature=x_request_signature,
            body=body,
        )
    )

    try:
        gateway.validate_report_integrity(
            timestamp=x_request_timestamp,
            signature=x_request_signature,
            body=body,
        )
    except TimestampOutOfRangeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Timestamp out of range"
        )
    except SignatureInvalidError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature"
        )

    try:
        request_status = RequestStatus.model_validate_json(body)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body"
        )

    logging.info(
        dict(
            event="valid_incoming_request",
            x_request_timestamp=x_request_timestamp,
            x_request_signature=x_request_signature,
            body=body,
            request_status=request_status,
        )
    )

    return JSONResponse(content={"ok": True}, status_code=status.HTTP_200_OK)
