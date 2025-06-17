import fitz
import json
from pdf2docx import Converter
from django.shortcuts import render,redirect
from django.http import HttpResponse
from myapp import form
from myapp import models
from django.contrib.auth.decorators import login_required #Libreria para implementar inicio de sesion
from django.contrib.auth import logout
from django.http import JsonResponse
from .utils import *
from django.contrib.auth.models import User
from .permisos import *
from .IA_utils import *
from .templates_names import *
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def index(request):
    return render(request, HOME) 

def registro(request):
    return render(request, REGISTRO)

@login_required #Marcar vista que requiere inicio de sesion
def ver_requerimientos(request):
    return render(request, VER_REQUERIMIENTO)

@csrf_exempt
@login_required #Marcar vista que requiere inicio de sesion
def requerimientos(request):
    if request.method==('GET'):
        return render(request, REQUERIMIENTO,{'formulario': form.CreateRequerimiento()})
    else:
        print(request.POST)
        objetivo=request.POST['objetivo']
        regiones=request.POST['regiones']
        descripcion=request.POST['descripcion']
        dict ={}
        dict["Regiones"] = regiones
        dict["Objetivo"] = objetivo
        dict["Descripcion"] = descripcion
        return evaluar_insersion(request=request,Requerimientos_dict=dict)
        #models.Requerimiento.objects.create(objetivo=objetivo,descripcion=descripcion,regiones=regiones,estados=0)
        #return redirect('ver_requerimientos')

@login_required #Marcar vista que requiere inicio de sesion  
def get_requerimiento(request):
    cant_listo=models.Requerimiento.objects.filter(estados=1).count()
    cant_registrados=models.Requerimiento.objects.filter(estados=0).count()
    cant_pendientes=models.Requerimiento.objects.filter(estados=-1).count()
    requerimiento=models.Requerimiento.objects.all()
    return render(request,VER_REQUERIMIENTO,{'Requerimiento': requerimiento,"cant_listo":cant_listo,"cant_registrados":cant_registrados,"cant_pendientes":cant_pendientes})

def cerrar_sesion(request):
    logout(request)
    return render(request,HOME) 

