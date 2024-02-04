import asyncio
import logging
import aiofile
import aiopath
from datetime import datetime

import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

from goit_h5_nbp_exchange_rate.utilities.nbp_exchange_rate_tools import (
    get_args,
    get_data_from_nbp,
    data_adapter,
    pretty_view,
)

# Create a logger with the name "server" and set its level to DEBUG.
logger = logging.getLogger("server")
logger.setLevel(logging.DEBUG)
# Set the following logging configuration:
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
# Create a file handler set its level to INFO and add the formatter to it.
fh = logging.FileHandler("server.log")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
# Add the file handler to the logger.
logger.addHandler(fh)


class Server:
    """
    Websocket server class from lecture (the only change is in distribute method + added method _set_exchange_message).
    """

    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logger.info(f"{ws.remote_address} connects")

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logger.info(f"{ws.remote_address} disconnects")

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    @staticmethod
    async def _set_exchange_message(message: str) -> str:
        """
        Create message with the exchange data.
        :param message: message starting with exchange to process
        :return: string with exchange data formatted to show on website
        """
        range_of_days, currencies = get_args(message.split()[1:])
        data_from_nbp = await get_data_from_nbp(range_of_days, currencies)
        message = data_adapter(data_from_nbp)
        return pretty_view(message)

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            # Check if the message is an exchange request.
            if message.split()[0].lower() == "exchange":
                await exchange_logging(ws.name, message)
                # Create message with the exchange data.
                message = await self._set_exchange_message(message)
            await self.send_to_clients(f"{ws.name}: {message}")


async def _set_exchange_logging_directory():
    """
    Function to set the directory for the exchange logging.

    :return: string with the directory path.
    """
    app_dir = await aiopath.Path(__file__).parent.absolute()
    logging_directory = app_dir.joinpath("exchange_logging")
    if not await logging_directory.exists():
        await aiopath.Path.mkdir(logging_directory)
    return logging_directory


async def exchange_logging(user_name: str, command: str):
    """
    Function to save in file logging for the exchange command.

    :param user_name: string with user's name who called the command.
    :param command: full command string.
    """
    logging_directory = await _set_exchange_logging_directory()
    log_file = logging_directory.joinpath("exchange.log")
    async with aiofile.async_open(log_file, mode="a") as f:
        await f.write(f"{datetime.now()} - {user_name} call command: {command}.\n")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, "localhost", 8080):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
