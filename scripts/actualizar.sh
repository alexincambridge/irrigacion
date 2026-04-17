#!/bin/bash
# ============================================================
#  actualizar.sh — Actualizar proyecto en la Raspberry Pi
#
#  Ejecutar directamente en la RPi:
#    cd /home/alexdev/Documents/irrigacion
#    ./scripts/actualizar.sh
#
#  Qué hace:
#    1. git pull (descarga últimos cambios)
#    2. Instala dependencias nuevas (pip)
#    3. Migra la base de datos (si hay cambios)
#    4. Reinicia el servicio systemd
#    5. Verifica que todo funciona
# ============================================================

set -e

# ── Configuración ──
PROJECT_DIR="/home/alexdev/Documents/irrigacion"
SERVICE_NAME="irrigacion"
BRANCH="main"
BACKUP_DB=true

# ── Colores ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}ℹ️  $1${NC}"; }
ok()    { echo -e "${GREEN}✅ $1${NC}"; }
warn()  { echo -e "${YELLOW}⚠️  $1${NC}"; }
fail()  { echo -e "${RED}❌ $1${NC}"; exit 1; }

echo ""
echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  🔄 Actualizar — Sistema de Riego Inteligente${NC}"
echo -e "${CYAN}  $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo ""

cd "$PROJECT_DIR" || fail "No se encuentra $PROJECT_DIR"

# ── 1. Backup de la base de datos ──
if [ "$BACKUP_DB" = true ] && [ -f instance/irrigation.db ]; then
    info "Paso 1/5 — Backup de la base de datos"
    BACKUP_FILE="instance/irrigation_backup_$(date '+%Y%m%d_%H%M%S').db"
    cp instance/irrigation.db "$BACKUP_FILE"
    ok "Backup: $BACKUP_FILE"

    # Limpiar backups antiguos (mantener últimos 5)
    ls -t instance/irrigation_backup_*.db 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
else
    info "Paso 1/5 — Sin base de datos, saltando backup"
fi

# ── 2. Git pull ──
info "Paso 2/5 — Descargando cambios (git pull)"

# Guardar cambios locales si los hay
if ! git diff --quiet 2>/dev/null; then
    warn "Hay cambios locales, guardando stash..."
    git stash push -m "auto-stash antes de actualizar $(date '+%Y%m%d_%H%M')"
fi

BEFORE=$(git rev-parse HEAD 2>/dev/null || echo "none")
git pull origin "$BRANCH" 2>&1
AFTER=$(git rev-parse HEAD 2>/dev/null || echo "none")

if [ "$BEFORE" = "$AFTER" ]; then
    ok "Ya estás en la última versión"
else
    COMMITS=$(git log --oneline "$BEFORE".."$AFTER" 2>/dev/null | wc -l)
    ok "$COMMITS commit(s) nuevos descargados"
    echo ""
    git log --oneline "$BEFORE".."$AFTER" 2>/dev/null | head -10 | while read line; do
        echo -e "    ${GREEN}→${NC} $line"
    done
    echo ""
fi

# ── 3. Instalar dependencias ──
info "Paso 3/5 — Verificando dependencias (pip)"
pip3 install -r requirements.txt --quiet 2>&1
ok "Dependencias actualizadas"

# ── 4. Migrar base de datos ──
info "Paso 4/5 — Migrando base de datos"
if [ -f scripts/migrate_db.py ]; then
    python3 scripts/migrate_db.py 2>&1 && ok "Migración completada" || warn "Migración falló (puede que no haya cambios)"
else
    warn "No se encontró scripts/migrate_db.py, saltando"
fi

# ── 5. Reiniciar servicio ──
info "Paso 5/5 — Reiniciando servicio"

if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    sudo systemctl restart "$SERVICE_NAME"
    sleep 3

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        ok "Servicio $SERVICE_NAME reiniciado y activo"
    else
        fail "El servicio no arrancó. Revisa con: sudo journalctl -u $SERVICE_NAME -n 20"
    fi
else
    warn "Servicio $SERVICE_NAME no está habilitado en systemd"
    echo "   Para iniciar manualmente: python3 run.py"
fi

# ── Resumen ──
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 Actualización completada${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo ""
echo "  📋 Versión: $(git log --oneline -1 2>/dev/null || echo 'N/A')"
echo "  🕐 Hora:    $(date '+%Y-%m-%d %H:%M:%S')"

if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo -e "  🟢 Estado:  ${GREEN}ACTIVO${NC}"
else
    echo -e "  🔴 Estado:  ${RED}INACTIVO${NC}"
fi

echo ""

