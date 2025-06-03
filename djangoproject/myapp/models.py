from django.db import models
import json
# Create your models here.
    
class Requerimiento(models.Model):
    objetivo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    regiones = models.CharField(max_length=255)
    estados=models.IntegerField()
    
    def __str__(self):
        return str(self.objetivo) if self.objetivo else "Sin título"
    
class Boletin(models.Model):
    titulo = models.CharField(max_length=255)  # Título del boletín
    descripcion = models.TextField(blank=True)  # Descripción opcional del boletín
    archivo_pdf = models.FileField(upload_to='boletines_pdfs/')  # Campo para el archivo PDF
    fecha_creacion = models.DateField(auto_now_add=True)  # Fecha de publicación automática
    requerimiento = models.ForeignKey(Requerimiento,on_delete=models.CASCADE)
    es_publico = models.BooleanField(default=False)
    vistas=models.IntegerField(default=0)
    descargas=models.IntegerField(default=0)
    def __str__(self):
        return str(self.titulo) if self.titulo else "Sin título"

class Fuente(models.Model):
    enlace = models.CharField(max_length=500)  # Link de la fuente
    estado = models.IntegerField(default=1)
    def __str__(self):
        return str(self.enlace) if self.enlace else "Sin título"
    
class Resumen(models.Model):
    fuente = models.ForeignKey(Fuente,on_delete=models.CASCADE)
    etiquetas = models.TextField(default='[]')
    resumen = models.CharField(max_length=2500)
    estado = models.IntegerField(default=-1)

    def get_lista(self):
        try:
            return json.loads(self.lista_serializada)
        except json.JSONDecodeError:
            return []

    def set_lista(self, lista):
        self.lista_serializada = json.dumps(lista)