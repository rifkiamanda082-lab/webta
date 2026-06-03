from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Model Profile Pengguna (Menyimpan Role dan Informasi Tambahan)
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'Pengguna'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# Signal untuk Membuat & Menyimpan UserProfile secara otomatis saat User baru dibuat
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if instance.is_superuser or instance.is_staff else 'user'
        UserProfile.objects.create(user=instance, role=role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        role = 'admin' if instance.is_superuser or instance.is_staff else 'user'
        UserProfile.objects.create(user=instance, role=role)


# Model Motor
class Motor(models.Model):
    STATUS_CHOICES = [
        ('available', 'Tersedia'),
        ('rented', 'Disewa'),
        ('maintenance', 'Perawatan'),
    ]

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    plate_number = models.CharField(max_length=20, unique=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image_url = models.CharField(max_length=300, blank=True, null=True, default='/static/images/default_motor.jpg')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.plate_number})"


# Model Transaksi Rental/Booking
class Rental(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu Persetujuan'),
        ('approved', 'Disetujui / Aktif'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals')
    motor = models.ForeignKey(Motor, on_delete=models.CASCADE, related_name='rentals')
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def duration_days(self):
        delta = self.end_date - self.start_date
        return max(delta.days, 1)  # Minimal 1 hari sewa

    def save(self, *args, **kwargs):
        # Hitung total harga otomatis sebelum disimpan
        days = self.duration_days()
        self.total_price = self.motor.price_per_day * days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sewa #{self.id} - {self.user.username} - {self.motor.name}"
