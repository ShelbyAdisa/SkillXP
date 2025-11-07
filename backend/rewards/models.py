from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from users.models import School

User = get_user_model()

class RedeemableItem(models.Model):
    """
    Items that can be redeemed using XP points.
    """
    class ItemType(models.TextChoices):
        VIRTUAL = 'VIRTUAL', 'Virtual Badge/Item'
        DISCOUNT = 'DISCOUNT', 'Discount/Coupon'
        TANGIBLE = 'TANGIBLE', 'Tangible Prize'
        PRIVILEGE = 'PRIVILEGE', 'Privilege/Exemption'

    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="XP cost to redeem this item."
    )
    item_type = models.CharField(max_length=20, choices=ItemType.choices, default=ItemType.VIRTUAL)
    stock = models.IntegerField(default=-1, help_text="Number of items available. -1 means unlimited.")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='redeemable_items')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'redeemable_items'
        ordering = ['cost', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.cost} XP)"

class RewardTransaction(models.Model):
    """
    Records a user's redemption of an item.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Fulfillment'
        FULFILLED = 'FULFILLED', 'Fulfilled'
        CANCELED = 'CANCELED', 'Canceled'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reward_transactions')
    item = models.ForeignKey(RedeemableItem, on_delete=models.PROTECT)
    xp_spent = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    fulfillment_details = models.TextField(blank=True, null=True)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    fulfilled_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'reward_transactions'
        ordering = ['-redeemed_at']
    
    def __str__(self):
        return f"{self.user.get_display_name()} redeemed {self.item.name} for {self.xp_spent} XP"


