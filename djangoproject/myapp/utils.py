import requests
from django.http import JsonResponse
from django.shortcuts import render,redirect
from myapp import models
from django.http import HttpResponse

URL_API_MAKE= "https://hook.us2.make.com/ci44onvom40qefynfkctvslihak0w4do" ## API para formatear los requerimientos con chatGPT
ACTIVACION_API_MAKE = False #Activacion de la API, Si esta desactivada no se formatean los datos. De lo contrario si.
#ID_SUPER_USUARIO = 1


def evaluar_insersion(request, Requerimientos_dict):
    # Datos que quieres enviar a la API
    datos = {
        "Regiones": Requerimientos_dict["Regiones"],
        "Objetivo": Requerimientos_dict["Objetivo"],
        "Descripcion":Requerimientos_dict["Descripcion"],
        "Url":"Url", #Modificar ya que aca recibira la respuesta
    }
    dict ={}
    if(not ACTIVACION_API_MAKE): #Si no esta activa inserto de forma directa
        dict["Regiones_nuevo"] = datos["Regiones"]
        dict["Objetivo_nuevo"] = datos["Objetivo"]
        dict["Descripcion_nuevo"] = datos["Descripcion"]
        dict["Error"] = 0
        models.Requerimiento.objects.create(objetivo=dict["Objetivo_nuevo"],descripcion=dict["Descripcion_nuevo"],regiones=dict["Regiones_nuevo"],estados=0)
        return render(request, 'insertar_requerimientos.html', dict)
    else:
        try:
            # Hacer la solicitud POST a la API
            respuesta = requests.post(URL_API_MAKE, json=datos)
            respuesta.raise_for_status()  # Verifica si hay algún error
            # Procesar los datos de la respuesta JSON
            respuesta_json = respuesta.json()

            dict["Regiones_nuevo"] = respuesta_json.get("Regiones_nuevo", 0)
            dict["Objetivo_nuevo"] = respuesta_json.get("Objetivo_nuevo", 0)
            dict["Descripcion_nuevo"] = respuesta_json.get("Descripcion_nuevo", 0)
            dict["Error"] = 0

            if(dict["Regiones_nuevo"]==0 or dict["Objetivo_nuevo"]==0 or dict["Descripcion_nuevo"]==0):
                if(dict["Regiones_nuevo"]==0):
                    dict["Error"] = "Region"
                else:
                    if(dict["Objetivo-nuevo"]==0):
                        dict["Error"] = "Objetivo"
                    else:
                        dict["Error"] = "Descripcion"
            
            # Aquí puedes hacer otras operaciones con los datos obtenidos
            # Por ejemplo, guardarlos en la base de datos, o manipularlos
            # MiModelo.objects.create(campo=resultado)
            respuesta ={
                "Regiones_nuevo":dict["Regiones_nuevo"],
                "Objetivo_nuevo":dict["Objetivo_nuevo"],
                "Descripcion_nuevo":dict["Descripcion_nuevo"],
                "Error":dict["Error"]
            }
            if (dict["Error"] == 0): #Solo se inserta si los datos son correctos
                models.Requerimiento.objects.create(objetivo=dict["Objetivo_nuevo"],descripcion=dict["Descripcion_nuevo"],regiones=dict["Regiones_nuevo"],estados=0)
            # Pasar los datos procesados al contexto de una plantilla
            return render(request, 'insertar_requerimientos.html', respuesta)

        except requests.exceptions.RequestException as e:
            # En caso de error, puedes manejarlo y mostrar un mensaje de error en la plantilla
            respuesta ={
                "Regiones_nuevo":-1,
                "Objetivo_nuevo":-1,
                "Descripcion_nuevo":-1,
                "Error":str(e)
            }
            return render(request, 'insertar_requerimientos.html', respuesta)

