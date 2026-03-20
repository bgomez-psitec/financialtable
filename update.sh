#!/bin/sh
# =============================================================================
#  DataContaBL — Script de actualización
#  Uso:  sh update.sh
#  Requisitos: ejecutar como root en el servidor Alpine Linux
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
INSTALL_DIR="/DataContaBL"
SERVICE_NAME="datacontabl"
VENV_DIR="${INSTALL_DIR}/venv"
PYTHON="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"

# ── Helpers ───────────────────────────────────────────────────────────────────
print_banner() {
    echo ""
    printf "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════╗"
    echo "║      DataContaBL — Actualización del servidor    ║"
    echo "╚══════════════════════════════════════════════════╝"
    printf "${NC}\n"
}

step() { printf "\n${GREEN}▶ ${BOLD}%s${NC}\n" "$1"; }
ok()   { printf "  ${GREEN}✓ %s${NC}\n" "$1"; }
warn() { printf "  ${YELLOW}⚠ %s${NC}\n" "$1"; }
fail() { printf "${RED}✗ ERROR: %s${NC}\n" "$1"; exit 1; }
info() { printf "  ${CYAN}%s${NC}\n" "$1"; }
hr()   { echo "  ──────────────────────────────────────────────"; }

# ── Verificaciones previas ────────────────────────────────────────────────────
print_banner

[ "$(id -u)" = "0" ] || fail "Este script debe ejecutarse como root: sudo sh update.sh"
[ -d "$INSTALL_DIR" ] || fail "No se encontró el directorio ${INSTALL_DIR}. ¿Está instalada la aplicación?"
[ -f "${VENV_DIR}/bin/python" ] || fail "No se encontró el entorno virtual en ${VENV_DIR}."
[ -f "${INSTALL_DIR}/config/local_settings.py" ] || fail "No existe local_settings.py. Ejecuta install.sh primero."

# ── Mostrar versión actual ────────────────────────────────────────────────────
cd "$INSTALL_DIR"

CURRENT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "desconocido")
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "desconocida")

echo ""
printf "${BOLD}  Estado actual${NC}\n"
hr
printf "  Versión:  %s\n" "$CURRENT_VERSION"
printf "  Commit:   %s\n" "$CURRENT_COMMIT"
printf "  Rama:     %s\n" "$(git branch --show-current 2>/dev/null || echo 'main')"
hr

echo ""
printf "  ¿Continuar con la actualización? [s/N]: "
read CONFIRM
[ "$CONFIRM" = "s" ] || [ "$CONFIRM" = "S" ] || { echo "  Actualización cancelada."; exit 0; }

# =============================================================================
#  ACTUALIZACIÓN
# =============================================================================

# ── 1. Detener el servicio ────────────────────────────────────────────────────
step "Deteniendo el servicio..."

if rc-service "$SERVICE_NAME" status >/dev/null 2>&1; then
    rc-service "$SERVICE_NAME" stop
    ok "Servicio detenido"
else
    # Intentar matar Gunicorn si no hay OpenRC disponible
    if pkill -f "gunicorn.*config.wsgi" 2>/dev/null; then
        ok "Proceso Gunicorn detenido"
    else
        warn "No había servicio en ejecución — continuando"
    fi
fi

# ── 2. Descargar cambios de GitHub ───────────────────────────────────────────
step "Descargando última versión de GitHub..."

# Preservar cambios locales no comiteados (no debería haberlos, pero por seguridad)
if git diff --quiet && git diff --cached --quiet; then
    info "Directorio limpio, actualizando..."
else
    warn "Hay cambios locales sin commitear — se preservarán con git stash"
    git stash push -m "update.sh backup $(date +%Y%m%d_%H%M%S)"
fi

git fetch --quiet origin
REMOTE_COMMIT=$(git rev-parse --short origin/main 2>/dev/null || git rev-parse --short origin/master)
git pull --quiet origin main 2>/dev/null || git pull --quiet origin master

NEW_VERSION=$(cat VERSION 2>/dev/null || echo "desconocida")
NEW_COMMIT=$(git rev-parse --short HEAD)

ok "Código actualizado: ${CURRENT_COMMIT} → ${NEW_COMMIT}  (v${NEW_VERSION})"

# ── 3. Actualizar dependencias Python ────────────────────────────────────────
step "Actualizando dependencias Python..."

$PIP install --quiet --upgrade pip setuptools wheel
$PIP install --quiet -r "${INSTALL_DIR}/requirements.txt"
ok "Dependencias actualizadas"

# ── 4. Migraciones de base de datos ──────────────────────────────────────────
step "Aplicando migraciones de base de datos..."

$PYTHON manage.py migrate --no-input
ok "Migraciones aplicadas"

# ── 5. Archivos estáticos ─────────────────────────────────────────────────────
step "Recopilando archivos estáticos..."

mkdir -p "${INSTALL_DIR}/staticfiles"
mkdir -p "${INSTALL_DIR}/media/company_logos"
$PYTHON manage.py collectstatic --no-input -v 0
ok "Estáticos actualizados en ${INSTALL_DIR}/staticfiles/"

# ── 6. Reiniciar el servicio ──────────────────────────────────────────────────
step "Iniciando el servicio..."

if [ -f "/etc/init.d/${SERVICE_NAME}" ]; then
    rc-service "$SERVICE_NAME" start
    sleep 2
    if rc-service "$SERVICE_NAME" status >/dev/null 2>&1; then
        ok "Servicio ${SERVICE_NAME} iniciado correctamente"
    else
        warn "El servicio no respondió — revisa los logs"
    fi
else
    warn "No se encontró el servicio OpenRC '${SERVICE_NAME}'"
    warn "Arranca manualmente con:  sh ${INSTALL_DIR}/start.sh"
fi

# ── 7. Resumen ────────────────────────────────────────────────────────────────
echo ""
printf "${GREEN}${BOLD}"
echo "╔══════════════════════════════════════════════════╗"
echo "║        ✓  Actualización completada               ║"
echo "╚══════════════════════════════════════════════════╝"
printf "${NC}"
echo ""
printf "  ${BOLD}Versión anterior:${NC}  v%s  (%s)\n" "$CURRENT_VERSION" "$CURRENT_COMMIT"
printf "  ${BOLD}Versión actual:${NC}    v%s  (%s)\n" "$NEW_VERSION"     "$NEW_COMMIT"
printf "  ${BOLD}Logs:${NC}              %s/logs/\n" "$INSTALL_DIR"
echo ""
printf "${BOLD}  Comandos útiles:${NC}\n"
printf "    rc-service %-12s status|restart|stop\n" "$SERVICE_NAME"
printf "    tail -f %s/logs/gunicorn.log\n" "$INSTALL_DIR"
printf "    tail -f %s/logs/error.log\n"    "$INSTALL_DIR"
echo ""
