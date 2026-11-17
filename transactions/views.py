from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework import authentication,permissions
from transactions.models import Expense
from transactions.serializers import ExpenseSerializer
from rest_framework.response import Response
from transactions.permissions import IsOwner
from datetime import datetime
from django.db.models import Sum

# Create your views here.
class ExpenseListCreateView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self,request):

        auth_user=request.user

        qs=Expense.objects.filter(owner=auth_user)

        serializer_instance=ExpenseSerializer(qs,many=True)

        return Response(serializer_instance.data)

    def post(self,request):

        form_data=request.data

        auth_user=request.user

        serializer_instance=ExpenseSerializer(data=form_data)

        if serializer_instance.is_valid():
            serializer_instance.save(owner=auth_user)

            return Response(serializer_instance.data)
        else:
            return Response(serializer_instance._errors)

class ExpenseRetrieveUpdateDeleteView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[IsOwner]

    def get(self,request,pk=None):

        qs=get_object_or_404(Expense,id=pk)
        self.check_object_permissions(request,qs)
        serializer_instance=ExpenseSerializer(qs)
        return Response(serializer_instance.data)

    def put(self,request,pk=None):

        instance=get_object_or_404(Expense,id=pk)
        self.check_object_permissions(request,instance)
        form_data=request.data
        serializer_instance=ExpenseSerializer(data=form_data,instance=instance)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(serializer_instance.data)
        else:
            return Response(serializer_instance.errors)

    def delete(self,request,pk=None):

        instance=get_object_or_404(Expense,id=pk)
        self.check_object_permissions(request,instance)
        instance.delete()
        return Response({"message" : "deleted"})


class ExpenseSummaryView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self,request):

        auth_user_expenses=Expense.objects.filter(owner=request.user)

        response_data={
            "todays_expense" : 0,
            "monthly_expense" : 0
        }

        cur_date=datetime.today().date()

        todays_total=auth_user_expenses.filter(
            created_at__date=cur_date).values("amount").aggregate(total=Sum("amount")).get("total")

        response_data["todays_expense"]=todays_total

        cur_month=datetime.today().month
        cur_year=datetime.today().year
        monthly_expense_total=auth_user_expenses.filter(created_at__month=cur_month,created_at__year=cur_year).values("amount").aggregate(total=Sum("amount")).get("total")
        response_data["monthly_expense"]=monthly_expense_total

        return Response(response_data)
    


