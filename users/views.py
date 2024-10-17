import random
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


# Регистрация
@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    # Создаем неактивного пользователя
    user = User.objects.create_user(username=username, password=password, email=email, is_active=False)

    # Генерация кода подтверждения
    confirmation_code = random.randint(100000, 999999)

    # Сохраняем код в модели пользователя (например, через профиль)
    user.profile.confirmation_code = confirmation_code
    user.save()

    # Отправляем код
    return Response({"confirmation_code": confirmation_code})


# Авторизация
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
            return Response({"error": "User is not active."}, status=403)
    return Response({"error": "Invalid credentials."}, status=400)


# Подтверждение пользователя
@api_view(['POST'])
def confirm_user(request):
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')

    user = User.objects.get(username=username)

    if user.profile.confirmation_code == confirmation_code:
        user.is_active = True
        user.save()
        return Response({"message": "User confirmed and activated."})

    return Response({"error": "Invalid confirmation code."}, status=400)
