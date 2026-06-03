from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Motor, Rental

# Form Registrasi Pengguna Baru
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True, label="Nama Depan")
    last_name = forms.CharField(max_length=30, required=True, label="Nama Belakang")
    phone_number = forms.CharField(max_length=15, required=True, label="Nomor Telepon")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True, label="Alamat Lengkap")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Update user profile with additional info
            profile = user.profile
            profile.phone_number = self.cleaned_data['phone_number']
            profile.address = self.cleaned_data['address']
            profile.save()
        return user


# Form CRUD Motor (Admin)
class MotorForm(forms.ModelForm):
    class Meta:
        model = Motor
        fields = ['name', 'brand', 'plate_number', 'price_per_day', 'status', 'image_url', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan nama motor (e.g. Vario 160)'}),
            'brand': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan merk motor (e.g. Honda)'}),
            'plate_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masukkan nomor plat (e.g. B 1234 ABC)'}),
            'price_per_day': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Harga per hari (Rp)'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'image_url': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'URL Gambar Motor'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Deskripsi singkat motor...'}),
        }


# Form Pemesanan/Booking Motor (Pengguna)
class BookingForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            from datetime import date
            if start_date < date.today():
                raise forms.ValidationError("Tanggal mulai sewa tidak boleh di masa lalu.")
            if end_date < start_date:
                raise forms.ValidationError("Tanggal selesai sewa harus setelah tanggal mulai.")
        return cleaned_data
