import os, time
from gpt4all import GPT4All
from textwrap import wrap

#Nuevo
from transformers import AutoTokenizer
from huggingface_hub import snapshot_download

#MODEL_DIR  = r"C:\Users\felid\.cache\huggingface\hub\models--QuantFactory--Meta-Llama-3-8B-Instruct-GGUF\snapshots\86e0c07efa3f1b6f06ea13e31b1e930dce865ae4"
#MODEL_NAME = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
home_dir = os.path.expanduser("~")
MAX_INTENTOS = 10
INTERVAL = 5
# Construye el path completo al modelo de forma portable
MODEL_DIR = os.path.join(
    home_dir,
    ".cache", "huggingface", "hub",
    "models--QuantFactory--Meta-Llama-3-8B-Instruct-GGUF",
    "snapshots", "86e0c07efa3f1b6f06ea13e31b1e930dce865ae4"
)

MODEL_NAME = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"

#Nuevo path tokenizador
TOKENIZER_DIR = os.path.join(home_dir, 
    ".cache", "huggingface", "hub",
    "llama2_tokenizer")
TOKENIZER_FILES = ["tokenizer.json",
                "tokenizer.model",
                "tokenizer_config.json",
                "special_tokens_map.json"]
if not os.path.exists(os.path.join(TOKENIZER_DIR, "tokenizer.model")):
    snapshot_download(
        repo_id="NousResearch/Llama-2-7b-chat-hf",
        allow_patterns=TOKENIZER_FILES,
        local_dir=TOKENIZER_DIR,
        local_dir_use_symlinks=False
    )
#Llamar al tokenizador
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_DIR)

#Nuevo
def Contar_tokens(texto):
    input_ids = tokenizer.encode(texto, add_special_tokens=True)
    print(f"CANTIDAD DE TOKENS: {len(input_ids)}")
    return len(input_ids)

def split_text(text, max_tokens=1700):
    # Aproximación: 1 token ≈ 4 caracteres en promedio (esto varía)
    max_chars = max_tokens * 4
    return wrap(text, max_chars)

def Get_resumen(texto):
    chunks = split_text(texto)
    resumen = ""
    for i, chunk in enumerate(chunks):
        response = Get_resumen_aux(chunk)
        print("RESPONSE", response)
        resumen+=response + "\n"
    if len(chunks)>1:
        return Get_resumen_aux(resumen)
    else:
        return resumen

def Get_resumen_aux(texto):
    global MODEL_DIR, MODEL_NAME
    os.environ["GPT4ALL_NO_CUDA"] = "1"
    orig_stderr = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)
    os.close(devnull)

    modelo = GPT4All(
        model_name=MODEL_NAME,
        model_path=MODEL_DIR,
        device="cpu",
        allow_download=False
    )

    os.dup2(orig_stderr, 2)
    os.close(orig_stderr)

    #consulta = "Resume lo siguiente, obteniendo los puntos PRINCIPALES:\n" + str(texto)
    #consulta+=".\nRetorna únicamente la respuesta, sin texto adicional y en Spanish y UTF-8.\n####"
    consulta = (
        "A continuación se presenta un texto. Haz un resumen conciso extrayendo SOLO las ideas principales, "
        "sin interpretaciones personales ni explicaciones subjetivas. "
        "Escribe el resumen en español claro y sin adornos. No incluyas ningún comentario adicional. "
        "No empieces con frases como 'el texto trata sobre' o 'en resumen'. SOLO devuelve el resumen en español y codificado en UTF-8. "
        "Texto:\n" + str(texto) + "\n####"
    )
    
    #Condicion texto largo->Limitar a 2200.
    largo = Contar_tokens(consulta)
    if largo>=2200:
        print("TEXTO MUY LARGO")
        return -1
    
    num_intentos = 0
    while(num_intentos<MAX_INTENTOS):
        try:
            with modelo.chat_session():
                salida = modelo.generate(
                    consulta,
                    max_tokens=500, 
                    temp=0.75
                )
            break
        except Exception as e:  
            num_intentos += 1
            print(f"Ocurrió un error generando el resumen (intento {num_intentos}): {e}")
            print(f"   Se volvera a intentar en {INTERVAL} segundos")
            time.sleep(INTERVAL)

    respuesta = salida.split("####")[0].strip()
    return respuesta.encode("cp1252", errors="ignore").decode("cp1252")