import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Category, Transaction, User
from .serializers import CategorySerializer, TransactionSerializer


class LoginView(viewsets.ViewSet):
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
        token, _ = Token.objects.get_or_create(user=user)
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


class GithubLoginView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @csrf_exempt
    @action(detail=False, methods=["post"], url_path="github")
    def login_view(self, request):
        token = request.data.get("access_token")
        token_type = request.data.get("token_type")
        if not token:
            return JsonResponse({"error": "缺少 token"}, status=400)

        if not token_type:
            return JsonResponse({"error": "缺少 Token Type"}, status=400)

        user_info_url = "https://api.github.com/user"
        headers = {"Authorization": f"token {token}"}
        response = requests.get(user_info_url, headers=headers)

        user_email_url = "https://api.github.com/user/emails"
        email_response = requests.get(user_email_url, headers=headers)

        if response.status_code != 200 or email_response.status_code != 200:
            return JsonResponse({"error": "無法驗證 GitHub token"}, status=400)

        github_user = response.json()
        username = github_user.get("login")

        user_emails = email_response.json()
        email = ""
        for user_email in user_emails:
            if user_email.get("primary") == True:
                email = user_email.get("email")
                break

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"password": make_password(settings.GITHUB_DEFAULT_PASSWORD), "email": email},
        )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class PasswordResetRequestView(View):
    def post(self, request):
        try:
            # 嘗試解析 JSON 請求
            if request.content_type == "application/json":
                body = json.loads(request.body)
                email = body.get("email", None)
            else:
                # 處理表單格式數據
                email = request.POST.get("email", None)

            # 驗證 email 是否存在
            if not email:
                return JsonResponse({"error": "請輸入電子郵件"}, status=400)

            # 查找用戶
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # 构建重置密碼連結
            reset_link = f"http://localhost:8000/password-reset/{uid}/{token}/"

            # 發送重置密碼郵件
            send_mail(
                "重置您的密碼",
                f"請點擊以下鏈接重置密碼：\n\n{reset_link}\n\n如果未請求，請忽略此郵件。",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            return JsonResponse({"message": "密碼重置郵件已發送"}, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "該電子郵件未註冊"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"後端錯誤：{str(e)}"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class PasswordResetView(View):
    permission_classes = [AllowAny]

    @csrf_exempt
    def get(self, request, uidb64, token):
        # 顯示重置密碼表單
        return render(
            request, "password_reset_form.html", {"uidb64": uidb64, "token": token}
        )

    @csrf_exempt
    def post(self, request, uidb64, token):
        new_password = request.POST.get("new_password")
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                messages.success(request, "密碼重置成功！")
                return render(
                    request, "password_reset_successful.html", {"success": True}
                )
            else:
                messages.error(request, "無效的重置連結")
        except Exception:
            messages.error(request, "密碼重置失敗")
        return redirect("password_reset_request")


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
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        if category:
            transactions = transactions.filter(category=category)
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)

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
