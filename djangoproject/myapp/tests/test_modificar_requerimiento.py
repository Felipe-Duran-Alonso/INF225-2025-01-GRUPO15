from django.test import TestCase, Client
from django.urls import reverse
from myapp.models import Requerimiento
from django.contrib.auth.models import User

class TestEditarRequerimiento(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #Creo un requerimiento sobre el que probaré cosas
        cls.requerimiento = Requerimiento.objects.create(
            objetivo = "Mejorar la tasa de crecimiento de los cultivos.",
            descripcion = "En la zona se está pasando por una inusual pero leve hambruna, por lo que se ha optado por la contratación de investigadores para desarrollar un nuevo fertilizante personalizado para los cultivos de la zona.",
            regiones="Región de los lagos.",
            estados=0
        )
        cls.url_req = reverse("editar_requerimientos")

        cls.staff = User.objects.create_user(username='test', password='contrasena', is_staff=True)
        
    def setUp(self):
        self.client.login(username="test",password="contrasena")
    
    def test_eliminacion_exitosa(self):
        response = self.client.post(self.url_req, {
            'requerimiento_id':self.requerimiento.id,
            'requerimiento_editar_reg': '0', 
            'requerimiento_editar_obj': '0', 
            'requerimiento_editar_des': '0', 
            'eliminar': '1', 
            'flag': '0'
        })
        
        self.assertRedirects(response,reverse("ver_requerimientos"))
        
        eliminado = Requerimiento.objects.filter(id=self.requerimiento.id).exists()
        self.assertFalse(eliminado,"No se eliminó")
        
        
    def test_modificar_objetivo_vacio(self):
            #Cuando apreto el boton "modificar"
            response1 = self.client.post(self.url_req,{
                'requerimiento_id':self.requerimiento.id,
                'requerimiento_editar_reg':'0',
                "requerimiento_editar_obj":'1',
                'requerimiento_editar_des':'0',
                'eliminar': '0',
                'flag': '0'
            })
            
            response2 = self.client.post(self.url_req,{
                'Objetivo': '', 
                'Regiones': '0', 
                'Descripcion': '0', 
                'Requerimiento': self.requerimiento.objetivo, 
                'requerimiento_id': self.requerimiento.id, 
                'flag': '1'
            })
            
            self.requerimiento.refresh_from_db()
            
            funciono = self.requerimiento.objetivo#Si funciono es '' entonces se pudo editar el campo objetivo como ''.
            self.assertEqual(funciono,"")
        

    @classmethod
    def tearDownClass(cls):
        cls.requerimiento.delete()
        cls.staff.delete()
        super().tearDownClass()