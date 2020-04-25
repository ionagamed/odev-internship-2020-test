from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from rates_api.serializers import (
    ExchangeRateRequestSerializer, ExchangeRateResponseSerializer
)
from rates_api.services import get_exchange_rate_statistics


class GetExchangeRatesAPIView(APIView):
    @swagger_auto_schema(
        operation_summary='Get exchange rate statistics',
        query_serializer=ExchangeRateRequestSerializer,
        responses={200: ExchangeRateResponseSerializer}
    )
    def get(self, request):
        request_serializer = ExchangeRateRequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        request_data = request_serializer.validated_data
        stats, correlations = get_exchange_rate_statistics(request_data['start_at'],
                                                           request_data['end_at'],
                                                           request_data['base'])

        output_serializer = ExchangeRateResponseSerializer(
            instance={'stats': stats, 'correlations': correlations}
        )

        return Response(output_serializer.data)
