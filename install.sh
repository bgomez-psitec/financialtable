#!/bin/sh
# =============================================================================
#  DataContaBL — Script de instalación para Alpine Linux
#  Uso: sh install.sh
#  Requisitos: ejecutar como root
# =============================================================================

set -e

# ── Colores ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── Constantes ────────────────────────────────────────────────────────────────
GITHUB_REPO="https://github.com/bgomez-psitec/financialtable"
INSTALL_DIR="/DataContaBL"
SERVICE_NAME="datacontabl"
VENV_DIR="${INSTALL_DIR}/venv"
PYTHON="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"
GUNICORN="${VENV_DIR}/bin/gunicorn"

# ── Helpers ───────────────────────────────────────────────────────────────────
print_banner() {
    echo ""
    printf "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════╗"
    echo "║      DataContaBL — Instalador Alpine Linux       ║"
    echo "╚══════════════════════════════════════════════════╝"
    printf "${NC}\n"
}

step() { printf "\n${GREEN}▶ ${BOLD}%s${NC}\n" "$1"; }
ok()   { printf "  ${GREEN}✓ %s${NC}\n" "$1"; }
warn() { printf "  ${YELLOW}⚠ %s${NC}\n" "$1"; }
fail() { printf "${RED}✗ ERROR: %s${NC}\n" "$1"; exit 1; }
hr()   { echo "  ──────────────────────────────────────────────"; }

# ── Verificaciones previas ────────────────────────────────────────────────────
print_banner

[ "$(id -u)" = "0" ] || fail "Este script debe ejecutarse como root: sudo sh install.sh"

if [ ! -f /etc/alpine-release ]; then
    warn "No se detectó Alpine Linux. El script está optimizado para Alpine."
    printf "  ¿Continuar de todas formas? [s/N]: "
    read CONT
    [ "$CONT" = "s" ] || [ "$CONT" = "S" ] || exit 0
fi

# ── Recopilación de datos de configuración ────────────────────────────────────
step "Configuración"
echo ""
printf "${BOLD}  Conexión a la base de datos MySQL/MariaDB${NC}\n"
hr

printf "  Host de BD        [192.168.85.50]: "
read INPUT_DB_HOST
DB_HOST="${INPUT_DB_HOST:-192.168.85.50}"

printf "  Puerto de BD      [32769]: "
read INPUT_DB_PORT
DB_PORT="${INPUT_DB_PORT:-32769}"

printf "  Nombre de la BD   [DataContaBL]: "
read INPUT_DB_NAME
DB_NAME="${INPUT_DB_NAME:-DataContaBL}"

printf "  Usuario de BD     [DataContaBL]: "
read INPUT_DB_USER
DB_USER="${INPUT_DB_USER:-DataContaBL}"

printf "  Contraseña de BD: "
stty -echo
read DB_PASSWORD
stty echo
echo ""

echo ""
printf "${BOLD}  Servidor${NC}\n"
hr

printf "  IP o dominio de esta máquina: "
read SERVER_IP
[ -n "$SERVER_IP" ] || fail "La IP del servidor es obligatoria."

printf "  Puerto Gunicorn   [8000]: "
read INPUT_PORT
GUNICORN_PORT="${INPUT_PORT:-8000}"

printf "  Trabajadores Gunicorn (workers) [auto]: "
read INPUT_WORKERS
if [ -n "$INPUT_WORKERS" ] && echo "$INPUT_WORKERS" | grep -qE '^[0-9]+$'; then
    WORKERS="$INPUT_WORKERS"
else
    CPU_COUNT=$(nproc 2>/dev/null || echo 1)
    WORKERS=$(( CPU_COUNT * 2 + 1 ))
fi

# Generar SECRET_KEY aleatoria
SECRET_KEY=$(python3 -c "import secrets,string; print(''.join(secrets.choice(string.ascii_letters+string.digits+'!@#%^*(-_=+)') for _ in range(60)))" 2>/dev/null \
    || cat /dev/urandom | tr -dc 'a-zA-Z0-9!@#%^*' | head -c 60)

