from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer
from django.db.models import Sum


class IncomeListAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        incomes = Transaction.objects.filter(user=request.user, t_type='income').order_by('-date')
        total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
        serializer = TransactionSerializer(incomes, many=True)
        return Response({'incomes': serializer.data, 'total_income': total_income})
