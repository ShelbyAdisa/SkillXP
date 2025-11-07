from rest_framework import serializers
from .models import RedeemableItem, RewardTransaction

class RedeemableItemSerializer(serializers.ModelSerializer):
    can_redeem = serializers.SerializerMethodField()
    
    class Meta:
        model = RedeemableItem
        fields = [
            'id', 'name', 'description', 'cost', 'item_type', 'stock', 
            'is_active', 'created_at', 'can_redeem'
        ]
        read_only_fields = ['created_at', 'updated_at', 'school']
        
    def get_can_redeem(self, obj):
       
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
            
        user_xp = request.user.xp_points
        is_in_stock = obj.stock == -1 or obj.stock > 0
        
        return user_xp >= obj.cost and is_in_stock

class RewardTransactionSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    
    class Meta:
        model = RewardTransaction
        fields = [
            'id', 'user', 'item', 'item_name', 'xp_spent', 'status', 
            'fulfillment_details', 'redeemed_at', 'fulfilled_at'
        ]
        read_only_fields = ['user', 'xp_spent', 'redeemed_at', 'fulfilled_at', 'item_name']

class RedeemRequestSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    
    def validate_item_id(self, value):
        try:
            item = RedeemableItem.objects.get(id=value, is_active=True)
            
            
            if item.stock == 0:
                raise serializers.ValidationError("This item is currently out of stock.")
            
          
            user = self.context['request'].user
            if user.xp_points < item.cost:
                raise serializers.ValidationError(f"You only have {user.xp_points} XP, but this item costs {item.cost} XP.")
            
            return value
        except RedeemableItem.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive item ID.")