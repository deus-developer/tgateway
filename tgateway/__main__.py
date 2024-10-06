"""CLI entry point to TelegramGateway."""

import warnings

try:
    from tgateway.cli.main import cli
except ImportError:
    has_typer = False
else:
    has_typer = True

if not has_typer:
    raise ImportError(
        "\n\nYou're trying to use the TelegramGateway CLI, "
        "\nbut you haven't installed the required dependencies."
        "\nPlease install them using the following command: "
        '\npip install "tgateway[cli]"',
    )

warnings.filterwarnings("default", category=ImportWarning, module="tgateway")

if __name__ == "__main__":
    cli(prog_name="tgateway")
