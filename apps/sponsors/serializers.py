"""
Serializers para patrocinadores.
"""
from rest_framework import serializers
from .models import SponsorTier, Sponsor, Sponsorship, SponsorBenefit
from apps.events.serializers import EventListSerializer


class SponsorTierSerializer(serializers.ModelSerializer):
    """Serializer para niveles de patrocinio."""
    sponsors_count = serializers.IntegerField(read_only=True)
    active_sponsorships_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SponsorTier
        fields = [
            'id', 'name', 'description', 'min_amount', 'max_amount',
            'color', 'icon', 'order', 'benefits_description',
            'is_active', 'sponsors_count', 'active_sponsorships_count',
            'created_at'
        ]


class SponsorSerializer(serializers.ModelSerializer):
    """Serializer básico para patrocinadores."""
    total_sponsorships = serializers.IntegerField(read_only=True)
    total_invested = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    tag_list = serializers.SerializerMethodField()

    class Meta:
        model = Sponsor
        fields = [
            'id', 'name', 'logo', 'description', 'industry',
            'contact_name', 'contact_email', 'contact_phone',
            'contact_position', 'website', 'facebook', 'twitter',
            'instagram', 'linkedin', 'tax_id', 'billing_address',
            'status', 'total_sponsorships', 'total_invested',
            'tags', 'tag_list', 'created_at'
        ]

    def get_tag_list(self, obj):
        return obj.get_tag_list()


class SponsorDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para patrocinadores."""
    total_sponsorships = serializers.IntegerField(read_only=True)
    total_invested = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    tag_list = serializers.SerializerMethodField()
    recent_sponsorships = serializers.SerializerMethodField()

    class Meta:
        model = Sponsor
        fields = [
            'id', 'name', 'logo', 'description', 'industry',
            'contact_name', 'contact_email', 'contact_phone',
            'contact_position', 'website', 'facebook', 'twitter',
            'instagram', 'linkedin', 'tax_id', 'billing_address',
            'status', 'notes', 'tags', 'tag_list', 'total_sponsorships',
            'total_invested', 'recent_sponsorships', 'created_at', 'updated_at'
        ]

    def get_tag_list(self, obj):
        return obj.get_tag_list()

    def get_recent_sponsorships(self, obj):
        sponsorships = obj.sponsorships.all().order_by('-created_at')[:5]
        return SponsorshipSerializer(sponsorships, many=True).data


class SponsorBenefitSerializer(serializers.ModelSerializer):
    """Serializer para beneficios de patrocinio."""
    benefit_type_display = serializers.CharField(
        source='get_benefit_type_display',
        read_only=True
    )

    class Meta:
        model = SponsorBenefit
        fields = [
            'id', 'sponsorship', 'benefit_type', 'benefit_type_display',
            'description', 'quantity', 'delivered', 'delivered_date',
            'proof_of_delivery', 'notes', 'created_at'
        ]
        read_only_fields = ['delivered_date']


class SponsorshipSerializer(serializers.ModelSerializer):
    """Serializer básico para patrocinios."""
    event_title = serializers.CharField(source='event.title', read_only=True)
    sponsor_name = serializers.CharField(source='sponsor.name', read_only=True)
    sponsor_logo = serializers.ImageField(source='sponsor.logo', read_only=True)
    tier_name = serializers.CharField(source='sponsor_tier.name', read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    benefits_delivered_count = serializers.IntegerField(read_only=True)
    benefits_pending_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Sponsorship
        fields = [
            'id', 'event', 'event_title', 'sponsor', 'sponsor_name',
            'sponsor_logo', 'sponsor_tier', 'tier_name', 'amount',
            'currency', 'status', 'is_active', 'start_date', 'end_date',
            'is_current', 'days_remaining', 'impressions', 'clicks',
            'leads_generated', 'benefits_delivered_count',
            'benefits_pending_count', 'created_at'
        ]


class SponsorshipDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para patrocinios."""
    event = EventListSerializer(read_only=True)
    sponsor = SponsorSerializer(read_only=True)
    sponsor_tier = SponsorTierSerializer(read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    roi_metrics = serializers.SerializerMethodField()
    benefits = SponsorBenefitSerializer(many=True, read_only=True)

    class Meta:
        model = Sponsorship
        fields = [
            'id', 'event', 'sponsor', 'sponsor_tier', 'amount', 'currency',
            'status', 'is_active', 'start_date', 'end_date',
            'contract_signed_date', 'contract_document', 'logo_placement',
            'booth_number', 'impressions', 'clicks', 'leads_generated',
            'notes', 'internal_notes', 'is_current', 'days_remaining',
            'roi_metrics', 'benefits', 'created_at', 'updated_at'
        ]

    def get_roi_metrics(self, obj):
        return obj.roi_metrics


class SponsorshipCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar patrocinios."""

    class Meta:
        model = Sponsorship
        fields = [
            'event', 'sponsor', 'sponsor_tier', 'amount', 'currency',
            'status', 'is_active', 'start_date', 'end_date',
            'contract_signed_date', 'contract_document', 'logo_placement',
            'booth_number', 'notes', 'internal_notes'
        ]

    def validate(self, data):
        """Validaciones personalizadas."""
        # Validar fechas
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError(
                    "La fecha de fin debe ser posterior a la fecha de inicio."
                )

        # Validar monto según tier
        if data.get('sponsor_tier') and data.get('amount'):
            tier = data['sponsor_tier']
            amount = data['amount']
            
            if amount < tier.min_amount:
                raise serializers.ValidationError(
                    f"El monto mínimo para {tier.name} es {tier.min_amount}"
                )
            
            if tier.max_amount and amount > tier.max_amount:
                raise serializers.ValidationError(
                    f"El monto máximo para {tier.name} es {tier.max_amount}"
                )

        return data


class SponsorshipROISerializer(serializers.Serializer):
    """Serializer para reporte de ROI."""
    sponsorship_id = serializers.IntegerField()
    sponsor_name = serializers.CharField()
    event_title = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    impressions = serializers.IntegerField()
    clicks = serializers.IntegerField()
    leads_generated = serializers.IntegerField()
    cpl = serializers.FloatField()
    ctr = serializers.FloatField()
    roi_score = serializers.FloatField()