import asyncio

from tgateway import TelegramGateway


async def main():
    async with TelegramGateway(access_token="<access-token>") as gateway:
        try:
            gateway.validate_report_integrity(
                timestamp=123456789,  # Timestamp from header
                signature="report_signature",  # Signature from header
                body=b"{}",  # Body of the report as bytes
            )
            print("Report integrity validated successfully.")
        except Exception as e:
            print(f"Validation failed: {e}")


asyncio.run(main())
