from django.test import TestCase, Client
from django.urls import reverse
from myapp.models import Requerimiento
from django.contrib.auth.models import User

class TestIA(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_ia = reverse("resumir_texto")
        cls.staff = User.objects.create_user(username='test', password='contrasena',is_staff=True)
        
    def setUp(self):
        self.client.login(username='test', password='contrasena')
        
    
    def test_texto_caracteres_especiales(self):
        #texto largo
        texto = 'En un pequeño pueblo llamado Ñuñoa, vivía Ana, una niña curiosa y llena de energía 🚀. Cada mañana, al despertar, pensaba en las maravillas del universo: desde el ∞ infinito hasta la misteriosa fórmula √(x² + y²) = z, que le enseñó su abuelo, un viejo matemático 👴. Ana amaba las historias que terminaban con un signo de interrogación ¿Por qué? —se preguntaba— porque en la vida todo tiene un porqué. En su cuaderno, anotaba palabras en varios idiomas: 你好, привет, مرحبا, junto a emoticones como 😂 y 🎉 que usaba para expresar alegría o sorpresa. Le fascinaba cómo el mundo está lleno de símbolos, desde el © copyright hasta el ™ de sus marcas favoritas. Un día, mientras exploraba el bosque cercano, encontró un libro antiguo con páginas llenas de «secretos» y ecuaciones, y supo que su aventura apenas comenzaba…'
        response = self.client.post(self.url_ia,{
            'texto': texto
        })
        
        self.assertEqual(response.status_code, 200)#Funcionó bien, renderizó->IA devolvió un texto.
        
        #Resúmen retornado por IA.
        resumen = response.context['resumen']
        print(resumen)
        #Resumen no vacío
        self.assertTrue(resumen.strip())
        
        #Texto tenga un largo mayo a algo
        self.assertGreater(len(resumen),15)
        
        #Que tenga palabras clave ana, abuelo, ñuñoa.
        palabras_clave = ["ana","ñuñoa","símbolos"]
        self.assertTrue(any(palabra in resumen.lower() for palabra in palabras_clave))
        
        

    
    def test_texto_largo(self):
        #texto largo
        texto = 'palabra'*3000
        
        #Envía un texto largo.
        response = self.client.post(self.url_ia,{
                'texto': texto
        })
            
        #No se cae la página, te renderiza igual    
        self.assertEqual(response.status_code, 200)

        #Verifica si la respuesta por parte de la IA es un mensaje de error, si ERROR:
        # esta dentro del mensaje retornado por la IA, entonces significa que dio error. 
        self.assertIn("ERROR:",response.content.decode())
    
    @classmethod
    def tearDownClass(cls):
        cls.staff.delete()
        super().tearDownClass()