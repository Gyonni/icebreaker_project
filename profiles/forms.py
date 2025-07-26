from django import forms
from .models import Person
from PIL import Image, ImageOps # ImageOps 추가
from io import BytesIO
from django.core.files.base import ContentFile
import os

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'bio', 'fun_fact', 'profile_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '이름'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '간단한 자기소개'}),
            'fun_fact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TMI, 재미있는 사실 한 가지!'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'name': '이름',
            'bio': '소개',
            'fun_fact': '재미있는 사실',
            'profile_image': '프로필 사진',
        }

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")

        # 새 이미지가 없거나 'clear' 체크박스가 선택된 경우
        if not image:
            return image

        try:
            # Pillow 라이브러리로 이미지 열기
            img = Image.open(image)

            # ★★★ 핵심 수정: EXIF 데이터를 읽어 이미지를 올바르게 회전 ★★★
            img = ImageOps.exif_transpose(img)

            # 이미지를 JPEG로 저장하기 위해 RGB 모드로 변환
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 이미지 비율을 유지하면서 최대 사이즈(1024x1024)로 리사이징
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

            # 리사이징된 이미지를 메모리 버퍼에 저장
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            
            # 새 파일 이름 만들기 (예: original_processed.jpg)
            filename_base = os.path.splitext(image.name)[0]
            new_filename = f"{filename_base}_processed.jpg"

            # 메모리 버퍼로부터 새로운 Django 파일 객체 생성
            new_image = ContentFile(buffer.read(), name=new_filename)
            
            return new_image
        except Exception as e:
            # 이미지 처리 중 오류가 발생하면 사용자에게 알림
            raise forms.ValidationError(f"이미지 처리 중 오류가 발생했습니다: {e}")
