#!/bin/bash
# ============================================================
#  deploy.sh — Desplegar cambios desde Mac a la Raspberry Pi
#
#  Uso:  ./deploy.sh              (commit + push + actualizar RPi)
#         ./deploy.sh "mensaje"    (con mensaje de commit personalizado)
#         ./deploy.sh --push-only  (solo push, sin actualizar RPi)
#
#  Requisitos:
#    - SSH configurado a la RPi (ssh-copy-id alexdev@<IP>)
#    - Git configurado con remote origin
# ============================================================

set -e

# ── Configuración ──
RPI_USER="alexdev"
RPI_HOST="tiger.local"                            # Cambia por IP si no resuelve: 192.168.1.XX
RPI_PROJECT="/home/alexdev/Documents/irrigacion"
SERVICE_NAME="irrigacion"
BRANCH="main"

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
echo -e "${CYAN}════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  🚀 Deploy — Sistema de Riego Inteligente${NC}"
echo -e "${CYAN}════════════════════════════════════════════════${NC}"
echo ""

PUSH_ONLY=false
COMMIT_MSG="Actualización $(date '+%Y-%m-%d %H:%M')"

for arg in "$@"; do
    case $arg in
        --push-only) PUSH_ONLY=true ;;
        *) COMMIT_MSG="$arg" ;;
    esac
done

# ── 1. Git: add + commit + push ──
info "Paso 1/4 — Git commit & push"

cd "$(dirname "$0")"

# Comprobar si hay cambios
if git diff --quiet && git diff --cached --quiet; then
    warn "No hay cambios nuevos en git"
else
    git add -A
    git commit -m "$COMMIT_MSG"
    ok "Commit: $COMMIT_MSG"
fi

git push origin "$BRANCH" 2>&1
ok "Push a origin/$BRANCH completado"

if [ "$PUSH_ONLY" = true ]; then
    echo ""
    ok "Push completado (--push-only). Para actualizar la RPi:"
    echo "   ssh $RPI_USER@$RPI_HOST 'cd $RPI_PROJECT && ./scripts/actualizar.sh'"
    exit 0
fi

# ── 2. Conectar a RPi y actualizar ──
info "Paso 2/4 — Conectando a RPi ($RPI_HOST)..."

if ! ssh -o ConnectTimeout=5 "$RPI_USER@$RPI_HOST" "echo ok" >/dev/null 2>&1; then
    fail "No se puede conectar a $RPI_USER@$RPI_HOST"
fi
ok "Conexión SSH establecida"

# ── 3. Pull + instalar dependencias ──
info "Paso 3/4 — Actualizando código en RPi..."

ssh "$RPI_USER@$RPI_HOST" bash -s <<REMOTE
    set -e
    cd "$RPI_PROJECT"

    echo "  → git pull..."
    git pull origin "$BRANCH" 2>&1

    echo "  → Instalando dependencias..."
    pip3 install -r requirements.txt --break-system-packages --quiet 2>&1

    echo "  → Migrando base de datos..."
    python3 scripts/migrate_db.py 2>&1 || true
REMOTE

ok "Código actualizado en RPi"

# ── 4. Reiniciar servicio ──
info "Paso 4/4 — Reiniciando servicio..."

ssh "$RPI_USER@$RPI_HOST" bash -s <<REMOTE
    set -e
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        sudo systemctl restart "$SERVICE_NAME"
        echo "  → Servicio reiniciado"
        sleep 2
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            echo "  → Estado: ACTIVO ✅"
        else
            echo "  → Estado: FALLIDO ❌"
            sudo journalctl -u "$SERVICE_NAME" --no-pager -n 10
            exit 1
        fi
    else
        echo "  → Servicio no encontrado, iniciando manualmente..."
        cd "$RPI_PROJECT"
        nohup python3 run.py > /dev/null 2>&1 &
        echo "  → Iniciado con PID \$!"
    fi
REMOTE

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 Deploy completado correctamente${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""