@csrf_exempt
def ver_boletines(request):
    boletines = models.Boletin.objects.all()

    if request.method == 'GET':
        return render(request, VER_BOLETIN, {'Boletin': boletines})

    boletin_id = int(request.POST.get('boletin_id', -1))
    if boletin_id == -1:
        return render(request, VER_BOLETIN, {'Boletin': boletines})

    boletin = models.Boletin.objects.get(id=boletin_id)
    accion = request.POST.get('accion', '')
    
    # --- VER PDF ---
    if request.POST.get('ver') == '1':
        boletin.vistas += 1
        boletin.save()
        with open(boletin.archivo_pdf.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{boletin.archivo_pdf.name}"'
            return response

    # --- DESCARGAR ---
    if accion == 'descargar':
        formato = request.POST.get('descargar_formato')
        boletin.descargas += 1
        boletin.save()

        if formato == 'pdf':
            with open(boletin.archivo_pdf.path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{boletin.archivo_pdf.name}"'
                return response
        elif formato == 'html':
            doc = fitz.open(boletin.archivo_pdf.path)
            html = "<html><body>"
            for page in doc:
                html += page.get_text("html")
            html += "</body></html>"
            
            response = HttpResponse(html, content_type='text/html')
            response['Content-Disposition'] = f'attachment; filename="{boletin.titulo}.html"'
            return response
        elif formato == 'docx':
            # Ruta del archivo original PDF
            pdf_path = boletin.archivo_pdf.path
            # Ruta temporal para guardar el archivo Word generado
            docx_path = pdf_path.replace(".pdf", ".docx")

            # Convertir PDF a DOCX
            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()

            # Retornar como archivo descargable
            with open(docx_path, 'rb') as docx_file:
                response = HttpResponse(docx_file.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename="{boletin.titulo}.docx"'
                return response

    # --- ENVIAR POR CORREO ---
    if accion == 'enviar':
        formato = request.POST.get('email_formato')
        # Aquí podrías usar un email real del usuario si lo recolectás
        destino = 'usuario@ejemplo.com'
        asunto = f"Boletín: {boletin.titulo}"
        cuerpo = "Adjunto encontrarás el boletín solicitado."

        email = EmailMessage(asunto, cuerpo, to=[destino])

        if formato == 'pdf':
            with open(boletin.archivo_pdf.path, 'rb') as f:
                email.attach(f"{boletin.titulo}.pdf", f.read(), 'application/pdf')
        elif formato == 'html':
            contenido = boletin.descripcion
            email.attach(f"{boletin.titulo}.html", contenido, 'text/html')

        try:
            email.send()
            mensaje = "📧 Boletín enviado exitosamente al correo."
        except:
            mensaje = "❌ Error al enviar el boletín por correo."

        return render(request, VER_BOLETIN, {'Boletin': boletines, 'mensaje': mensaje})

    # Por defecto, recargar la vista
    return render(request, VER_BOLETIN, {'Boletin': boletines})


@staff_required #Marcar vista que requiere estado staff
def editar_boletines(request):
    estados_requerimientos = ["Por procesar", "En proceso", "Finalizado"]
    boletines=models.Boletin.objects.all()
    if request.method==('GET'):
        return render(request,EDITAR_BOLETIN,{'Boletin': boletines})    
    else:
        boletin_id=request.POST['boletin_id']
        lugar = int(request.POST['lugar'])
        if(lugar ==0):
            flag = int(request.POST['flag'])
            if flag==1:
                boletin = models.Boletin.objects.get(id = boletin_id)
                return render(request,EDITAR_BOLETIN_AUX,{'boletin_id': boletin_id, 'Boletin':boletin, 'requerimientos':models.Requerimiento.objects.all(),'mostrar':False, 'estados':estados_requerimientos})
            else:
                boletin_estado=request.POST['boletin_estado']
                boletin_por_cambiar = models.Boletin.objects.get(id = boletin_id)
                boletin_por_cambiar.es_publico = boletin_estado
                boletin_por_cambiar.save()
        else:
            eliminar = int(request.POST['eliminar'])
            print(eliminar)
            boletin = models.Boletin.objects.get(id = boletin_id)
            if eliminar == 1:
                print("ENTREEEEE")
                boletin.delete()
            else:
                mostrar = request.POST.get('mostrar')
                if int(mostrar) == 1:
                    tipo = request.POST.get('tipo')
                    if tipo == estados_requerimientos[0]: #LOS POR PROCESAR
                        requerimientos =  models.Requerimiento.objects.filter(estados=0)
                    elif tipo == estados_requerimientos[1]: #LOS EN PROCESO
                        requerimientos =  models.Requerimiento.objects.filter(estados=-1)
                    elif tipo == estados_requerimientos[2]: #LOS LISTOS
                        requerimientos =  models.Requerimiento.objects.filter(estados=1)
                    return render(request,EDITAR_BOLETIN_AUX,{'boletin_id': boletin_id, 'Boletin':boletin, 'requerimientos':requerimientos,'mostrar':True, 'estados':estados_requerimientos})
                titulo = request.POST.get('titulo')
                descripcion = request.POST.get('descripcion')
                archivo_pdf = request.FILES.get('archivo_pdf')
                requerimiento_id = request.POST.get('requerimiento')      
                if titulo:
                    boletin.titulo = titulo
                if descripcion:
                    boletin.descripcion = descripcion
                if archivo_pdf:
                    boletin.archivo_pdf = archivo_pdf
                if requerimiento_id:
                    boletin.requerimiento = models.Requerimiento.objects.get(id = requerimiento_id)
                boletin.save()
        return redirect('editar_boletines')

@staff_required #Marcar vista que requiere estado staff
def subir_boletines(request):
    if request.method==('GET'):
        return render(request,SUBIR_BOLETIN,{'form': form.CreateBoletin()})
    else:
        boletin_titulo=request.POST['titulo']
        boletin_desc=request.POST['descripcion']
        boletin_arch = request.FILES.get('archivo_pdf')
        boletin_req = request.POST['requerimiento']
        Requimiento_vinculado = models.Requerimiento.objects.get(id = boletin_req)
        models.Boletin.objects.create(titulo = boletin_titulo,descripcion=boletin_desc,archivo_pdf=boletin_arch,requerimiento=Requimiento_vinculado)
        Requimiento_vinculado.estados = 1
        Requimiento_vinculado.save()        
        return redirect('index')

@staff_required #Marcar vista que requiere estado staff
def editar_requerimientos(request):
    requerimientos=models.Requerimiento.objects.all()
    if request.method==('GET'):
        return render(request,EDITAR_REQUERIMIENTO,{'Requerimiento': requerimientos})    
    else:
        requerimiento_id=request.POST['requerimiento_id']
        requerimiento = models.Requerimiento.objects.get(id=requerimiento_id)
        if(int(request.POST["flag"]) == 1):
            print("entre")
            dict = {
                'Regiones':request.POST['Regiones'],
                'Objetivo':request.POST['Objetivo'],
                'Descripcion':request.POST['Descripcion'],
                'Id': request.POST['requerimiento_id']
            }
            return evaluar_modificacion(request = request, Requerimiento_dict = dict)
        else:
            if (int(request.POST["eliminar"])==1):
                requerimiento.delete()  
                return redirect('ver_requerimientos')
            else:
                requerimiento_editar_reg=int(request.POST['requerimiento_editar_reg'])
                requerimiento_editar_obj=int(request.POST['requerimiento_editar_obj'])
                requerimiento_editar_des=int(request.POST['requerimiento_editar_des'])
                return render(request, EDITAR_REQUERIMIENTO_AUX, {'req_id':requerimiento_id,'editar_reg':requerimiento_editar_reg,'editar_obj':requerimiento_editar_obj,'editar_des':requerimiento_editar_des,'Requerimiento':requerimiento,'lugar':0})

@superuser_required #Marcar vista que requiere ser super usuario
def modificar_configuraciones(request):
    nombres = ["ACTIVACION_API_MAKE", "USUARIOS"] #Enumerar todas las opciones
    valores = [get_API_MAKE(), User.objects.all()] #Enumerar todos los valores que se quieren enviar al template
    dict = get_diccionario_nombre_valor(nombres,valores)
    if request.method==('GET'):
        return render(request,CONFIGURACIONES,dict)
    else:
        retornos = {}
        flag = int(request.POST["flag"])
        if flag == 0 : #Caso activacion de API
            retornos["ACTIVACION_API_MAKE"] = request.POST["opcion_ACTIVACION_API_MAKE"]

            if int(retornos["ACTIVACION_API_MAKE"]) == 0:
                set_API_MAKE(False)
                dict["ACTIVACION_API_MAKE"] = False
            if int(retornos["ACTIVACION_API_MAKE"]) == 1:
                set_API_MAKE(True)
                dict["ACTIVACION_API_MAKE"] = True
        elif flag == 1 : #Caso modificacion permisos de usuarios
            Staff = int(request.POST["Staff"])
            Activacion = int(request.POST["Activacion"])
            user_id = int(request.POST["user_id"])
            user = User.objects.get(id=user_id)
            if Activacion == -1: #Caso modificacion de staff
                if Staff ==1:
                    user.is_staff = True
                else:
                    user.is_staff = False
            else: #Caso modificacion de Activacion
                if Activacion == 1:
                    user.is_active = True
                else:
                    user.is_active = False
            user.save()
            dict["USUARIOS"] = User.objects.all()
        elif flag == -1 :
            requerimientos = models.Requerimiento.objects.all()
            boletines = models.Boletin.objects.all()
            for boletin in boletines:
                if boletin.requerimiento in requerimientos and boletin.requerimiento.estados != 1:
                    boletin.requerimiento.estados = 1
                    boletin.requerimiento.save()
            return redirect('ver_requerimientos')
        return render(request,CONFIGURACIONES,dict)

@staff_required #Marcar vista que requiere estado staff   
def estadisticas_boletines(request):
    cant_publicos=models.Boletin.objects.filter(es_publico = True).count()
    cant_ocultos=models.Boletin.objects.filter(es_publico = False).count()
    boletines = models.Boletin.objects.all()
    descargas_publicos = 0
    descargas_ocultos = 0 
    vistas_publicos =0
    vistas_ocultos =0
    for boletin in boletines:
        if boletin.es_publico:
            descargas_publicos = descargas_publicos + boletin.descargas
            vistas_publicos = vistas_publicos + boletin.vistas
        else:
            descargas_ocultos = descargas_ocultos + boletin.descargas
            vistas_ocultos = vistas_ocultos + boletin.vistas
    if(cant_publicos != 0):
        descargas_publicos=int(descargas_publicos/cant_publicos)
        vistas_publicos = int(vistas_publicos/cant_publicos)
    if(cant_ocultos !=0):
        descargas_ocultos=int(descargas_ocultos/cant_ocultos)
        vistas_ocultos=int(vistas_ocultos/cant_ocultos)
    dict ={
        'Boletines': boletines,
        'cant_publicos':cant_publicos,
        'cant_ocultos':cant_ocultos,
        'descargas_publicos':descargas_publicos,
        'vistas_publicos':vistas_publicos,
        'descargas_ocultos':descargas_ocultos,
        'vistas_ocultos':vistas_ocultos,
    }
    if request.method==('GET'):
        dict['mostrar']=0
        return render(request,ESTADISTICA_BOLETIN,dict)
    else:
        dict['mostrar']=int(request.POST["mostrar"])
        return render(request,ESTADISTICA_BOLETIN,dict)

@staff_required 
def administrar_fuentes(request):
    if request.method == ('GET'):
        return render(request, ADMINISTRAR_FUENTE,{'formulario': form.CreateFuente(),'fuentes':models.Fuente.objects.all()})
    else:
        if int(request.POST['ingresar']) == 1:
            enlace=request.POST['enlace']
            models.Fuente.objects.create(enlace=str(enlace))
            return redirect('administrar_fuentes')   
        else:       
            fuente_id, flag,  = int(request.POST['fuente_id']), int(request.POST['flag'])
            fuente = models.Fuente.objects.get(id = fuente_id)
            if flag == 100:
                fuente.delete()
            else:
                fuente.estado = flag
                fuente.save()
            return redirect('administrar_fuentes')   

def resumir_texto(request):
    sin_resumen = models.Fuente.objects.annotate(num_resumenes=Count('resumen')).filter(num_resumenes=0, estado =1)
    if request.method==('GET'):
        return render(request, CREAR_RESUMEN_OLD,{'vista': 1,"fuentes":sin_resumen})
    else:
        texto = str(request.POST['texto'])
        fuente = str(request.POST['fuente'])
        resumen = Get_resumen(texto)
        
        #Caso que supera el límite -> Texto muy largo.
        if resumen == -1:
            return render(request, CREAR_RESUMEN_OLD,{'vista': 1,"fuentes":sin_resumen,'error_largo':True})
        
        if fuente != "aaa":
            obj_fuente = models.Fuente.objects.get(pk=fuente)
            registro = models.Resumen(fuente = obj_fuente,resumen = resumen)
            registro.save()
        return render(request, CREAR_RESUMEN_OLD,{'vista': 0,'resumen':resumen})
    
@csrf_exempt
def resumir_texto1(request):
    sin_resumen = models.Fuente.objects.annotate(num_resumenes=Count('resumen')).filter(num_resumenes=0, estado =1)
    print(request.POST)
    if request.method==('GET'):
        try:
            #print("ENTRE")
            fuente = str(request.GET['fuente'])
            obj_fuente = models.Fuente.objects.get(pk=fuente)
            #print("FUENTE:",obj_fuente.enlace)
            url = obj_fuente.enlace
            #print("Voy a entrar al scraper")
            scrap = Scraper_fuente(url)
            #print("Sali del scraper")
            #print(scrap)
            return render(request, CREAR_RESUMEN,{'vista': 3,"fuentes":sin_resumen,"scrap":scrap,"url":url})            
        except:
            return render(request, CREAR_RESUMEN,{'vista': 1,"fuentes":sin_resumen})
    else:
        texto = str(request.POST['contenido'])
        fuente = str(request.POST['url'])
        resumen = Get_resumen(texto)
        
        #Caso que supera el límite -> Texto muy largo.
        if resumen == -1:
            return render(request, CREAR_RESUMEN,{'vista': 1,"fuentes":sin_resumen,'error_largo':True})
        
        if fuente != "aaa":
            obj_fuente = models.Fuente.objects.get(enlace=fuente)
            registro = models.Resumen(fuente = obj_fuente,resumen = resumen)
            registro.save()
        return render(request, CREAR_RESUMEN,{'vista': 0,'resumen':resumen})

def revisar_resumen(request):
    if request.method==('GET'):
        etiquetas_totales = set()

        for resumen in models.Resumen.objects.all():
            try:
                etiquetas = json.loads(resumen.etiquetas)
                etiquetas_totales.update(etiquetas)
            except json.JSONDecodeError:
                continue      

        resumenes = models.Resumen.objects.filter(estado=-1)

        return render(request, REVISAR_RESUMEN,{'vista': 0,"resumenes":resumenes,"etiquetas":etiquetas_totales})
    else:
        id = str(request.POST['resumen_id'])
        obj_resumen = models.Resumen.objects.get(pk=id)
        obj_resumen.estado = 1
        etiquetas = request.POST.getlist('etiquetas[]')
        obj_resumen.etiquetas = json.dumps(etiquetas)
        obj_resumen.save()
        return redirect('revisar_resumen') 
    
def editar_resumen(request):
    if request.method==('GET'):
        resumenes = models.Resumen.objects.filter(estado__in=[0, 1])
        etiquetas_totales = set()
        resumenes_con_etiquetas = []
        for resumen in resumenes:
            try:
                etiquetas = json.loads(resumen.etiquetas)
            except (TypeError, json.JSONDecodeError):
                etiquetas = []
            
            resumenes_con_etiquetas.append({
                'resumen': resumen,
                'etiquetas': etiquetas
            })

            try:
                etiquetas = json.loads(resumen.etiquetas)
                etiquetas_totales.update(etiquetas)
            except json.JSONDecodeError:
                continue    
        return render(request, EDITAR_RESUMEN, {"resumenes": resumenes_con_etiquetas,"etiquetas_t":etiquetas_totales})              
    else:
        modo = int(request.POST['modo'])
        resumen_id = str(request.POST['resumen_id'])
        obj_resumen = models.Resumen.objects.get(pk=resumen_id)
        #print(modo)
        if modo == 2: #Editar estado
            #print("ENTRE")
            new_estado = int(request.POST['new_estado'])
            obj_resumen.estado = new_estado
            obj_resumen.save()
        elif modo == 1: #Edicion del resumen
            contenido = quitar_etiquetas_bs(request.POST['contenido'])
            obj_resumen.resumen = contenido
            obj_resumen.save()
        elif modo ==0:  #Editar etiquetas
            etiquetas = request.POST.getlist('etiquetas[]')
            obj_resumen.etiquetas = json.dumps(etiquetas)
            obj_resumen.save()
        elif modo ==-1: #Borrar resumen
            obj_resumen.delete()
        return redirect('editar_resumen')           


        


        





