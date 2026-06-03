from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .models import Motor, Rental, UserProfile
from .forms import RegistrationForm, MotorForm, BookingForm
from datetime import date

# Helper decorator untuk membatasi akses khusus Admin
def admin_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Anda tidak memiliki hak akses ke halaman ini.")
        return redirect('dashboard')
    return _wrapped_view_func


# View Halaman Landing (Utama)
def landing_view(request):
    motors = Motor.objects.filter(status='available')[:6]
    return render(request, 'landing.html', {'motors': motors})


# View Registrasi Pengguna Baru
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Registrasi berhasil! Selamat datang, {user.username}.")
            return redirect('dashboard')
        else:
            messages.error(request, "Terjadi kesalahan dalam registrasi. Silakan periksa kembali data Anda.")
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


# View Login Pengguna
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Selamat datang kembali, {username}!")
                return redirect('dashboard')
        messages.error(request, "Username atau password salah.")
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})


# View Logout Pengguna
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Anda telah keluar dari akun.")
    return redirect('landing')


# View Dashboard Pusat (Mengalihkan berdasarkan Role)
@login_required
def dashboard_view(request):
    role = request.user.profile.role
    if role == 'admin':
        return admin_dashboard_view(request)
    return user_dashboard_view(request)


# View Dashboard Pengguna (User Dashboard)
@login_required
def user_dashboard_view(request):
    user = request.user
    active_rentals = Rental.objects.filter(user=user, status__in=['pending', 'approved']).order_by('-created_at')
    rental_history = Rental.objects.filter(user=user, status__in=['completed', 'cancelled']).order_by('-created_at')
    
    context = {
        'active_rentals': active_rentals,
        'rental_history': rental_history,
        'role': 'user'
    }
    return render(request, 'user/dashboard.html', context)


# View Dashboard Admin (Admin Dashboard)
@login_required
@admin_required
def admin_dashboard_view(request):
    total_motors = Motor.objects.count()
    available_motors = Motor.objects.filter(status='available').count()
    active_rentals_count = Rental.objects.filter(status='approved').count()
    pending_rentals_count = Rental.objects.filter(status='pending').count()
    
    # Hitung pendapatan kotor dari persewaan yang sudah selesai / aktif
    total_revenue = Rental.objects.filter(status__in=['approved', 'completed']).aggregate(total=Sum('total_price'))['total'] or 0

    recent_rentals = Rental.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_motors': total_motors,
        'available_motors': available_motors,
        'active_rentals_count': active_rentals_count,
        'pending_rentals_count': pending_rentals_count,
        'total_revenue': total_revenue,
        'recent_rentals': recent_rentals,
        'role': 'admin'
    }
    return render(request, 'admin/dashboard.html', context)


# --- FITUR PENGGUNA ---

# Menampilkan semua motor yang tersedia untuk disewa
@login_required
def motor_browse_view(request):
    motors = Motor.objects.filter(status='available')
    return render(request, 'user/motor_browse.html', {'motors': motors})


# Mengajukan booking motor
@login_required
def booking_create_view(request, motor_id):
    motor = get_object_or_404(Motor, id=motor_id)
    
    if motor.status != 'available':
        messages.error(request, "Maaf, motor ini tidak tersedia untuk disewa saat ini.")
        return redirect('motor_browse')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.user = request.user
            rental.motor = motor
            rental.status = 'pending'
            rental.save()
            
            # Ubah status motor menjadi rented jika disetujui (opsional, pada booking baru diset di admin)
            # Di sini kita biarkan 'available' sampai disetujui Admin, atau langsung di-block.
            # Agar motor tidak di-double book, biasanya langsung di-mark, tapi di sini status motor 
            # akan berubah menjadi 'rented' saat Admin menekan 'Approve' (Disetujui).
            
            messages.success(request, f"Pengajuan sewa motor {motor.name} berhasil dikirim! Menunggu persetujuan admin.")
            return redirect('dashboard')
    else:
        form = BookingForm()
    
    context = {
        'form': form,
        'motor': motor
    }
    return render(request, 'user/booking_form.html', context)


