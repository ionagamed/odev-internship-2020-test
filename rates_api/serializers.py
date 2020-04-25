from rest_framework import serializers


class ExchangeRateRequestSerializer(serializers.Serializer):
    start_at = serializers.DateField(write_only=True,
                                     help_text='Date from which to begin counting')
    end_at = serializers.DateField(write_only=True,
                                   help_text='Date at which to start counting')
    base = serializers.CharField(write_only=True,
                                 help_text='Which currency to take as the base')

    def validate(self, data):
        if data['start_at'] > data['end_at']:
            raise serializers.ValidationError('start_at cannot be larger than end_at')
        return data


class CurrencyExchangeRateSerializer(serializers.Serializer):
    std_dev = serializers.FloatField(read_only=True, help_text='Standard deviation')
    avg = serializers.FloatField(read_only=True, help_text='Average value')
    correlation = serializers.FloatField(read_only=True,
                                         help_text='Correlation between the two values')


class ExchangeRateResponseSerializer(serializers.Serializer):
    # output API format is up for me to choose, and I don't like free keys floating
    # around at the root of the response object
    stats = serializers.DictField(child=CurrencyExchangeRateSerializer())
    correlations = serializers.DictField(
        child=serializers.DictField(
            child=serializers.FloatField(
                help_text='Correlation between the two currencies'
            )
        ),
        help_text='''
A mapping from the first currency to a dict, which maps second currencies to their
correlations.

For example:

```
{
    "RUB": {
        "EUR": 123,
        "USD": 456
    }
}
```

Here, (RUB, EUR) has correlation 123, and (RUB, USD) has correlation 456.
'''
    )
