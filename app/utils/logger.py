import os
import sys
import datetime
import threading

# Lock global para evitar conflito de escrita em logs concorrentes
_log_lock = threading.Lock()

# Caminho padrão para salvar logs (caso queira registrar em disco)
LOG_PATH = os.getenv("APP_LOG_PATH", "logs")
LOG_FILE = os.path.join(LOG_PATH, "agent.log")

# Códigos ANSI para colorir o terminal (desativa em Windows se não suportado)
COLORS = {
    "RESET": "\033[0m",
    "INFO": "\033[94m",      # azul
    "SUCCESS": "\033[92m",   # verde
    "WARNING": "\033[93m",   # amarelo
    "ERROR": "\033[91m",     # vermelho
    "HEADER": "\033[95m"     # magenta
}


def _ensure_log_dir():
    """Garante que o diretório de logs exista."""
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH, exist_ok=True)


def log(tag: str, message: str, level: str = "INFO", save_to_file: bool = True):
    """
    Loga uma mensagem formatada com timestamp e cor.
    
    Args:
        tag (str): Contexto ou origem do log (ex: 'ReasonNode', 'ExcelAgent').
        message (str): Mensagem para registrar.
        level (str): INFO | SUCCESS | WARNING | ERROR.
        save_to_file (bool): Se True, grava no arquivo de log também.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = COLORS.get(level.upper(), COLORS["INFO"])
    reset = COLORS["RESET"]

    formatted = f"[{timestamp}] [{level.upper()}] [{tag}] {message}"

    # Log colorido no terminal
    with _log_lock:
        sys.stdout.write(f"{color}{formatted}{reset}\n")
        sys.stdout.flush()

        # Também salva em arquivo, se habilitado
        if save_to_file:
            _ensure_log_dir()
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")


def clear_logs():
    """Apaga o arquivo de log atual."""
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        log("Logger", "Arquivo de log limpo.", level="WARNING")


def log_startup(app_name: str):
    """Mensagem inicial para indicar que o sistema iniciou."""
    banner = f"\n🚀 {app_name} iniciado em {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 🚀\n"
    sys.stdout.write(COLORS["HEADER"] + banner + COLORS["RESET"])
    sys.stdout.flush()
    log("System", "Aplicação iniciada com sucesso.", "SUCCESS")
