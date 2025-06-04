# INF225-2025-01-GRUPO15
 ### Integrantes (con rol):
- Frnco Sepúlveda  (202160584-3)
- Felipe Duran Alonso  (202160599-1)
- Oscar Valverde  (202173623-9)
- **Tutor:** Eduardo Pino
### Enlaces relevantes:
*  [Repositorio Analisis y diseño de software.](https://github.com/Blindas31/GRUPO5-2024-PROYINF) 

### Pasos a seguir para la ejecucion de la [ultima version](https://github.com/Felipe-Duran-Alonso/INF225-2025-01-GRUPO15/wiki/Avances-de-codigo#cuarta-entrega) :

1. Abrir la terminal en la ubicación del [archivo](https://github.com/Felipe-Duran-Alonso/INF225-2025-01-GRUPO15/tree/dd1d979515e51b55a1c2a466e6511709b1eefcb6/djangoproject) del proyecto.
2. En caso de usar virtualenv (para windows):
     <br>python -m venv venv      
     venv\Scripts\activate   
4. Ejecutar la siguiente linea (En caso de no funciona, se recomienda reiniciar el equipo luego de la instalacion):
     <br>pip install -r requirements.txt
     <br>huggingface-cli download QuantFactory/Meta-Llama-3-8B-Instruct-GGUF
6. Escribir "python manage.py runserver" (en caso de que no funcioné escribir "python3 manage.py runserver").
7. En la terminal se indicara la url de la página web normalmente "http://127.0.0.1:8000/".
