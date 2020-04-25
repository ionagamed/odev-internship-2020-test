from collections import defaultdict
import datetime
import statistics
from typing import List, Tuple, Dict, Any
from urllib.parse import urlencode
from django.conf import settings
from rest_framework import status
from cacheops import cached
import requests


class ExternalServiceError(Exception):
    pass


def _correlation(values_a: List[float], values_b: List[float], mean_a: float,
                 mean_b: float, stddev_a: float, stddev_b: float) -> float:
    ab = [a * b for a, b in zip(values_a, values_b)]
    mean_ab = sum(ab) / len(ab)
    covariance = mean_ab - mean_a * mean_b

    # okay, i'm not a data scientist, dunno what to do in that case
    if stddev_a * stddev_b == 0:
        return 0

    return covariance / (stddev_a * stddev_b)


@cached(timeout=settings.RATE_STATISTICS_CACHE_TIMEOUT)
def get_exchange_rate_statistics(start_at: datetime.date, end_at: datetime.date,
                                 base: str) -> Tuple[Dict[str, Any], List[Any]]:
    '''
    Fetch external exchange rate information and process it into a dict with statistics.

    This currently takes O(N^2), but can be optimized using divide-and-conquer to
    O(NlogN).

    :param start_at: date at which to start counting.
    :param end_at: date at which to stop counting.
    :param base: base currency.
    :returns: calculated statistics, as a tuple of (avg and mean by currency,
              correlation by currency pair)
    '''

    rates = get_exchange_rates(start_at, end_at, base)

    values_by_currency = defaultdict(list)
    for rate_obj in rates:
        for currency, rate in rate_obj.items():
            values_by_currency[currency].append(rate)

    stats_by_currency = {}
    for currency, values in values_by_currency.items():
        avg = statistics.mean(values)
        std_dev = statistics.pstdev(values)
        stats_by_currency[currency] = {
            'avg': avg,
            'std_dev': std_dev
        }

    correlation_by_currency_pair = defaultdict(dict)
    for currency_a, values_a in values_by_currency.items():
        for currency_b, values_b in values_by_currency.items():
            correlation_by_currency_pair[currency_a][currency_b] = \
                _correlation(
                    values_a,
                    values_b,
                    stats_by_currency[currency_a]['avg'],
                    stats_by_currency[currency_b]['avg'],
                    stats_by_currency[currency_a]['std_dev'],
                    stats_by_currency[currency_b]['std_dev'],
                )

    return stats_by_currency, correlation_by_currency_pair


@cached(timeout=settings.RATE_FETCH_CACHE_TIMEOUT)
def get_exchange_rates(start_at: datetime.date, end_at: datetime.date, base: str):
    '''
    Fetch external exchange rate information and process it into a list of dicts.

    This might be worth to refactor to a class, but there is no stateful logic right
    now, so...

    :param start_at: date at which to start counting.
    :param end_at: date at which to stop counting.
    :param base: base currency.
    :returns: fetched currency rates.
    '''

    params = {
        'start_at': start_at.strftime('%Y-%m-%d'),
        'end_at': end_at.strftime('%Y-%m-%d'),
        'base': base
    }
    url = f'{settings.EXTERNAL_API_BASE}/history?{urlencode(params)}'

    # thrown errors are expected to be rethrown
    response = requests.get(url)

    if response.status_code != status.HTTP_200_OK:
        raise ExternalServiceError(
           f'Expected status code 200 from external API, got {response.status_code}'
        )

    raw_json = response.json()
    rate_output = [rate_entry for rate_entry in raw_json['rates'].values()]
    return rate_output