# ── Resumen y confirmación ────────────────────────────────────────────────────
echo ""
printf "${BOLD}  Resumen de instalación${NC}\n"
hr
printf "  Directorio:    %s\n" "$INSTALL_DIR"
printf "  Repositorio:   %s\n" "$GITHUB_REPO"
printf "  Base de datos: %s@%s:%s/%s\n" "$DB_USER" "$DB_HOST" "$DB_PORT" "$DB_NAME"
printf "  Servidor:      http://%s:%s\n" "$SERVER_IP" "$GUNICORN_PORT"
printf "  Workers:       %s\n" "$WORKERS"
hr
echo ""
printf "  ¿Iniciar la instalación? [s/N]: "
read CONFIRM
[ "$CONFIRM" = "s" ] || [ "$CONFIRM" = "S" ] || { echo "  Instalación cancelada."; exit 0; }

# =============================================================================
#  INSTALACIÓN
# =============================================================================

# ── 1. Paquetes del sistema ───────────────────────────────────────────────────
step "Instalando paquetes del sistema..."

apk update --quiet
apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    git \
    curl \
    build-base \
    gcc \
    musl-dev \
    linux-headers \
    mariadb-dev \
    mariadb-connector-c-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    libwebp-dev \
    2>&1 | tail -5

ok "Paquetes del sistema instalados"

# ── 2. Clonar repositorio ─────────────────────────────────────────────────────
step "Descargando el proyecto desde GitHub..."

if [ -d "$INSTALL_DIR" ]; then
    BACKUP="${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    warn "El directorio ${INSTALL_DIR} ya existe. Se moverá a ${BACKUP}"
    mv "$INSTALL_DIR" "$BACKUP"
fi

git clone --quiet "$GITHUB_REPO" "$INSTALL_DIR"
ok "Proyecto descargado en ${INSTALL_DIR}"

# ── 3. Entorno virtual Python ─────────────────────────────────────────────────
step "Creando entorno virtual Python..."

python3 -m venv "$VENV_DIR"
$PIP install --quiet --upgrade pip setuptools wheel
ok "Entorno virtual creado en ${VENV_DIR}"

# ── 4. Dependencias Python ────────────────────────────────────────────────────
step "Instalando dependencias Python..."

$PIP install --quiet -r "${INSTALL_DIR}/requirements.txt"
ok "Dependencias instaladas"

# ── 5. Directorios necesarios ─────────────────────────────────────────────────
mkdir -p "${INSTALL_DIR}/logs"
mkdir -p "${INSTALL_DIR}/staticfiles"
mkdir -p "${INSTALL_DIR}/media/company_logos"

# ── 6. Configuración local (local_settings.py) ───────────────────────────────
step "Generando configuración local..."

cat > "${INSTALL_DIR}/config/local_settings.py" << PYEOF
# =============================================================================
#  Configuración local — generada por install.sh el $(date)
#  NO subir este archivo a git (está en .gitignore)
# =============================================================================

DEBUG = False

SECRET_KEY = '${SECRET_KEY}'

ALLOWED_HOSTS = ['${SERVER_IP}', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '${DB_NAME}',
        'USER': '${DB_USER}',
        'PASSWORD': '${DB_PASSWORD}',
        'HOST': '${DB_HOST}',
        'PORT': '${DB_PORT}',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Rutas absolutas — no depende de BASE_DIR
STATIC_ROOT = '${INSTALL_DIR}/staticfiles'
MEDIA_ROOT  = '${INSTALL_DIR}/media'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '${INSTALL_DIR}/logs/error.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'ERROR',
    },
}
PYEOF

# Añadir import de local_settings al final de settings.py (solo si no existe)
if ! grep -q "local_settings" "${INSTALL_DIR}/config/settings.py"; then
    cat >> "${INSTALL_DIR}/config/settings.py" << 'SETTINGSEOF'

# ── Overrides locales (no subir a git) ────────────────────────────────────────
try:
    from .local_settings import *  # noqa: F401,F403
except ImportError:
    pass
SETTINGSEOF
fi

# Añadir local_settings.py al .gitignore si existe
if [ -f "${INSTALL_DIR}/.gitignore" ]; then
    grep -q "local_settings.py" "${INSTALL_DIR}/.gitignore" \
        || echo "config/local_settings.py" >> "${INSTALL_DIR}/.gitignore"
fi

ok "Configuración local generada"

# ── 7. Migraciones y estáticos ────────────────────────────────────────────────
step "Aplicando migraciones de base de datos..."

cd "$INSTALL_DIR"
$PYTHON manage.py migrate --no-input
ok "Migraciones aplicadas"

step "Recopilando archivos estáticos..."
$PYTHON manage.py collectstatic --no-input --quiet
ok "Archivos estáticos en ${INSTALL_DIR}/staticfiles/"

