"""
Serializers para tickets.
"""
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from .models import TicketType, Ticket, DiscountCode
from apps.events.serializers import EventListSerializer


class TicketTypeSerializer(serializers.ModelSerializer):
    """Serializer básico para tipos de ticket."""
    event_title = serializers.CharField(source='event.title', read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    sold_out = serializers.BooleanField(read_only=True)
    percentage_sold = serializers.FloatField(read_only=True)
    benefit_list = serializers.SerializerMethodField()

    class Meta:
        model = TicketType
        fields = [
            'id', 'event', 'event_title', 'name', 'description', 'price',
            'quantity', 'sold_count', 'available_quantity', 'min_purchase',
            'max_purchase', 'sale_start', 'sale_end', 'is_active',
            'is_available', 'sold_out', 'percentage_sold', 'benefits',
            'benefit_list', 'color', 'created_at'
        ]

    def get_benefit_list(self, obj):
        return obj.get_benefit_list()


class TicketTypeDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para tipos de ticket."""
    event = EventListSerializer(read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    sold_out = serializers.BooleanField(read_only=True)
    percentage_sold = serializers.FloatField(read_only=True)
    benefit_list = serializers.SerializerMethodField()

    class Meta:
        model = TicketType
        fields = [
            'id', 'event', 'name', 'description', 'price', 'quantity',
            'sold_count', 'available_quantity', 'min_purchase', 'max_purchase',
            'sale_start', 'sale_end', 'is_active', 'is_available', 'sold_out',
            'percentage_sold', 'benefits', 'benefit_list', 'color',
            'created_at', 'updated_at'
        ]

    def get_benefit_list(self, obj):
        return obj.get_benefit_list()


class TicketSerializer(serializers.ModelSerializer):
    """Serializer básico para tickets."""
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    event_title = serializers.CharField(source='ticket_type.event.title', read_only=True)
    event_start_date = serializers.DateTimeField(source='ticket_type.event.start_date', read_only=True)
    buyer_name = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_type', 'ticket_type_name', 'event_title',
            'event_start_date', 'buyer', 'buyer_name', 'code', 'uuid',
            'status', 'attendee_name', 'attendee_email', 'attendee_phone',
            'purchase_price', 'discount_applied', 'final_price',
            'qr_code', 'pdf_ticket', 'purchased_at', 'used_at',
            'is_valid', 'can_be_cancelled'
        ]
        read_only_fields = ['code', 'uuid', 'qr_code', 'pdf_ticket', 'purchased_at']

    def get_buyer_name(self, obj):
        return obj.buyer.get_full_name() or obj.buyer.username


class TicketDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para tickets."""
    ticket_type = TicketTypeSerializer(read_only=True)
    buyer_name = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    discount_code_value = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_type', 'buyer', 'buyer_name', 'code', 'uuid',
            'status', 'attendee_name', 'attendee_email', 'attendee_phone',
            'purchase_price', 'discount_applied', 'discount_code',
            'discount_code_value', 'final_price', 'qr_code', 'pdf_ticket',
            'purchased_at', 'used_at', 'cancelled_at', 'notes',
            'is_valid', 'can_be_cancelled'
        ]

    def get_buyer_name(self, obj):
        return obj.buyer.get_full_name() or obj.buyer.username

    def get_discount_code_value(self, obj):
        if obj.discount_code:
            return obj.discount_code.code
        return None


