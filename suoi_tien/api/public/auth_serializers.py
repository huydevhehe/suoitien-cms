from django.utils import timezone
from rest_framework import serializers

from suoi_tien.models import HalinkUser, _md5_double_hash


class CustomerRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=False, allow_blank=True)
    fullname = serializers.CharField(max_length=255, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_username(self, username):
        if HalinkUser.objects.filter(username=username).exists():
            raise serializers.ValidationError("Tên đăng nhập đã được sử dụng.")
        return username

    def create(self, validated_data):
        return HalinkUser.objects.create(
            username=validated_data['username'],
            password=validated_data['password'],  # tự hash trong HalinkUser.save()
            email=validated_data.get('email', ''),
            fullname=validated_data.get('fullname', ''),
            phone=validated_data.get('phone', ''),
            date=timezone.now().date(),
            ticlock=0,
            type_login='normal',
        )


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = HalinkUser.objects.filter(username=attrs['username']).first()
        if not user or user.password != _md5_double_hash(attrs['password']):
            raise serializers.ValidationError("Tên đăng nhập hoặc mật khẩu không đúng.")
        if user.ticlock:
            raise serializers.ValidationError("Tài khoản đã bị khóa.")
        attrs['user'] = user
        return attrs


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HalinkUser
        fields = [
            'id', 'username', 'email', 'fullname', 'birthday',
            'phone', 'avatar', 'gioitinh', 'address', 'date',
        ]
        read_only_fields = ['id', 'username', 'date']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate_old_password(self, old_password):
        user = self.context['user']
        if user.password != _md5_double_hash(old_password):
            raise serializers.ValidationError("Mật khẩu hiện tại không đúng.")
        return old_password


class CustomerOrderHistorySerializer(serializers.Serializer):
    id_cart = serializers.CharField()
    date = serializers.DateTimeField()
    status = serializers.IntegerField()
    status_label = serializers.SerializerMethodField()
    total_price = serializers.CharField(source='computed_total_price_formatted')
    type_payment = serializers.IntegerField()
    dateoforg = serializers.CharField()

    def get_status_label(self, obj) -> str:
        from .serializers import get_order_status_label
        return get_order_status_label(obj.status)
