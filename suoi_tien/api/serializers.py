from rest_framework import serializers
from suoi_tien.models import (
    HalinkAdmin, HalinkUser, HalinkPost, HalinkCart, HalinkMenu,
    TicketOrderProxy, FoodOrderProxy, CommentProxy, SupportProxy
)

class HalinkAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = HalinkAdmin
        fields = ['Id', 'username', 'password', 'email', 'level', 'time', 'fullname', 'note', 'address', 'idcat']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        # Admin model đã tự băm MD5 double hash trong hàm save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class HalinkUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = HalinkUser
        fields = [
            'id', 'username', 'password', 'email', 'fullname', 
            'birthday', 'phone', 'avatar', 'gioitinh', 'address', 
            'date', 'ticlock', 'type_login'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }


class HalinkPostSerializer(serializers.ModelSerializer):
    clean_title = serializers.CharField(read_only=True)
    clean_description = serializers.CharField(read_only=True)
    clean_content = serializers.CharField(read_only=True)

    class Meta:
        model = HalinkPost
        fields = '__all__'


class TicketOrderSerializer(serializers.ModelSerializer):
    computed_total_price_num = serializers.IntegerField(read_only=True)
    computed_total_price_formatted = serializers.CharField(read_only=True)

    class Meta:
        model = TicketOrderProxy
        fields = '__all__'


class FoodOrderSerializer(serializers.ModelSerializer):
    customer_info = serializers.JSONField(source='get_customer_info', read_only=True)
    fullname = serializers.CharField(read_only=True)
    phone = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    total_price = serializers.CharField(read_only=True)

    class Meta:
        model = FoodOrderProxy
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    processed_data = serializers.JSONField(read_only=True)

    class Meta:
        model = CommentProxy
        fields = '__all__'


class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportProxy
        fields = '__all__'


class HalinkMenuSerializer(serializers.ModelSerializer):
    clean_title = serializers.CharField(read_only=True)

    class Meta:
        model = HalinkMenu
        fields = '__all__'