# Membatalkan booking (oleh pengguna jika masih pending)
@login_required
def booking_cancel_view(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    
    # Validasi kepemilikan sewa (kecuali admin)
    if rental.user != request.user and request.user.profile.role != 'admin':
        messages.error(request, "Anda tidak diizinkan membatalkan penyewaan ini.")
        return redirect('dashboard')

    if rental.status == 'pending':
        rental.status = 'cancelled'
        rental.save()
        messages.success(request, "Pengajuan penyewaan berhasil dibatalkan.")
    elif rental.status == 'approved' and request.user.profile.role == 'admin':
        # Admin membatalkan sewa yang sedang aktif
        rental.status = 'cancelled'
        rental.save()
        # Kembalikan status motor
        rental.motor.status = 'available'
        rental.motor.save()
        messages.success(request, "Penyewaan aktif berhasil dibatalkan.")
    else:
        messages.error(request, "Penyewaan tidak dapat dibatalkan pada status saat ini.")
        
    return redirect('dashboard')


# --- FITUR ADMIN: CRUD MOTOR ---

# List Motor (Admin)
@login_required
@admin_required
def motor_list_view(request):
    motors = Motor.objects.all().order_by('brand', 'name')
    return render(request, 'admin/motor_list.html', {'motors': motors})


# Tambah Motor Baru (Admin)
@login_required
@admin_required
def motor_create_view(request):
    if request.method == 'POST':
        form = MotorForm(request.POST)
        if form.is_valid():
            motor = form.save()
            messages.success(request, f"Motor {motor.name} berhasil ditambahkan!")
            return redirect('motor_list')
    else:
        form = MotorForm()
    return render(request, 'admin/motor_form.html', {'form': form, 'title': 'Tambah Motor Baru'})


# Edit Detail Motor (Admin)
@login_required
@admin_required
def motor_edit_view(request, motor_id):
    motor = get_object_or_404(Motor, id=motor_id)
    if request.method == 'POST':
        form = MotorForm(request.POST, instance=motor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Detail motor {motor.name} berhasil diperbarui!")
            return redirect('motor_list')
    else:
        form = MotorForm(instance=motor)
    return render(request, 'admin/motor_form.html', {'form': form, 'title': f'Edit Motor: {motor.name}', 'motor': motor})


# Hapus Motor (Admin)
@login_required
@admin_required
def motor_delete_view(request, motor_id):
    motor = get_object_or_404(Motor, id=motor_id)
    name = motor.name
    # Cek apakah motor sedang disewa
    active_rentals = Rental.objects.filter(motor=motor, status='approved')
    if active_rentals.exists():
        messages.error(request, f"Motor {name} tidak dapat dihapus karena sedang disewa aktif.")
    else:
        motor.delete()
        messages.success(request, f"Motor {name} berhasil dihapus.")
    return redirect('motor_list')


# --- FITUR ADMIN: KELOLA SEWA ---

# List Semua Transaksi Sewa (Admin)
@login_required
@admin_required
def rental_list_view(request):
    rentals = Rental.objects.all().order_by('-created_at')
    return render(request, 'admin/rental_list.html', {'rentals': rentals})


# Mengubah Status Rental (Approve, Complete, Cancel) oleh Admin
@login_required
@admin_required
def rental_update_status_view(request, rental_id, action):
    rental = get_object_or_404(Rental, id=rental_id)
    
    if action == 'approve':
        if rental.status == 'pending':
            # Pastikan motor masih tersedia
            if rental.motor.status == 'available':
                rental.status = 'approved'
                rental.save()
                
                # Ubah status motor menjadi rented/disewa
                rental.motor.status = 'rented'
                rental.motor.save()
                messages.success(request, f"Penyewaan #{rental.id} disetujui! Motor {rental.motor.name} sekarang berstatus disewa.")
            else:
                messages.error(request, f"Motor {rental.motor.name} sedang tidak tersedia (status: {rental.motor.get_status_display()}).")
        else:
            messages.error(request, "Transaksi tidak berstatus pending.")

    elif action == 'complete':
        if rental.status == 'approved':
            rental.status = 'completed'
            rental.save()
            
            # Kembalikan status motor menjadi available
            rental.motor.status = 'available'
            rental.motor.save()
            messages.success(request, f"Penyewaan #{rental.id} telah selesai! Motor {rental.motor.name} sekarang kembali tersedia.")
        else:
            messages.error(request, "Transaksi tidak berstatus aktif/disetujui.")

    elif action == 'cancel':
        if rental.status in ['pending', 'approved']:
            rental.status = 'cancelled'
            rental.save()
            
            # Jika dibatalkan saat sedang aktif (approved), kembalikan status motor
            if rental.motor.status == 'rented':
                rental.motor.status = 'available'
                rental.motor.save()
            messages.success(request, f"Penyewaan #{rental.id} telah dibatalkan.")
        else:
            messages.error(request, "Penyewaan tidak dapat dibatalkan.")
            
    return redirect('rental_list')


# --- FITUR ADMIN: MANAJEMEN PENGGUNA ---

# List Pengguna Terdaftar (Admin)
@login_required
@admin_required
def user_list_view(request):
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    return render(request, 'admin/user_list.html', {'users': users})
