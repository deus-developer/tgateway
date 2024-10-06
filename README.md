# Telegram Gateway Python SDK

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/github/license/deus-developer/tgateway)
![Build Status](https://img.shields.io/github/actions/workflow/status/deus-developer/tgateway/release_pypi.yaml)

Telegram Gateway Python SDK is a lightweight and asynchronous client library designed to interface with the [Telegram Gateway API](https://core.telegram.org/gateway).

## ✨ Features

- **Send Verification Messages**: Deliver verification codes to users' phone numbers.
- **Check Delivery Status**: Verify the status of sent messages and handle callbacks.
- **Revoke Verification**: Invalidate previously sent verification messages.
- **Integrity Validation**: Ensure authenticity of incoming reports using signature validation.
- **Easy to Use**: Designed with simplicity and usability in mind.
- **Fully Asynchronous**: Built on `asyncio` for high-performance integration.

## 🏗️ Installation

Install the SDK using pip:

```bash
pip install tgateway
```

## 📚 Usage

Here's a basic example to get started with the `TelegramGateway` client:

### Check a send verification message ability

```python
import asyncio
from tgateway import TelegramGateway

async def main():
    async with TelegramGateway(access_token="<access-token>") as gateway:
        result = await gateway.check_send_ability(
            phone_number="+1234567890",
        )

        print(f"Verification ability: {result}")

asyncio.run(main())
```

### Send a verification message

```python
import asyncio
from tgateway import TelegramGateway

async def main():
    async with TelegramGateway(access_token="<access-token>") as gateway:
        result = await gateway.send_verification_message(
            phone_number="+1234567890",
            code_length=6
        )

        print(f"Verification message sent: {result}")

asyncio.run(main())
```

### Check the Status of a Verification Request

```python
import asyncio
from tgateway import TelegramGateway

async def main():
    async with TelegramGateway(access_token="<access-token>") as gateway:
        result = await gateway.check_verification_status(request_id="<request-id>")

        print(f"Verification status: {result}")

asyncio.run(main())
```

### Revoke a Verification Message

```python
import asyncio
from tgateway import TelegramGateway

async def main():
    async with TelegramGateway(access_token="<access-token>") as gateway:
        result = await gateway.revoke_verification_message(request_id="<request-id>")

        print(f"Verification revoked: {result}")

asyncio.run(main())
```

### Validate Incoming Delivery Reports

To confirm the origin and integrity of incoming reports, you can use the `validate_report_integrity` method provided by the SDK:

```python
import asyncio
from tgateway import TelegramGateway


async def main():
    async with TelegramGateway(access_token="<access-token>") as gateway:
        try:
            gateway.validate_report_integrity(
                timestamp=123456789,  # Timestamp from header
                signature="report_signature",  # Signature from header
                body=b'{}'  # Body of the report as bytes
            )
            print("Report integrity validated successfully.")
        except Exception as e:
            print(f"Validation failed: {e}")

asyncio.run(main())
```

## 🏛️ Project Structure

The project is structured for ease of use and maintainability:

```
tgateway/
├── client.py                    # Main client class.
├── constants.py                 # Constants used throughout the SDK.
├── enums.py                     # Enum definitions for API statuses.
├── exceptions.py                # Custom exception classes.
├── integrity.py                 # Integrity validation utilities.
├── methods.py                   # Implementation of Telegram Gateway API methods.
├── types.py                     # Type definitions for API responses.
```

## 🧪 Testing

Currently, the project does not have test cases but this is planned for future releases. Contributions to add tests are welcome!

## 🔗 Important Links
- **Telegram Gateway Overview**: [Telegram Gateway Overview](https://core.telegram.org/gateway)
- **API Reference**: [Gateway API Reference](https://core.telegram.org/gateway/api)
- **Verification Tutorial**: [Verification Tutorial](https://core.telegram.org/gateway/verification-tutorial)
- **Manage Your Account**: [Gateway Account](https://gateway.telegram.org/account)
- **Terms of Service**: [Gateway Terms of Service](https://telegram.org/tos/gateway)

## 📃 License

This project is licensed under the [Apache License](LICENSE).

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/my-new-feature`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/my-new-feature`.
5. Open a pull request.

## 💬 Contact

For questions, support, or just to connect, please reach out to the project maintainers:

- **Email**: [deusdeveloper@yandex.com](mailto:deusdeveloper@yandex.com)
- **Telegram**: [@DeusDeveloper](https://t.me/DeusDeveloper)
- **Chat**: [@tgateway](https://t.me/tgateway)
- **GitHub Issues**: [GitHub Repository](https://github.com/deus-developer/tgateway/issues)

---

Enjoy using the Telegram Gateway Python SDK! 🎉
