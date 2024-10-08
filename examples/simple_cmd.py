import asyncio
from concurrent.futures import ThreadPoolExecutor

from tgateway import TelegramGateway


async def main():
    access_token = "<access_token>"
    phone_number = "<phone-number>"

    async with TelegramGateway(
        access_token=access_token,
    ) as gateway:
        ability = await gateway.check_send_ability(
            phone_number=phone_number,
        )

        print("ability:", ability)

        sent = await ability.send(code_length=4)

        print("sent:", sent)

        with ThreadPoolExecutor(max_workers=1) as executor:
            code = await asyncio.get_running_loop().run_in_executor(
                executor,
                input,
                "Enter code: ",
            )

        valid = await sent.check(code)
        print("valid", valid)


if __name__ == "__main__":
    asyncio.run(main())
