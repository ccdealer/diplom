# ameneties/serializers.py
from rest_framework import serializers
from .models import Goods, Services


# ==================== Goods Serializers ====================

class GoodsListSerializer(serializers.ModelSerializer):
    """Список товаров"""
    
    class Meta:
        model = Goods
        fields = ['id', 'name', 'price', 'relevant_from', 'relevant_to']
        read_only_fields = ['id']


class GoodsDetailSerializer(serializers.ModelSerializer):
    """Детали товара"""
    
    class Meta:
        model = Goods
        fields = '__all__'
        read_only_fields = ['id']


class GoodsCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление товара"""
    
    class Meta:
        model = Goods
        fields = ['name', 'price', 'relevant_from', 'relevant_to']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше нуля")
        return value
    
    def validate(self, data):
        """Комплексная валидация"""
        if data.get('relevant_from') and data.get('relevant_to'):
            if data['relevant_from'] > data['relevant_to']:
                raise serializers.ValidationError({
                    'relevant_to': 'Дата окончания должна быть после даты начала'
                })
        return data


# ==================== Services Serializers ====================

class ServicesListSerializer(serializers.ModelSerializer):
    """Список услуг"""
    
    class Meta:
        model = Services
        fields = ['id', 'name', 'price', 'relevant_from', 'relevant_to']
        read_only_fields = ['id']


class ServicesDetailSerializer(serializers.ModelSerializer):
    """Детали услуги"""
    
    class Meta:
        model = Services
        fields = '__all__'
        read_only_fields = ['id']


class ServicesCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление услуги"""
    
    class Meta:
        model = Services
        fields = ['name', 'price', 'relevant_from', 'relevant_to']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше нуля")
        return value
    
    def validate(self, data):
        """Комплексная валидация"""
        if data.get('relevant_from') and data.get('relevant_to'):
            if data['relevant_from'] > data['relevant_to']:
                raise serializers.ValidationError({
                    'relevant_to': 'Дата окончания должна быть после даты начала'
                })
        return data