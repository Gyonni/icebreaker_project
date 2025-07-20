from django import forms
from .models import Person

class PersonEditForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['bio', 'fun_fact']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5, 'class': 'w-full p-2 border rounded-md focus:ring-purple-500 focus:border-purple-500'}),
            'fun_fact': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-md focus:ring-purple-500 focus:border-purple-500'}),
        }
        labels = {
            'bio': '자기소개',
            'fun_fact': 'TMI / Fun Fact! 🥳',
        }