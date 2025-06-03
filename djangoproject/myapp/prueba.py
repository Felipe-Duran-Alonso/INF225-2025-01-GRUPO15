import os, sys
from gpt4all import GPT4All

# ——————————————————————————————
# 1) Silenciar mensajes de CUDA/DLL
# ——————————————————————————————
os.environ["GPT4ALL_NO_CUDA"] = "1"
# redirige todo stderr a /dev/null
orig_stderr = os.dup(2)
devnull = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnull, 2)
os.close(devnull)

# ——————————————————————————————
# 2) Carga tu modelo local
# ——————————————————————————————
MODEL_DIR  = r"C:\Users\felid\.cache\huggingface\hub\models--QuantFactory--Meta-Llama-3-8B-Instruct-GGUF\snapshots\86e0c07efa3f1b6f06ea13e31b1e930dce865ae4"
MODEL_NAME = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"

modelo = GPT4All(
    model_name=MODEL_NAME,
    model_path=MODEL_DIR,
    device="cpu",
    allow_download=False
)

# restaura stderr para ver errores Python a partir de aquí
os.dup2(orig_stderr, 2)
os.close(orig_stderr)

# ——————————————————————————————
# 3) Prepara tu prompt con marcador de fin
# ——————————————————————————————
consulta = "Resume lo siguiente, obteniendo los puntos PRINCIPALES:" 
consulta+=str("El relojero y el tiempoEn un pequeño pueblo, vivía un anciano relojero llamado Elías. Su tienda, repleta de relojes antiguos y engranajes brillantes, tenía una particularidad: todos los relojes marcaban una hora distinta.La gente decía que Elías estaba loco, que ya no podía ni ajustar un péndulo. Pero lo que nadie sabía era que cada reloj estaba sincronizado con el momento más feliz de quien lo compraba.Un día, un niño entró a la tienda y preguntó:—¿Por qué tus relojes están mal?Elías sonrió, le ofreció un reloj diminuto de bolsillo y respondió:—No están mal. Cada uno recuerda el instante en que alguien fue feliz… para que nunca se les olvide que ese tiempo existe.El niño se fue con su reloj, que marcaba las 4:17. A esa hora exacta, veinte años después, le daría el primer beso a la persona que cambiaría su vida.")
consulta+=".Responde únicamente con la respuesta, sin texto adicional y en Spanish y UTF-8.\n####"

# ——————————————————————————————
# 4) Genera sin stop, sólo max_tokens y temp
# ——————————————————————————————
flag = True
while(flag):
    try:
        with modelo.chat_session():
            salida = modelo.generate(
                consulta,
                max_tokens=500, 
                temp=0.75
            )
        flag=False
    except:
        continue
# ——————————————————————————————
# 5) Trocea la salida en el marcador y limpia
# ——————————————————————————————
respuesta = salida.split("####")[0].strip()
clean = respuesta.encode("cp1252", errors="ignore").decode("cp1252")
print(clean)