def evaluar_modificacion(request, Requerimiento_dict):
    Requerimiento = models.Requerimiento.objects.get(id = Requerimiento_dict["Id"])
    if(not ACTIVACION_API_MAKE): #Si no esta activa inserto de forma directa
        if Requerimiento_dict["Regiones"] != "0" :
            Requerimiento.regiones = Requerimiento_dict["Regiones"]
        else:
            if Requerimiento_dict["Objetivo"] != "0" :
                Requerimiento.objetivo = Requerimiento_dict["Objetivo"]
            else:
                Requerimiento.descripcion = Requerimiento_dict["Descripcion"]
        Requerimiento.save()
        dict = {}
        dict["Regiones_nuevo"] = Requerimiento.regiones
        dict["Objetivo_nuevo"] = Requerimiento.objetivo
        dict["Descripcion_nuevo"] = Requerimiento.descripcion
        dict["Error"] = 0    
        dict["lugar"] = 1      
        return render(request, 'editar_requerimientos_aux.html', dict)
    else:
        datos = {"Url":"Url"}#Modificar ya que aca recibira la respuesta
        if Requerimiento_dict["Regiones"] != "0" :
            datos["Regiones"] = Requerimiento_dict["Regiones"]
            datos["Objetivo"] = Requerimiento.objetivo
            datos["Descripcion"] = Requerimiento.descripcion
        else:
            if Requerimiento_dict["Objetivo"] != "0" :
                datos["Objetivo"] = Requerimiento_dict["Objetivo"]
                datos["Regiones"] = Requerimiento.regiones
                datos["Descripcion"] = Requerimiento.descripcion
            else:
                datos["Descripcion"] = Requerimiento_dict["Descripcion"]
                datos["Objetivo"] = Requerimiento.objetivo
                datos["Descripcion"] = Requerimiento.descripcion

        try:
            dict = {}
            # Hacer la solicitud POST a la API
            respuesta = requests.post(URL_API_MAKE, json=datos)
            respuesta.raise_for_status()  # Verifica si hay algún error
            # Procesar los datos de la respuesta JSON
            respuesta_json = respuesta.json()

            dict["Regiones_nuevo"] = respuesta_json.get("Regiones_nuevo", 0)
            dict["Objetivo_nuevo"] = respuesta_json.get("Objetivo_nuevo", 0)
            dict["Descripcion_nuevo"] = respuesta_json.get("Descripcion_nuevo", 0)
            dict["Error"] = 0

            if(dict["Regiones_nuevo"]==0 or dict["Objetivo_nuevo"]==0 or dict["Descripcion_nuevo"]==0):
                if(dict["Regiones_nuevo"]==0):
                    dict["Error"] = "Region"
                else:
                    if(dict["Objetivo-nuevo"]==0):
                        dict["Error"] = "Objetivo"
                    else:
                        dict["Error"] = "Descripcion"
            
            # Aquí puedes hacer otras operaciones con los datos obtenidos
            # Por ejemplo, guardarlos en la base de datos, o manipularlos
            # MiModelo.objects.create(campo=resultado)
            respuesta ={
                "Regiones_nuevo":dict["Regiones_nuevo"],
                "Objetivo_nuevo":dict["Objetivo_nuevo"],
                "Descripcion_nuevo":dict["Descripcion_nuevo"],
                "Error":dict["Error"],
                "lugar":1
            }
            if (dict["Error"] == 0): #Solo se Modifica si los datos son correctos
                Requerimiento.regiones = respuesta["Regiones_nuevo"]
                Requerimiento.objetivo = respuesta["Objetivo_nuevo"]
                Requerimiento.descripcion = respuesta["Descripcion_nuevo"]
                Requerimiento.save()
            # Pasar los datos procesados al contexto de una plantilla
            return render(request, 'editar_requerimientos_aux.html', respuesta)

        except requests.exceptions.RequestException as e:
            # En caso de error, puedes manejarlo y mostrar un mensaje de error en la plantilla
            respuesta ={
                "Regiones_nuevo":-1,
                "Objetivo_nuevo":-1,
                "Descripcion_nuevo":-1,
                "Error":str(e),
                "lugar":1
            }
            return render(request, 'editar_requerimientos_aux.html', respuesta)
        #Adaptar el manejo de la API

def get_API_MAKE():
    global ACTIVACION_API_MAKE
    return ACTIVACION_API_MAKE

def set_API_MAKE(valor):
    global ACTIVACION_API_MAKE
    ACTIVACION_API_MAKE = valor
    return

def get_diccionario_nombre_valor(nombres,valores):
    dict = {}
    for i in range(0, len(nombres)):
        dict[nombres[i]] = valores[i]
    return dict

"""
def get_SUPER_USUARIO():
    global ID_SUPER_USUARIO
    return ID_SUPER_USUARIO

def set_SUPER_USUARIO(valor):
    global ID_SUPER_USUARIO 
    ID_SUPER_USUARIO = valor
    return
"""
