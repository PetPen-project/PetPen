from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    message = 'users can only modify their own projects.'
    
    def has_object_permission(self, request, view, obj):
        # if request.method in permissions.SAFE_METHODS:
            # return True
        return obj.user == request.user

    def has_permission(self, request, view):
        return request.user.is_authenticated
