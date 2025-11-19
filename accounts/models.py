# account/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="회사명")
    registration_number = models.CharField(max_length=20, unique=True, verbose_name="사업자등록번호")
    industry = models.CharField(max_length=50, blank=True, null=True, verbose_name="업종")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="가입일")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "회사"
        verbose_name_plural = "회사 목록"


class Department(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments', verbose_name="소속 회사")
    code = models.CharField(max_length=20, verbose_name="부서코드")
    name = models.CharField(max_length=50, verbose_name="부서명")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일", null=True)
    def __str__(self):
        return f"[{self.company.name}] {self.name}"

    class Meta:
        verbose_name = "부서"
        verbose_name_plural = "부서 목록"
        constraints = [
            models.UniqueConstraint(fields=['company', 'code'], name='unique_dept_code_per_company')
        ]


class User(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees', null=True, blank=True, verbose_name="소속 회사")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='members', verbose_name="소속 부서")
    
    employee_id = models.CharField(max_length=50, verbose_name="사원번호") # 사번
    birth_date = models.DateField(null=True, blank=True, verbose_name="생년월일")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="전화번호")
    korean_name = models.CharField(max_length=30, verbose_name="직원명")

    def __str__(self):
        return f"[{self.company.name if self.company else '무소속'}] {self.korean_name} ({self.username})"

    class Meta:
        verbose_name = "직원(사용자)"
        verbose_name_plural = "직원 목록"
        constraints = [
            models.UniqueConstraint(fields=['company', 'employee_id'], name='unique_employee_id_per_company')
        ]

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    status_message = models.CharField(max_length=100, blank=True, default="")
    
    total_calls = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.korean_name}의 프로필"