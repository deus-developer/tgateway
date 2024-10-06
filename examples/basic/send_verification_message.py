import asyncio

from tgateway import TelegramGateway


async def main():
    async with TelegramGateway(access_token="<access-token>") as gateway:
        result = await gateway.send_verification_message(
            phone_number="+1234567890", code_length=6
        )

        print(f"Verification message sent: {result}")


asyncio.run(main())
