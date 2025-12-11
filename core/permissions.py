"""
Permisos personalizados para EventHub.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado: solo el propietario puede editar.
    """
    def has_object_permission(self, request, view, obj):
        # Los métodos de lectura están permitidos para cualquiera
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # El propietario puede modificar
        return obj.created_by == request.user


class IsEventOrganizer(permissions.BasePermission):
    """
    Permiso personalizado: solo el organizador del evento puede modificarlo.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verificar si el objeto es un evento
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        
        # Si el objeto tiene relación con evento
        if hasattr(obj, 'event'):
            return obj.event.organizer == request.user
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado: solo administradores pueden modificar.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff


class IsAttendeeOwner(permissions.BasePermission):
    """
    Permiso personalizado: solo el usuario puede ver/modificar su información de asistente.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        return obj.user == request.user