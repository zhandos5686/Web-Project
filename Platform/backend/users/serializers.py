from django.contrib.auth import authenticate
from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "username", "email", "role", "bio"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserProfile.Role.choices, default=UserProfile.Role.STUDENT)
    bio = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        role = validated_data.pop("role")
        bio = validated_data.pop("bio", "")
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.bio = bio
        profile.save(update_fields=["role", "bio"])
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("This user account is disabled.")
        attrs["user"] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def get_user(self):
        email = self.validated_data["email"]
        return User.objects.filter(email__iexact=email, is_active=True).first()

    @staticmethod #Это часть системы сброса пароля. Она генерирует данные для токена сброса пароля, который будет отправлен пользователю по электронной почте. Данные включают в себя уникальный идентификатор пользователя (uid) и токен, который проверяет подлинность запроса на сброс пароля.
    def build_token_data(user):
        return {
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        }


class ResetPasswordSerializer(serializers.Serializer): # эта часть системы сброса пароля. Она принимает данные от пользователя, включая uid, токен и новый пароль. Она проверяет валидность данных и, если все в порядке, обновляет пароль пользователя.
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True) # это поле для подтверждения нового пароля. Оно должно совпадать с полем new_password, чтобы убедиться, что пользователь не допустил ошибку при вводе нового пароля. В методе validate выполняется проверка на совпадение этих двух полей, и если они не совпадают, возникает ошибка валидации.

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        try:
            user_id = force_str(urlsafe_base64_decode(attrs["uid"])) # Этот код декодирует uid, который был закодирован с помощью urlsafe_base64_encode при генерации токена сброса пароля. Он преобразует закодированный uid обратно в строку, которая представляет собой первичный ключ пользователя. Затем он пытается получить объект пользователя из базы данных, используя этот первичный ключ и проверяя, что пользователь активен. Если декодирование или получение пользователя не удается, возникает ошибка валидации.
            user = User.objects.get(pk=user_id, is_active=True) #what is the pk? pk stands for "primary key". In Django, each model has a primary key field that uniquely identifies each record in the database. By default, Django creates an auto-incrementing integer field called "id" as the primary key for each model. In this code, pk refers to the primary key of the User model, which is used to retrieve the user object from the database based on the decoded uid.
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid password reset link."})

        if not default_token_generator.check_token(user, attrs["token"]): # Этот код проверяет действительность токена сброса пароля, используя встроенный генератор токенов Django. Он принимает объект пользователя и токен, который был передан в запросе. Метод check_token возвращает True, если токен действителен для данного пользователя, и False в противном случае. Если токен недействителен, возникает ошибка валидации.
            raise serializers.ValidationError({"token": "Invalid or expired password reset token."})

        password_validation.validate_password(attrs["new_password"], user=user)
        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user
