from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import RedeemableItem, RewardTransaction
from .serializers import RedeemableItemSerializer, RewardTransactionSerializer, RedeemRequestSerializer
from .permissions import IsStudent, CanManageRewards
from users.models import User 

class RedeemableItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing and managing redeemable items.
    Allows listing all active items.
    """
    serializer_class = RedeemableItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['item_type', 'is_active']
    
    def get_queryset(self):
        # Only show active items for the user's school
        return RedeemableItem.objects.filter(school=self.request.user.school, is_active=True)

class RewardTransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing reward transactions.
    Students can only see their own. Managers can see all in the school.
    """
    serializer_class = RewardTransactionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'item', 'user']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # All authenticated users can view their own transactions
            return [permissions.IsAuthenticated()]
        # Only managers can perform create, update, destroy (for fulfillment)
        return [CanManageRewards()]

    def get_queryset(self):
        user = self.request.user
        if user.role in [User.Role.ADMIN, User.Role.SCHOOL_ADMIN, User.Role.TEACHER]:
            # Managers/Admins see all transactions in their school
            return RewardTransaction.objects.filter(user__school=user.school)
        else:
            # Other users (students/parents) only see their own
            return RewardTransaction.objects.filter(user=user)

    @action(detail=True, methods=['post'], permission_classes=[CanManageRewards])
    def fulfill(self, request, pk=None):
        """Action for an administrator to fulfill a pending transaction."""
        transaction_obj = self.get_object()
        
        if transaction_obj.status != RewardTransaction.Status.PENDING:
            return Response({"detail": "Transaction is already fulfilled or canceled."}, status=status.HTTP_400_BAD_REQUEST)
        
        transaction_obj.status = RewardTransaction.Status.FULFILLED
        transaction_obj.fulfilled_at = timezone.now()
        transaction_obj.fulfillment_details = request.data.get('fulfillment_details', 'Item fulfilled.')
        transaction_obj.save()
        
        return Response(RewardTransactionSerializer(transaction_obj, context={'request': request}).data)


class RedeemRewardView(generics.CreateAPIView):
    """
    API endpoint for a student to redeem a reward.
    """
    serializer_class = RedeemRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        item_id = serializer.validated_data['item_id']
        user = request.user
        
        try:
            item = RedeemableItem.objects.get(id=item_id, is_active=True)
        except RedeemableItem.DoesNotExist:
            return Response({"detail": "Invalid or inactive item."}, status=status.HTTP_404_NOT_FOUND)

        # Use a transaction to ensure atomicity of XP deduction and record creation/stock update
        with transaction.atomic():
            # Re-fetch user in transaction to ensure latest XP is checked (race condition mitigation)
            user = User.objects.select_for_update().get(pk=user.pk)
            
            if user.xp_points < item.cost:
                return Response({"detail": "Insufficient XP points."}, status=status.HTTP_400_BAD_REQUEST)

            # 1. Deduct XP
            user.xp_points -= item.cost
            user.save()
            
            # 2. Update stock
            if item.stock > 0:
                item.stock -= 1
                item.save()
            elif item.stock == 0:
                # Should have been caught by serializer, but safety check
                raise Exception("Item out of stock during transaction.")
            
            # 3. Create transaction record
            transaction_record = RewardTransaction.objects.create(
                user=user,
                item=item,
                xp_spent=item.cost,
                status=RewardTransaction.Status.PENDING
            )
        

        return Response({
            "message": f"Successfully redeemed {item.name} for {item.cost} XP.",
            "xp_remaining": user.xp_points,
            "transaction": RewardTransactionSerializer(transaction_record).data
        }, status=status.HTTP_201_CREATED)
