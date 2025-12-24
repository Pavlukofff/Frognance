from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer


class IncomeListAPI(generics.ListAPIView):
    """
    API view to list all income transactions for the authenticated user.

    Provides a paginated list of income transactions, ordered by date.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        """
        Return a queryset of income transactions filtered by the current user.
        """
        return Transaction.objects.filter(user=self.request.user, t_type='income').order_by('-date')
