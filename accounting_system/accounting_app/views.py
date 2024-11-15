import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from .models import Category, Transaction, User
from .serializers import CategorySerializer, TransactionSerializer


class LoginSystem(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @csrf_exempt
    @action(detail=False, methods=["post"], url_path="register")
    def register_view(self, request):
        """用戶註冊"""
        try:
            username = request.data.get("username")
            password = request.data.get("password")
            email = request.data.get("email")

            # 檢查是否已存在該用戶
            if User.objects.filter(username=username).exists():
                return Response(
                    {"error": "帳號已存在"}, status=status.HTTP_400_BAD_REQUEST
                )

            # 檢查必要欄位
            if not (username and password and email):
                return Response(
                    {"error": "缺少必要欄位"}, status=status.HTTP_400_BAD_REQUEST
                )

            # 創建新用戶
            user = User.objects.create(
                username=username, password=make_password(password), email=email
            )
            return Response(
                {"message": "註冊成功", "username": user.username},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @action(detail=False, methods=["post"], url_path="login")
    def login_view(self, request):
        """用戶登入並返回 Token"""
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # 生成或取得 Token
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="logout")
    def logout_view(self, request):
        """用戶登出"""
        if request.user.is_authenticated:
            # 刪除用戶的 Token
            request.user.auth_token.delete()
            return Response({"message": "登出成功"}, status=status.HTTP_200_OK)
        return Response({"error": "用戶未登入"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=["get"], url_path="users")
    def user_view(self, request):
        """獲取用戶列表"""
        users = User.objects.all()
        data = [{"username": user.username, "email": user.email} for user in users]
        return Response(data, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        category_type = request.query_params.get("category_type", None)
        if category_type:
            categories = categories.filter(category_type=category_type)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryGetDeleteUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            category = get_object_or_404(Category, id=id)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "無效的 ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            category = get_object_or_404(Category, id=id)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response({"error": "無效的 ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)

        category = request.query_params.get("category", None)
        start_time = request.query_params.get("start_time", None)
        end_time = request.query_params.get("end_time", None)

        if category:
            transactions = transactions.filter(category=category)
        if start_time:
            transactions = transactions.filter(date__gte=start_time)
        if end_time:
            transactions = transactions.filter(date__lte=end_time)

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionGetDeleteUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            transaction = get_object_or_404(Transaction, id=id, user=request.user)
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"error": "無效的 ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        transaction = get_object_or_404(Transaction, id=id, user=request.user)
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            transaction = get_object_or_404(Transaction, id=id, user=request.user)
            transaction.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response({"error": "無效的 ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
