import os
import django

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental_motor_project.settings')
django.setup()

from django.contrib.auth.models import User
from rental.models import Motor, UserProfile

def seed_data():
    print("--- Memulai Proses Seeding Database ---")

    # 1. Create Superuser / Admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@motorent.com',
            'first_name': 'Admin',
            'last_name': 'MotoRent',
            'is_superuser': True,
            'is_staff': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Admin user dibuat: admin (password: admin123)")
    else:
        print("Admin user sudah ada.")

    # Update admin profile
    admin_profile = admin_user.profile
    admin_profile.role = 'admin'
    admin_profile.phone_number = '081111111111'
    admin_profile.address = 'Kantor Pusat MotoRent Jakarta'
    admin_profile.save()

    # 2. Create Regular User
    regular_user, created = User.objects.get_or_create(
        username='pengguna',
        defaults={
            'email': 'pengguna@gmail.com',
            'first_name': 'Budi',
            'last_name': 'Santoso'
        }
    )
    if created:
        regular_user.set_password('user123')
        regular_user.save()
        print("Regular user dibuat: pengguna (password: user123)")
    else:
        print("Regular user sudah ada.")

    # Update regular user profile
    user_profile = regular_user.profile
    user_profile.role = 'user'
    user_profile.phone_number = '081234567890'
    user_profile.address = 'Jl. Sukaluyu No. 12, Bandung'
    user_profile.save()

    # 3. Create Motors
    motors_data = [
        {
            'name': 'Vario 160',
            'brand': 'Honda',
            'plate_number': 'B 1234 ABC',
            'price_per_day': 100000.00,
            'status': 'available',
            'image_url': 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&q=80&w=400',
            'description': 'Motor matic premium 160cc, nyaman untuk perjalanan perkotaan, bagasi luas, dan sangat irit bahan bakar.'
        },
        {
            'name': 'NMAX 155',
            'brand': 'Yamaha',
            'plate_number': 'B 5678 XYZ',
            'price_per_day': 120000.00,
            'status': 'available',
            'image_url': 'https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?auto=format&fit=crop&q=80&w=400',
            'description': 'Motor matic bongsor yang sangat nyaman dikendarai, posisi berkendara ergonomis, suspensi empuk, dan bagasi besar.'
        },
        {
            'name': 'CBR150R',
            'brand': 'Honda',
            'plate_number': 'B 9012 DEF',
            'price_per_day': 180000.00,
            'status': 'available',
            'image_url': 'https://images.unsplash.com/photo-1622185135505-2d795003994a?auto=format&fit=crop&q=80&w=400',
            'description': 'Motor sport 150cc dengan tampilan agresif dan handling tajam, cocok untuk Anda yang menyukai performa dan kecepatan.'
        },
        {
            'name': 'KLX 150',
            'brand': 'Kawasaki',
            'plate_number': 'B 3456 GHI',
            'price_per_day': 150000.00,
            'status': 'available',
            'image_url': 'https://images.unsplash.com/photo-1599819811279-d5ad9cccf838?auto=format&fit=crop&q=80&w=400',
            'description': 'Motor trail tangguh, siap melibas segala medan jalanan rusak maupun jalur off-road ringan.'
        }
    ]

    for m_data in motors_data:
        motor, created = Motor.objects.get_or_create(
            plate_number=m_data['plate_number'],
            defaults=m_data
        )
        if created:
            print(f"Motor ditambahkan: {motor.brand} {motor.name} ({motor.plate_number})")
        else:
            # Update data jika sudah ada
            for key, val in m_data.items():
                setattr(motor, key, val)
            motor.save()
            print(f"Motor diperbarui: {motor.brand} {motor.name} ({motor.plate_number})")

    print("--- Proses Seeding Selesai Sukses! ---")

if __name__ == '__main__':
    seed_data()