# ── 8. Configuración de Gunicorn ──────────────────────────────────────────────
step "Configurando Gunicorn..."

cat > "${INSTALL_DIR}/gunicorn.conf.py" << GCEOF
# Gunicorn — configuración generada por install.sh
bind             = "0.0.0.0:${GUNICORN_PORT}"
workers          = ${WORKERS}
worker_class     = "sync"
timeout          = 120
keepalive        = 5
max_requests     = 1000
max_requests_jitter = 100
preload_app      = True
accesslog        = "${INSTALL_DIR}/logs/access.log"
errorlog         = "${INSTALL_DIR}/logs/gunicorn.log"
loglevel         = "warning"
capture_output   = True
GCEOF

ok "gunicorn.conf.py generado (${WORKERS} workers, puerto ${GUNICORN_PORT})"

# ── 9. Script de arranque manual ──────────────────────────────────────────────
cat > "${INSTALL_DIR}/start.sh" << STARTEOF
#!/bin/sh
# Arranque manual de DataContaBL
cd ${INSTALL_DIR}
${GUNICORN} config.wsgi:application -c ${INSTALL_DIR}/gunicorn.conf.py
STARTEOF
chmod +x "${INSTALL_DIR}/start.sh"

cat > "${INSTALL_DIR}/stop.sh" << STOPEOF
#!/bin/sh
# Parada manual de DataContaBL
pkill -f "gunicorn.*datacontabl" 2>/dev/null && echo "Gunicorn detenido" || echo "No había proceso Gunicorn en ejecución"
STOPEOF
chmod +x "${INSTALL_DIR}/stop.sh"

# ── 10. Servicio OpenRC (Alpine Linux) ────────────────────────────────────────
step "Creando servicio OpenRC..."

cat > "/etc/init.d/${SERVICE_NAME}" << SRCEOF
#!/sbin/openrc-run
# DataContaBL OpenRC service

name="${SERVICE_NAME}"
description="DataContaBL — Django/Gunicorn application"
command="${GUNICORN}"
command_args="config.wsgi:application -c ${INSTALL_DIR}/gunicorn.conf.py"
command_background=true
pidfile="/run/\${RC_SVCNAME}.pid"
directory="${INSTALL_DIR}"
output_log="${INSTALL_DIR}/logs/openrc.log"
error_log="${INSTALL_DIR}/logs/openrc.log"

depend() {
    need net
    after firewall
}

start_pre() {
    checkpath --directory --mode 0755 /run
    cd "${INSTALL_DIR}"
}
SRCEOF

chmod +x "/etc/init.d/${SERVICE_NAME}"
rc-update add "$SERVICE_NAME" default 2>/dev/null || warn "No se pudo añadir al arranque automático"
rc-service "$SERVICE_NAME" start 2>/dev/null || warn "No se pudo iniciar el servicio (puede que OpenRC no esté disponible en este entorno)"

ok "Servicio OpenRC configurado: ${SERVICE_NAME}"

# ── 11. Resumen final ─────────────────────────────────────────────────────────
echo ""
printf "${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════════════╗"
echo "║        ✓  Instalación completada                 ║"
echo "╚══════════════════════════════════════════════════╝"
printf "${NC}"
echo ""
printf "  ${BOLD}Acceso:${NC}       http://%s:%s\n"        "$SERVER_IP" "$GUNICORN_PORT"
printf "  ${BOLD}Directorio:${NC}   %s\n"                  "$INSTALL_DIR"
printf "  ${BOLD}Logs:${NC}         %s/logs/\n"            "$INSTALL_DIR"
printf "  ${BOLD}Config local:${NC} %s/config/local_settings.py\n" "$INSTALL_DIR"
echo ""
printf "${BOLD}  Comandos útiles:${NC}\n"
printf "    rc-service %-12s start|stop|restart|status\n" "$SERVICE_NAME"
printf "    tail -f %s/logs/gunicorn.log\n"               "$INSTALL_DIR"
printf "    tail -f %s/logs/error.log\n"                  "$INSTALL_DIR"
printf "    sh %s/start.sh   # arranque manual\n"         "$INSTALL_DIR"
printf "    sh %s/stop.sh    # parada manual\n"           "$INSTALL_DIR"
echo ""
printf "  ${YELLOW}⚠  El archivo local_settings.py contiene credenciales.${NC}\n"
printf "  ${YELLOW}   No lo subas a git ni lo compartas.${NC}\n"
echo ""
