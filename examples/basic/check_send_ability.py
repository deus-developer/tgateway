import asyncio

from tgateway import TelegramGateway


async def main():
    async with TelegramGateway(access_token="<access-token>") as gateway:
        result = await gateway.check_send_ability(
            phone_number="+1234567890",
        )

        print(f"Verification ability: {result}")


asyncio.run(main())
