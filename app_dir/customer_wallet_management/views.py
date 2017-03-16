from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from app_dir.customer_wallet_management.models import CustomerWallet
from app_dir.customer_wallet_management.serializers import CustomerWalletSerializer

@csrf_exempt
def wallets_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        wallets = CustomerWallet.objects.all()
        serializer = CustomerWalletSerializer(wallets, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CustomerWalletSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)