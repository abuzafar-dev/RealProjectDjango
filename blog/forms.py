from django import forms

from blog.models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'text']
        labels = {'title': 'Sarlavha', 'category': 'Kategoriya', 'text': 'Matn'}
        help_texts = {
            'text': "Bo'sh qator — yangi xatboshi. ## — kichik sarlavha. "
                    "Kod uchun ```python ... ``` yoki `qisqa kod` ishlating.",
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': "Masalan: Django'da birinchi model"}),
            'text': forms.Textarea(attrs={'rows': 14, 'class': 'is-mono'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Kategoriyasiz'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Izoh'}
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': "Fikringiz yoki savolingizni yozing..."}),
        }
