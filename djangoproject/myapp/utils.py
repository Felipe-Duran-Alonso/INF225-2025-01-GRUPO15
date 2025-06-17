import requests
from django.http import JsonResponse
from django.shortcuts import render,redirect
from myapp import models
from django.http import HttpResponse
from bs4 import BeautifulSoup
from readability import Document
from .templates_names import *
URL_API_MAKE= "https://hook.us2.make.com/ci44onvom40qefynfkctvslihak0w4do" ## API para formatear los requerimientos con chatGPT
ACTIVACION_API_MAKE = False #Activacion de la API, Si esta desactivada no se formatean los datos. De lo contrario si.
#ID_SUPER_USUARIO = 1

def quitar_etiquetas_bs(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    etiquetas_borrar = ["script", "style", "noscript", "header", "footer", "iframe"]
    for tag_name in etiquetas_borrar:
        for tag in soup.find_all(tag_name):
            try:
                tag.decompose()  # elimina el nodo del árbol
            except Exception as e:
                print(f"No pude eliminar <{tag_name}>: {e!r}")
    return soup.get_text(separator=" ", strip=True)

def Scraper_fuente(url, usar_readability=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ScraperGenérico/1.0)",
        "Accept-Language": "es-ES,es;q=0.9"
    }
    readability_disponible = True
    try:
        respuesta = requests.get(url, headers=headers, timeout=10)
        respuesta.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"No se pudo obtener la URL ({e})")

    html = respuesta.text
    #print(html)
    # Extraer contenido principal si se desea y si readability está disponible
    if usar_readability and readability_disponible:
        doc = Document(html)
        html = doc.summary()  # HTML solo del contenido principal

    # Parsear HTML con BeautifulSoup
    soup = quitar_etiquetas_bs(html)
    # Eliminar elementos no deseados
    """
    for tag in soup(["script", "style", "noscript", "header", "footer", "iframe"]):
        tag.decompose()
    print("\n\n\n\n\n\n\n\n??????????????????????????????????????????????????????")    
    """
    # Extraer texto visible
    #print(soup)
    """
    texto_completo = soup.get_text(separator="\n")
    lineas = [line.strip() for line in texto_completo.splitlines()]
    lineas = [line for line in lineas if line]
    texto_limpio = "\n".join(lineas)
    #print(texto_limpio)   
    return texto_limpio  
    """
    return soup


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
        return render(request, CREAR_REQUERIMIENTO, dict)
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
            return render(request, CREAR_REQUERIMIENTO, respuesta)

        except requests.exceptions.RequestException as e:
            # En caso de error, puedes manejarlo y mostrar un mensaje de error en la plantilla
            respuesta ={
                "Regiones_nuevo":-1,
                "Objetivo_nuevo":-1,
                "Descripcion_nuevo":-1,
                "Error":str(e)
            }
            return render(request, CREAR_REQUERIMIENTO, respuesta)

def evaluar_modificacion(request, Requerimiento_dict):
    Requerimiento = models.Requerimiento.objects.get(id = Requerimiento_dict["Id"])
    if(not ACTIVACION_API_MAKE): #Si no esta activa inserto de forma directa
        if Requerimiento_dict["Regiones"] != "0" :
            Requerimiento.regiones = Requerimiento_dict["Regiones"]
        else:
            if Requerimiento_dict["Objetivo"] != "0" :
                
                #Caso Objetivo vacio -----
                Obj = Requerimiento_dict["Objetivo"].strip()
                if Obj == "":
                    dict = {}
                    dict["Regiones_nuevo"] = Requerimiento.regiones
                    dict["Objetivo_nuevo"] = Requerimiento.objetivo
                    dict["Descripcion_nuevo"] = Requerimiento.descripcion
                    dict["Error"] = "El campo Objetivo no puede quedar vacío"    
                    dict["lugar"] = 0
                    dict["editar_obj"] = 1
                    dict["req_id"] = Requerimiento_dict["Id"]
                    return render(request, EDITAR_REQUERIMIENTO_AUX, dict)
                # --------
                
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
        return render(request, EDITAR_REQUERIMIENTO_AUX, dict)
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
            return render(request, EDITAR_REQUERIMIENTO_AUX, respuesta)

        except requests.exceptions.RequestException as e:
            # En caso de error, puedes manejarlo y mostrar un mensaje de error en la plantilla
            respuesta ={
                "Regiones_nuevo":-1,
                "Objetivo_nuevo":-1,
                "Descripcion_nuevo":-1,
                "Error":str(e),
                "lugar":1
            }
            return render(request, EDITAR_REQUERIMIENTO_AUX, respuesta)
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
