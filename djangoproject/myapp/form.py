from django import forms
from .models import Boletin

class CreateRequerimiento(forms.Form):
    objetivo=forms.CharField(label='Objetivo principal',max_length=255)
    regiones=forms.CharField(label='Regiones involucradas',max_length=255)
    descripcion=forms.CharField(label='descripcion general',widget=forms.Textarea)

class CreateBoletin(forms.ModelForm):
    class Meta:
        model = Boletin
        fields = ['titulo', 'descripcion', 'archivo_pdf','requerimiento'] 

class CreateFuente(forms.Form):
    enlace = forms.CharField(label='Enlace',max_length=500)