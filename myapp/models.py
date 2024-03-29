from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from .utils.common import document_upload_path


class UserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, phone_no, profile_pic, password=None, is_active=True,
                    is_admin=False, **extra_fields):
        if not email:
            raise ValueError('Please Enter Email')
        if not username:
            raise ValueError('Please Enter UserName')

        email = self.normalize_email(email)
        # username = self.model(username = username)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_no=phone_no,
            profile_pic=profile_pic,
            is_active=is_active,
            is_admin=is_admin,
        )
        user.set_password(password)
        # if password:  # If password is provided
        #     user.password = password
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=10, unique=True)
    username = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=4, primary_key=True)
    profile_pic = models.FileField(upload_to=document_upload_path)
    last_activity_time = models.DateTimeField(null=True, blank=True)
    # id=models.AutoField(unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # Generate user_id if it's a new user
        if not self.pk:
            last_user = User.objects.order_by('-user_id').first()
            if last_user:
                last_id = int(last_user.user_id[1:])
                self.user_id = 'U{:03d}'.format(last_id + 1)
            else:
                self.user_id = 'U001'

        super().save(*args, **kwargs)


class Grievance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gk_id = models.CharField(max_length=5, primary_key=True)
    username = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.gk_id:
            last_grievance = Grievance.objects.order_by('-gk_id').first()
            if last_grievance:
                last_id = int(last_grievance.gk_id[1:])  # Extract the numeric part
                new_id = f'G{last_id + 1:03}'  # Increment by 1 and format as 'G001'
            else:
                new_id = 'G001'  # If no grievance exists yet, start with 'G001'
            self.gk_id = new_id

        super(Grievance, self).save(*args, **kwargs)


class OTP(models.Model):
    key = models.EmailField()
    otp_secret = models.CharField(max_length=255)
    otp = models.CharField(max_length=10)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(null=True, blank=True)

