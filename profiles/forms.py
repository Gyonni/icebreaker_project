from django import forms
from .models import Person
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
import os

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Person
        # [수정] 3T1L 필드들을 추가합니다.
        fields = [
            'name', 'bio', 'fun_fact', 'profile_image',
            'truth1', 'truth2', 'truth3', 'lie', 'lie_answer'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fun_fact': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            # 3T1L 필드에 대한 위젯 추가
            'truth1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '진실 1'}),
            'truth2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '진실 2'}),
            'truth3': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '진실 3'}),
            'lie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '거짓말'}),
            'lie_answer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '이름', 'bio': '소개', 'fun_fact': '재미있는 사실',
            'profile_image': '프로필 사진', 'truth1': '진실 1', 'truth2': '진실 2',
            'truth3': '진실 3', 'lie': '거짓말', 'lie_answer': '어떤 문장이 거짓말인가요?',
        }

    def clean_profile_image(self, *args, **kwargs):
        image = self.cleaned_data.get("profile_image")
        if not image:
            return image
        try:
            img = Image.open(image)
            img = ImageOps.exif_transpose(img)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            filename_base = os.path.splitext(image.name)[0]
            new_filename = f"{filename_base}_processed.jpg"
            new_image = ContentFile(buffer.read(), name=new_filename)
            return new_image
        except Exception as e:
            raise forms.ValidationError(f"이미지 처리 중 오류가 발생했습니다: {e}")