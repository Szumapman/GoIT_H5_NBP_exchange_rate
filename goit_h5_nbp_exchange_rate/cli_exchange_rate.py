import sys
import platform
import asyncio

from utilities.nbp_exchange_rate_tools import get_args, get_data_from_nbp, data_adapter


if __name__ == "__main__":
    """ """
    # Get the range of days and currencies according to the arguments passed to the script.
    range_of_days, currencies = get_args(sys.argv[1:])
    # Set the event loop policy on Windows, to avoid error: "RuntimeError: Event loop is closed."
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # Get the data from NBP API with the range of days and currencies.
    data_from_nbp = asyncio.run(get_data_from_nbp(range_of_days, currencies))
    # Print the data in the format according to the homework requirements.
    print(data_adapter(data_from_nbp))
