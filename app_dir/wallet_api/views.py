from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from app_dir.wallet_transactions.models import BatchTransaction
from app_dir.wallet_transactions.serializers import BatchTransactionSerializer


class BatchTransactions(APIView):

    def get_object(self, pk):
        try:
            return BatchTransaction.objects.get(pk=pk)
        except BatchTransaction.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        batch_transactions = BatchTransaction.objects.all()
        serializer = BatchTransactionSerializer(batch_transactions, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        print("Started")
        data = request.data

        print("Ended")
        # serializer = BatchTransactionSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(data, status=status.HTTP_202_ACCEPTED)