import asyncio
import logging
from http import HTTPStatus
import aiohttp


CURRENCY_ERROR = "failed to pull data for the currency:"


def _set_url(currency, range_of_days):
    """
    Function to set NBP API url.

    :param currency: string representing the currency code in NBP url
    :param range_of_days: range of days to set in NBP url.
    :return: string representing the NBP API url with the currency and range of days.
    """
    default_nbp_api_url = (
        "http://api.nbp.pl/api/exchangerates/rates/c/CURRENCY/last/DAYS/?format=json"
    )
    return default_nbp_api_url.replace("CURRENCY", currency).replace(
        "DAYS", str(range_of_days)
    )


async def _get_exchange_rate_from_nbp(currency, range_of_days, session):
    """
    Function to get exchange rate from NBP API.

    :param currency: string representing the currency code in NBP url / API.
    :param range_of_days: range of days to get data from NBP API.
    :param session: aiohttp.ClientSession object.
    :return: dict in the format: {"code": "currency code", "rates": [{"effectiveDate": "date", "mid": "rate"}]}
            or {CURRENCY_ERROR: "currency code"} if failed to get data for the currency.
    """
    logging.basicConfig(level=logging.ERROR)
    # Set the url for the currency and range of days to get data from NBP API.
    url = _set_url(currency, range_of_days)
    # Get the data from NBP API with exception handling.
    try:
        async with session.get(url) as response:
            if response.status == HTTPStatus.OK:
                result = await response.json()
                return result
            else:
                logging.error(f"Error status: {response.status} for {url}")
                return {CURRENCY_ERROR: currency}
    except aiohttp.ClientConnectorError as err:
        logging.error(f"Connection error: {url}", str(err))
    return {CURRENCY_ERROR: currency}


async def get_data_from_nbp(range_of_days, currencies: list):
    """
    Function to retrieve data from the NBP API from the passed multiple currencies and the passed range of days.

    :param range_of_days: range of days to get data from NBP API.
    :param currencies: list of currencies to get data from NBP API.
    :return: list of dicts in the format like for example (for currencies USD and EUR and range of days 2):
        [{'table': 'C', 'currency': 'dolar amerykański', 'code': 'USD', 'rates':
        [{'no': '023/C/NBP/2024', 'effectiveDate': '2024-02-01', 'bid': 3.9439, 'ask': 4.0235},
        {'no': '024/C/NBP/2024', 'effectiveDate': '2024-02-02', 'bid': 3.9558, 'ask': 4.0358}]},
        {'table': 'C', 'currency': 'euro', 'code': 'EUR', 'rates':
        [{'no': '023/C/NBP/2024', 'effectiveDate': '2024-02-01', 'bid': 4.291, 'ask': 4.3776},
        {'no': '024/C/NBP/2024', 'effectiveDate': '2024-02-02', 'bid': 4.2829, 'ask': 4.3695}]}]
    """
    async with aiohttp.ClientSession() as session:
        result = await asyncio.gather(
            *[
                _get_exchange_rate_from_nbp(currency, range_of_days, session)
                for currency in currencies
            ]
        )
        return result


def get_args(arguments):
    """
    Functon to set range of days and currencies to get data from NBP API,
    based on the passed arguments and default values.

    :param arguments: tuple of strings representing the arguments passed from the command line.
    :return: tuple of two elements: range of days and list of currencies.
    """
    currencies = ["usd", "eur"]
    range_of_days = 1
    if len(arguments) == 0:
        return range_of_days, currencies
    arguments = [arg.lower() for arg in arguments]
    # If the first argument is a number, set range of days to the passed number,
    if arguments[0].lstrip("-").isdecimal():
        # if it is in the range 0-10: return it.
        if 0 < int(arguments[0]) <= 10:
            range_of_days = int(arguments[0])
        # If it is bigger than 10, set it to 10. If it is lower than 1, return 1 (default value).
        elif int(arguments[0]) > 10:
            range_of_days = 10
        currencies += arguments[1:]
        return range_of_days, currencies
    currencies += arguments
    return range_of_days, currencies


def data_adapter(data: tuple) -> list:
    """
    Function to adapt data from NBP API to the format required for the homework.

    :param data: tuple of dicts in the format returned from NBP by function get_data_from_nbp function.
    :return: list of dicts in the format like for example (for currencies USD, EUR and XYZ (unable to get currency)
    and range of days 2):
    [{'date': '2024-02-01', 'USD': {'sale': 3.9439, 'purchase': 4.0235}, 'EUR': {'sale': 4.291, 'purchase': 4.3776}},
    {'date': '2024-02-02', 'USD': {'sale': 3.9558, 'purchase': 4.0358}, 'EUR': {'sale': 4.2829, 'purchase': 4.3695}},
    [{'failed to pull data for the currency:': 'xyz'}]]
    """
    dates = {}
    errors = []
    for item in data:
        if CURRENCY_ERROR in item.keys():
            errors.append({CURRENCY_ERROR: item[CURRENCY_ERROR]})
            continue
        item["rates"].reverse()
        for rate in item["rates"]:
            dates[rate["effectiveDate"]] = (
                {item["code"]: {"sale": rate["ask"], "purchase": rate["bid"]}}
                if rate["effectiveDate"] not in dates
                else dates[rate["effectiveDate"]]
                | {item["code"]: {"sale": rate["ask"], "purchase": rate["bid"]}}
            )
    # If there are errors, return the data formatted in the way required for the homework and errors.
    # Returning errors is not a part of the homework, so to skip it, just comment out the if statement below.
    if errors:
        return [dates, errors]
    return [dates]


def pretty_view(data: list) -> str:
    """
    Function to set format data in the way suitable for the web page.

    :param data: list in the format returned from data_adapter function.
    :return: string formatted in the way suitable for the web page.
    """
    formatted_string = "exchange rates: "
    error_info = ""
    for date_dict in data:
        # If the data is list it means that there are errors. So, we need to add the error info to the string.
        if isinstance(date_dict, list):
            error_info += f"{CURRENCY_ERROR.upper()} "
            wrong_args = []
            for info in date_dict:
                wrong_args.append(f"{info[CURRENCY_ERROR]}")
            error_info += ", ".join(wrong_args) + "\n"
            continue
        currencies_info = []
        for date, currencies in date_dict.items():
            formatted_string += f"DATE: {date} - "
            for currency, values in currencies.items():
                currency = currency.upper()
                buy = values["purchase"]
                sale = values["sale"]
                currencies_info.append(f"{currency}: sale: {buy} | sale: {sale}")
            formatted_string += " || ".join(currencies_info) + " <<>> "
    if error_info:
        return formatted_string + "\n" + error_info
    return formatted_string