class TicketPurchaseSerializer(serializers.Serializer):
    """Serializer para compra de tickets."""
    ticket_type = serializers.PrimaryKeyRelatedField(queryset=TicketType.objects.all())
    quantity = serializers.IntegerField(min_value=1)
    attendee_name = serializers.CharField(max_length=200)
    attendee_email = serializers.EmailField()
    attendee_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    discount_code = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate(self, data):
        """Validaciones de compra."""
        ticket_type = data['ticket_type']
        quantity = data['quantity']
        
        # Verificar disponibilidad
        if not ticket_type.is_available:
            raise serializers.ValidationError("Este tipo de ticket no está disponible.")
        
        # Verificar cantidad disponible
        if quantity > ticket_type.available_quantity:
            raise serializers.ValidationError(
                f"Solo hay {ticket_type.available_quantity} tickets disponibles."
            )
        
        # Verificar límites de compra
        if quantity < ticket_type.min_purchase:
            raise serializers.ValidationError(
                f"La compra mínima es de {ticket_type.min_purchase} tickets."
            )
        
        if quantity > ticket_type.max_purchase:
            raise serializers.ValidationError(
                f"La compra máxima es de {ticket_type.max_purchase} tickets."
            )
        
        # Validar código de descuento si se proporciona
        if data.get('discount_code'):
            try:
                discount = DiscountCode.objects.get(
                    code=data['discount_code'],
                    event=ticket_type.event
                )
                
                if not discount.is_valid:
                    raise serializers.ValidationError("El código de descuento no es válido.")
                
                user = self.context['request'].user
                if not discount.can_be_used_by_user(user):
                    raise serializers.ValidationError(
                        "Has alcanzado el límite de uso para este código."
                    )
                
                # Verificar si el código aplica a este tipo de ticket
                if discount.applicable_ticket_types.exists():
                    if ticket_type not in discount.applicable_ticket_types.all():
                        raise serializers.ValidationError(
                            "Este código no aplica para este tipo de ticket."
                        )
                
                data['discount_obj'] = discount
                
            except DiscountCode.DoesNotExist:
                raise serializers.ValidationError("El código de descuento no existe.")
        
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Crear tickets con transacción atómica."""
        ticket_type = validated_data['ticket_type']
        quantity = validated_data['quantity']
        user = self.context['request'].user
        discount_code = validated_data.get('discount_code')
        discount_obj = validated_data.get('discount_obj')
        
        tickets = []
        
        for _ in range(quantity):
            # Calcular precio con descuento
            price = ticket_type.price
            discount_applied = 0
            
            if discount_obj:
                discount_applied = discount_obj.calculate_discount(price)
            
            # Crear ticket
            ticket = Ticket.objects.create(
                ticket_type=ticket_type,
                buyer=user,
                attendee_name=validated_data['attendee_name'],
                attendee_email=validated_data['attendee_email'],
                attendee_phone=validated_data.get('attendee_phone', ''),
                purchase_price=price,
                discount_applied=discount_applied,
                discount_code=discount_obj
            )
            tickets.append(ticket)
        
        # Actualizar contador de vendidos
        ticket_type.sold_count += quantity
        ticket_type.save(update_fields=['sold_count'])
        
        # Actualizar contador de uso del código de descuento
        if discount_obj:
            discount_obj.used_count += 1
            discount_obj.save(update_fields=['used_count'])
        
        return tickets


class DiscountCodeSerializer(serializers.ModelSerializer):
    """Serializer para códigos de descuento."""
    event_title = serializers.CharField(source='event.title', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    remaining_uses = serializers.IntegerField(read_only=True)

    class Meta:
        model = DiscountCode
        fields = [
            'id', 'event', 'event_title', 'code', 'description',
            'discount_type', 'discount_value', 'max_uses', 'used_count',
            'remaining_uses', 'max_uses_per_user', 'valid_from',
            'valid_until', 'is_active', 'is_valid', 'minimum_purchase',
            'applicable_ticket_types', 'created_at'
        ]

    def validate_code(self, value):
        """Validar que el código sea único."""
        if self.instance:
            # Si estamos actualizando, excluir la instancia actual
            if DiscountCode.objects.filter(code=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Este código ya existe.")
        else:
            if DiscountCode.objects.filter(code=value).exists():
                raise serializers.ValidationError("Este código ya existe.")
        return value.upper()

    def validate(self, data):
        """Validaciones adicionales."""
        if data.get('valid_from') and data.get('valid_until'):
            if data['valid_until'] <= data['valid_from']:
                raise serializers.ValidationError(
                    "La fecha de fin debe ser posterior a la fecha de inicio."
                )
        
        if data.get('discount_type') == 'percentage':
            if data.get('discount_value', 0) > 100:
                raise serializers.ValidationError(
                    "El descuento porcentual no puede ser mayor a 100%."
                )
        
        return data


class TicketValidationSerializer(serializers.Serializer):
    """Serializer para validar tickets."""
    code = serializers.CharField(max_length=50, required=False)
    uuid = serializers.UUIDField(required=False)

    def validate(self, data):
        if not data.get('code') and not data.get('uuid'):
            raise serializers.ValidationError(
                "Debe proporcionar el código o UUID del ticket."
            )
        return data