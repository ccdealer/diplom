# booking/serializers.py
from rest_framework import serializers
from .models import Agent, Guest, RoomType, Room, RoomCondition, Booking, BookingCard
from django.utils import timezone


# ==================== Agent Serializers ====================

class AgentListSerializer(serializers.ModelSerializer):
    """Список контрагентов"""
    bookings_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Agent
        fields = [
            'id', 'full_title', 'short_title', 'phone', 
            'is_active', 'bookings_count', 'created_at', "IIN_BIN"
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_bookings_count(self, obj):
        return obj.bookings.count()


class AgentDetailSerializer(serializers.ModelSerializer):
    """Детали контрагента"""
    bookings_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Agent
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_bookings_count(self, obj):
        return obj.bookings.count()


class AgentCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление контрагента"""
    
    class Meta:
        model = Agent
        fields = [
            'full_title', 'short_title', 'IIN_BIN', 'adress',
            'IBAN', 'BIC', 'phone', 'is_active'
        ]


# ==================== Guest Serializers ====================

class GuestListSerializer(serializers.ModelSerializer):
    """Список гостей"""
    nationality_name = serializers.CharField(source='nationality.nationality', read_only=True)
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Guest
        fields = [
            'id', 'full_name', 'phone', 'email', 'nationality',
            'nationality_name', 'age', 'blacklisted', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class GuestDetailSerializer(serializers.ModelSerializer):
    """Детали гостя"""
    nationality_name = serializers.CharField(source='nationality.nationality', read_only=True)
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    documents_list = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Guest
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_documents_list(self, obj):
        return [
            {
                'id': doc.id,
                'type': doc.get_document_type_display(),
                'number': doc.number,
                'IIN': doc.IIN
            }
            for doc in obj.documents.all()
        ]


class GuestCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление гостя"""
    
    class Meta:
        model = Guest
        fields = [
            'first_name', 'last_name', 'middle_name', 'nationality',
            'documents', 'phone', 'email', 'date_of_birth', 'gender',
            'blacklisted', 'blacklist_reason', 'notes'
        ]
    
    def validate_phone(self, value):
        """Валидация телефона"""
        instance = self.instance
        if Guest.objects.filter(phone=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Гость с таким номером телефона уже существует")
        return value
    
    def validate(self, data):
        """Комплексная валидация"""
        if data.get('blacklisted') and not data.get('blacklist_reason'):
            raise serializers.ValidationError({
                'blacklist_reason': 'Укажите причину добавления в чёрный список'
            })
        return data


# ==================== RoomType Serializers ====================

class RoomTypeListSerializer(serializers.ModelSerializer):
    """Список типов номеров"""
    rooms_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = RoomType
        fields = [
            'id', 'title', 'price', 'is_active', 
            'relevant_from', 'relevant_to', 'rooms_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_rooms_count(self, obj):
        return obj.rooms.count()


class RoomTypeDetailSerializer(serializers.ModelSerializer):
    """Детали типа номера"""
    
    class Meta:
        model = RoomType
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomTypeCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление типа номера"""
    
    class Meta:
        model = RoomType
        fields = ['title', 'price', 'relevant_from', 'relevant_to', 'description', 'is_active']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше нуля")
        return value
    
    def validate(self, data):
        if data.get('relevant_from') and data.get('relevant_to'):
            if data['relevant_from'] > data['relevant_to']:
                raise serializers.ValidationError({
                    'relevant_to': 'Дата окончания должна быть после даты начала'
                })
        return data


# ==================== Room Serializers ====================

class RoomListSerializer(serializers.ModelSerializer):
    """Список номеров"""
    room_types_list = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'room', 'floor', 'is_active', 'room_types_list'
        ]
        read_only_fields = ['id']
    
    def get_room_types_list(self, obj):
        return [
            {'id': rt.id, 'title': rt.title, 'price': float(rt.price)}
            for rt in obj.room_types.all()
        ]


class RoomDetailSerializer(serializers.ModelSerializer):
    """Детали номера"""
    room_types_list = serializers.SerializerMethodField(read_only=True)
    current_condition = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ['id']
    
    def get_room_types_list(self, obj):
        return [
            {
                'id': rt.id,
                'title': rt.title,
                'price': float(rt.price),
                'description': rt.description
            }
            for rt in obj.room_types.all()
        ]
    
    def get_current_condition(self, obj):
        condition = obj.get_current_condition()
        if condition:
            return {
                'id': condition.id,
                'condition': condition.condition,
                'color': condition.color
            }
        return None


class RoomCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление номера"""
    
    class Meta:
        model = Room
        fields = ['room', 'room_types', 'floor', 'is_active']
    
    def validate_room(self, value):
        """Валидация номера комнаты"""
        instance = self.instance
        if Room.objects.filter(room=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Номер с таким номером уже существует")
        return value


# ==================== RoomCondition Serializers ====================

class RoomConditionSerializer(serializers.ModelSerializer):
    """Сериализатор состояний номеров"""
    
    class Meta:
        model = RoomCondition
        fields = '__all__'
        read_only_fields = ['id']


# ==================== Booking Serializers ====================

class BookingListSerializer(serializers.ModelSerializer):
    """Список бронирований"""
    guest_name = serializers.CharField(source='guest.full_name', read_only=True, allow_null=True)
    agent_name = serializers.CharField(source='agent.short_title', read_only=True, allow_null=True)
    room_number = serializers.IntegerField(source='room.room', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration = serializers.DurationField(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'guest', 'guest_name', 'agent', 'agent_name',
            'room', 'room_number', 'status', 'status_display',
            'check_in', 'check_out', 'duration', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BookingDetailSerializer(serializers.ModelSerializer):
    """Детали бронирования"""
    guest_name = serializers.CharField(source='guest.full_name', read_only=True, allow_null=True)
    agent_name = serializers.CharField(source='agent.full_title', read_only=True, allow_null=True)
    room_number = serializers.IntegerField(source='room.room', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    duration = serializers.DurationField(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление бронирования"""
    
    class Meta:
        model = Booking
        fields = [
            'agent', 'guest', 'room', 'room_condition',
            'status', 'created_by', 'check_in', 'check_out', 'note'
        ]
    
    def validate(self, data):
        """Комплексная валидация"""
        if data.get('check_in') and data.get('check_out'):
            if data['check_in'] >= data['check_out']:
                raise serializers.ValidationError({
                    'check_out': 'Дата выезда должна быть позже даты заезда'
                })
        
        # Проверка гостя на чёрный список
        if data.get('guest'):
            can_book, reason = data['guest'].can_book()
            if not can_book:
                raise serializers.ValidationError({
                    'guest': f'Гость не может забронировать: {reason}'
                })
        
        return data


# ==================== BookingCard Serializers ====================

class BookingCardListSerializer(serializers.ModelSerializer):
    """Список карточек бронирования"""
    primary_guest_name = serializers.CharField(source='primary_guest.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_bookings = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = BookingCard
        fields = [
            'id', 'primary_guest', 'primary_guest_name',
            'status', 'status_display', 'total_amount',
            'total_bookings', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BookingCardDetailSerializer(serializers.ModelSerializer):
    """Детали карточки бронирования"""
    primary_guest_name = serializers.CharField(source='primary_guest.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    bookings_list = BookingListSerializer(source='bookings', many=True, read_only=True)
    total_bookings = serializers.IntegerField(read_only=True)
    total_goods_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_services_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    goods_list = serializers.SerializerMethodField(read_only=True)
    services_list = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = BookingCard
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_goods_list(self, obj):
        return [
            {'id': g.id, 'name': g.name, 'price': g.price}
            for g in obj.goods.all()
        ]
    
    def get_services_list(self, obj):
        return [
            {'id': s.id, 'name': s.name, 'price': s.price}
            for s in obj.services.all()
        ]


class BookingCardCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление карточки бронирования"""


    class Meta:
        model = BookingCard
        fields = [
            'primary_guest', 'bookings', 'goods',
            'services', 'status', 'total_amount'
        ]