from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.db.models import Count
from .models import Complaint, Category
from .serializers import ComplaintSerializer, CategorySerializer


class IsStaffOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff_member or obj.complainant == request.user


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Complaint.objects.all() if user.is_staff_member else Complaint.objects.filter(complainant=user)
        for field in ['status', 'priority', 'type']:
            val = self.request.query_params.get(field)
            if val:
                qs = qs.filter(**{field: val})
        return qs

    def perform_create(self, serializer):
        serializer.save(complainant=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        qs = Complaint.objects.all() if user.is_staff_member else Complaint.objects.filter(complainant=user)
        return Response({
            'total': qs.count(),
            'pending': qs.filter(status='pending').count(),
            'resolved': qs.filter(status='resolved').count(),
            'by_category': list(qs.values('category__name').annotate(count=Count('id'))),
        })


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.pk,
                         'username': user.username, 'role': user.role})