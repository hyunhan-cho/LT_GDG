# account/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Company, Department


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 1

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'industry', 'department_count', 'employee_count', 'created_at')
    search_fields = ('name', 'registration_number')
    list_filter = ('industry',)
    inlines = [DepartmentInline]  # 회사 상세 페이지 하단에 부서 관리 추가

    def department_count(self, obj):
        return obj.departments.count()
    department_count.short_description = '부서 수'

    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = '직원 수'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'company', 'member_count', 'created_at')
    list_filter = ('company',)  # 회사별로 필터링 가능
    search_fields = ('name', 'code', 'company__name')
    ordering = ('company', 'name')

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = '소속 직원 수'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 
        'korean_name', 
        'employee_id', 
        'company', 
        'department', 
        'is_active', 
        'date_joined'
    )
    list_filter = ('company', 'department', 'is_active', 'is_staff')
    search_fields = ('username', 'korean_name', 'employee_id', 'company__name', 'department__name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('회사 및 직무 정보', {
            'fields': ('company', 'department', 'employee_id', 'korean_name', 'phone_number', 'birth_date')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('회사 및 직무 정보', {
            'classes': ('wide',),
            'fields': ('korean_name', 'employee_id', 'company', 'department', 'email'),
        }),
    )