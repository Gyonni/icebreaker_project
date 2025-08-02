from django import forms
from .models import Person
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
import os

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Person
        # [수정] bio 대신 새로운 필드들을 포함시킵니다.
        fields = [
            'name', 'fun_fact', 'profile_image',
            'bio_q1_answer', 'bio_q2_answer', 'bio_q3_answer', 'prayer_request',
            'sentence1', 'sentence2', 'sentence3', 'sentence4', 'lie_answer'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'fun_fact': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'bio_q1_answer': forms.TextInput(attrs={'class': 'form-control'}),
            'bio_q2_answer': forms.TextInput(attrs={'class': 'form-control'}),
            'bio_q3_answer': forms.TextInput(attrs={'class': 'form-control'}),
            'prayer_request': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sentence1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '첫 번째 문장'}),
            'sentence2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '두 번째 문장'}),
            'sentence3': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '세 번째 문장'}),
            'sentence4': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '네 번째 문장'}),
            'lie_answer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '이름',
            'fun_fact': '재미있는 사실',
            'profile_image': '프로필 사진',
            'bio_q1_answer': '답변 1',
            'bio_q2_answer': '답변 2',
            'bio_q3_answer': '답변 3',
            'prayer_request': '기도제목을 나눠주세요',
            'sentence1': '문장 1', 'sentence2': '문장 2',
            'sentence3': '문장 3', 'sentence4': '문장 4', 
            'lie_answer': '몇 번 문장이 거짓말인가요?',
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