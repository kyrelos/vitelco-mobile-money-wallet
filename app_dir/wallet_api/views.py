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
        bulk_transactions = BatchTransaction.objects.all()
        serializer = BatchTransactionSerializer(bulk_transactions, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):



        serializer = BatchTransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)