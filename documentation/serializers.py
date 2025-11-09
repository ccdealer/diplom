# documentation/serializers.py
from rest_framework import serializers
from django.utils import timezone


from documentation.models import Nationality, Document


class NationalitySerializer(serializers.ModelSerializer):
    """Сериализатор для национальностей"""
    documents_count = serializers.SerializerMethodField(read_only=True)
    guests_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Nationality
        fields = ['id', 'nationality', 'code', 'documents_count', 'guests_count']
        read_only_fields = ['id']
    
    def get_documents_count(self, obj):
        """Количество документов"""
        return obj.documents.count()
    
    def get_guests_count(self, obj):
        """Количество гостей"""
        return obj.guests.count()


class DocumentListSerializer(serializers.ModelSerializer):
    """Упрощённый сериализатор для списка документов"""
    nationality_name = serializers.CharField(source='nationality.nationality', read_only=True)
    full_name = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'IIN', 'full_name', 'nationality', 'nationality_name',
            'document_type', 'document_type_display', 'number',
            'issued_date', 'expiry_date', 'is_expired', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор документа"""
    nationality_name = serializers.CharField(source='nationality.nationality', read_only=True)
    nationality_code = serializers.CharField(source='nationality.code', read_only=True)
    full_name = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'nationality', 'nationality_name', 'nationality_code',
            'IIN', 'first_name', 'last_name', 'middle_name', 'full_name',
            'date_of_birth', 'document_type', 'document_type_display', 'number',
            'file', 'url', 'issued_date', 'expiry_date', 'issued_by',
            'uploaded_at', 'updated_at', 'notes',
            'is_expired', 'days_until_expiry', 'is_expiring_soon'
        ]
        read_only_fields = ['id', 'uploaded_at', 'updated_at']


class DocumentCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления документа"""
    
    class Meta:
        model = Document
        fields = [
            'nationality', 'IIN', 'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'document_type', 'number', 'file', 'url',
            'issued_date', 'expiry_date', 'issued_by', 'notes'
        ]
    
    def validate_IIN(self, value):
        """Проверка уникальности и формата ИИН"""
        if not value.isdigit():
            raise serializers.ValidationError("ИИН должен содержать только цифры")
        if len(value) != 12:
            raise serializers.ValidationError("ИИН должен содержать ровно 12 цифр")
        
        # Проверка уникальности
        instance = self.instance
        if Document.objects.filter(IIN=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Документ с таким ИИН уже существует")
        
        return value
    
    def validate(self, data):
        """Комплексная валидация"""
        # Проверка дат
        if data.get('issued_date') and data.get('expiry_date'):
            if data['issued_date'] >= data['expiry_date']:
                raise serializers.ValidationError({
                    'expiry_date': 'Срок действия должен быть позже даты выдачи'
                })
        
        if data.get('date_of_birth') and data.get('issued_date'):
            if data['date_of_birth'] >= data['issued_date']:
                raise serializers.ValidationError({
                    'issued_date': 'Дата выдачи должна быть позже даты рождения'
                })
        
        # Проверка соответствия ИИН и даты рождения
        if data.get('IIN') and data.get('date_of_birth'):
            try:
                iin = data['IIN']
                year = int(iin[0:2])
                month = int(iin[2:4])
                day = int(iin[4:6])
                
                century_digit = int(iin[6])
                if century_digit in [3, 4]:
                    year += 1900
                elif century_digit in [5, 6]:
                    year += 2000
                
                from datetime import date
                iin_date = date(year, month, day)
                
                if iin_date != data['date_of_birth']:
                    raise serializers.ValidationError({
                        'IIN': f'ИИН не соответствует дате рождения. По ИИН: {iin_date}'
                    })
            except (ValueError, IndexError):
                pass  # Если не можем распарсить, пропускаем
        
        return data