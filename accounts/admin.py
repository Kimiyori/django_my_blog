from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from .forms import UserCreationForm, UserChangeForm
import json
from django.contrib.auth.models import Permission

# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ['username', 'email', 'password', ]
    list_filter = ('is_superuser',)
    
    fieldsets = (
        (None, {'fields': ('email', 'is_active','is_staff', 'is_superuser', 'password')}),
        ('Personal info', {'fields': ('username', )}),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('user_permissions',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'is_staff',
         'is_superuser', 'password', 'password2')}),
        ('Personal info', {'fields': ('username', )}),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('user_permissions',)}),
    )
    
    search_fields = ('email', 'username',)
    ordering = ('email',)
    filter_horizontal = ()

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'user_permissions':
            kwargs['queryset'] = Permission.objects.all(
            ).select_related('content_type')
        return super(CustomUserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super(CustomUserAdmin, self).save_model(request, obj, form, change)
        


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin): 

    list_display = ['user', 'photo', 'info']
