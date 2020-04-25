from unittest.mock import patch
from urllib.parse import urlencode
from django.test import TestCase


def mock_get_exchange_rates(*args, **kwargs):
    return [
        {
            'RUB': 10,
            # did you know that there is a currency with code PHP?
            # it is Philippine peso
            # guess it's ... unstable, amirite? )000)0)
            # yeah, i know, thanks, come to my standup
            'PHP': 20
        },
        {
            'RUB': 20,
            'EUR': 5
        },
        {
            'EUR': 10,
            'PHP': 30
        }
    ]


class ExchangeRatesAPIViewTestCase(TestCase):
    maxDiff = None

    @patch('rates_api.services.get_exchange_rates', mock_get_exchange_rates)
    def test__get_rate_stats__correct(self):
        params = {
            'start_at': '2020-04-01',
            'end_at': '2020-04-03',
            'base': 'USD'
        }
        response = self.client.get(f'/api/?{urlencode(params)}')
        body = response.json()

        self.assertEqual(body, {
            'stats': {
                'RUB': {
                    'avg': 15.0,
                    'std_dev': 5.0
                },
                'EUR': {
                    'avg': 7.5,
                    'std_dev': 2.5
                },
                'PHP': {
                    'avg': 25.0,
                    'std_dev': 5.0
                }
            }
        })

    def test__get_rate_stats__fails__when_date_format_wrong(self):
        params = {
            'start_at': '01.04.2020',
            'end_at': '2020-04-02',
            'base': 'USD'
        }
        response = self.client.get(f'/api/?{urlencode(params)}')
        self.assertEqual(response.status_code, 400)

    def test__get_rate_stats__fails__when_not_enough_fields(self):
        params = {
            'start_at': '2020-04-01',
            'base': 'USD'
        }
        response = self.client.get(f'/api/?{urlencode(params)}')
        self.assertEqual(response.status_code, 400)
