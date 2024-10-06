import asyncio

from tgateway import TelegramGateway


async def main():
    async with TelegramGateway(access_token="<access-token>") as gateway:
        result = await gateway.check_verification_status(request_id="<request-id>")

        print(f"Verification status: {result}")


asyncio.run(main())
