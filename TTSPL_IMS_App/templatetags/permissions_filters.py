from django import template

register = template.Library()

@register.filter(name='has_permission')
def has_permission(user, permission_name):
    # If the user is a superuser, they have all permissions
    if user.is_superuser:
        return True
    # Otherwise, check if the user has the specific permission
    return user.has_permission(permission_name)



@register.filter(name='has_role')
def has_role(user, role_name):
    # If the user is a superuser, they have all roles
    if user.is_superuser:
        return True
    # Otherwise, check if the user has the specific role
    return user.has_role(role_name)
