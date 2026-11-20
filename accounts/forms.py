from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Django's Uzbek locale does not cover auth validators, so the messages users
# actually see are translated here, keyed by (field, code) or just the code.
ERROR_MESSAGES = {
    ('username', 'unique'): 'Bu login band. Boshqasini tanlang.',
    ('username', 'invalid'): "Login faqat harf, raqam va @ . + - _ belgilaridan iborat bo'lishi mumkin.",
    ('email', 'invalid'): "Email noto'g'ri. Masalan: ali@mail.uz",
    'required': "Bu maydonni to'ldiring.",
    'password_too_short': "Parol juda qisqa: kamida 8 ta belgi bo'lsin.",
    'password_too_common': 'Bu parol juda oddiy, uni topish oson.',
    'password_entirely_numeric': "Parol faqat raqamlardan iborat bo'lmasin.",
    'password_too_similar': "Parol login yoki ismingizga juda o'xshash.",
    'password_mismatch': 'Ikkala parol bir xil emas.',
}


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']
        labels = {'username': 'Login', 'first_name': 'Ism'}
        help_texts = {'username': "Lotin harflari, raqamlar va @ . + - _ belgilari."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Parol'
        self.fields['password1'].help_text = "Kamida 8 ta belgi, faqat raqamlardan iborat bo'lmasin."
        self.fields['password2'].label = 'Parolni takrorlang'
        self.fields['password2'].help_text = ''

    def full_clean(self):
        super().full_clean()
        for field, errors in self.errors.as_data().items():
            self._errors[field] = self.error_class(
                [ERROR_MESSAGES.get((field, error.code)) or ERROR_MESSAGES.get(error.code, message)
                 for error in errors for message in error.messages],
            )
