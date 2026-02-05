#!/bin/bash
# Sistema de Gestión Unificado de Bots de Trading
# Autor: Antigravity Agent
# Fecha: 2026-01-20

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║     🤖 ANTIGRAVITY BOT MANAGEMENT SYSTEM 🤖         ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Funciones de utilidad
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar si Docker está corriendo
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker no está corriendo o no tienes permisos"
        info "Intenta: sudo systemctl start docker"
        exit 1
    fi
}

# Comandos principales

cmd_start() {
    local bot=$1
    
    if [ -z "$bot" ]; then
        error "Especifica qué bot iniciar: btc, eth, sol, all"
        info "Uso: $0 start [btc|eth|sol|all]"
        exit 1
    fi
    
    check_docker
    
        docker-compose up -d trader_btc_200usd trader_eth_200usd trader_sol_200usd board_200usd
        success "Todos los bots iniciados"
    else
        info "Iniciando bot de ${bot^^}..."
        docker-compose up -d "trader_${bot}_200usd"
        success "Bot de ${bot^^} iniciado"
    fi
    
    echo ""
    cmd_status
}

cmd_stop() {
    local bot=$1
    
    if [ -z "$bot" ]; then
        error "Especifica qué bot detener: btc, eth, sol, all"
        info "Uso: $0 stop [btc|eth|sol|all]"
        exit 1
    fi
    
    check_docker
    
    if [ "$bot" = "all" ]; then
        info "Deteniendo todos los bots..."
        docker-compose down
        success "Todos los bots detenidos"
    else
        info "Deteniendo bot de ${bot^^}..."
        docker-compose stop "trader_${bot}_200usd"
        success "Bot de ${bot^^} detenido"
    fi
}

cmd_restart() {
    local bot=$1
    
    if [ -z "$bot" ]; then
        error "Especifica qué bot reiniciar: btc, eth, sol, all"
        info "Uso: $0 restart [btc|eth|sol|all]"
        exit 1
    fi
    
    check_docker
    
        docker-compose restart trader_btc_200usd trader_eth_200usd trader_sol_200usd
        success "Todos los bots reiniciados"
    else
        info "Reiniciando bot de ${bot^^}..."
        docker-compose restart "trader_${bot}_200usd"
        success "Bot de ${bot^^} reiniciado"
    fi
    
    echo ""
    cmd_status
}

cmd_status() {
    check_docker
    
    echo -e "${CYAN}📊 ESTADO DE LOS BOTS${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Verificar cada bot
    for bot in btc eth sol; do
        container="trader_${bot}_200usd"
        if docker ps --filter "name=$container" --filter "status=running" | grep -q $container; then
            echo -e "${GREEN}✅ ${bot^^} Bot:${NC} RUNNING"
        else
            echo -e "${RED}❌ ${bot^^} Bot:${NC} STOPPED"
        fi
    done
    
    echo ""
    
    # TensorBoard
    if docker ps --filter "name=board_200usd" --filter "status=running" | grep -q board_200usd; then
        echo -e "${GREEN}✅ TensorBoard:${NC} RUNNING"
        echo "   └─ URL: http://localhost:6007"
    else
        echo -e "${YELLOW}⚠️  TensorBoard:${NC} STOPPED"
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

cmd_logs() {
    local bot=$1
    local follow=${2:-""}
    
    if [ -z "$bot" ]; then
        error "Especifica de qué bot ver logs: btc, eth, sol"
        info "Uso: $0 logs [btc|eth|sol] [--follow|-f]"
        exit 1
    fi
    
    check_docker
    
    local container="trader_${bot}_200usd"
    
    if [ "$follow" = "--follow" ] || [ "$follow" = "-f" ]; then
        info "Mostrando logs en tiempo real de ${bot^^}... (Ctrl+C para salir)"
        docker logs -f --tail 50 $container
    else
        info "Mostrando últimos logs de ${bot^^}..."
        docker logs --tail 100 $container
    fi
}

cmd_stats() {
    check_docker
    
    echo -e "${CYAN}📈 ESTADÍSTICAS DE RECURSOS${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    docker stats --no-stream trader_btc_200usd trader_eth_200usd trader_sol_200usd board_200usd 2>/dev/null || \
        warning "Algunos contenedores no están corriendo"
}

cmd_clean() {
    warning "Esto detendrá todos los bots y limpiará contenedores viejos"
    read -p "¿Estás seguro? (s/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        info "Limpiando sistema Docker..."
        docker-compose down
        docker system prune -f
        success "Limpieza completada"
    else
        info "Limpieza cancelada"
    fi
}

cmd_deploy() {
    info "Reconstruyendo imagen Docker..."
    docker-compose build
    
    success "Imagen reconstruida"
    
    info "Reiniciando todos los bots..."
    docker-compose up -d trader_btc_200usd trader_eth_200usd trader_sol_200usd board_200usd
    
    success "Deploy completado"
    echo ""
    cmd_status
}

cmd_tensorboard() {
    local port=${1:-6007}
    
    info "Iniciando TensorBoard en puerto $port..."
    docker-compose up -d board_200usd
    
    success "TensorBoard iniciado"
    info "Accede en: http://localhost:$port"
    info "o en VPS: http://107.174.133.37:$port"
}

cmd_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="backups"
    
    info "Creando backup de modelos..."
    
    mkdir -p $backup_dir
    
    if [ -d "models/PRODUCTION" ]; then
        tar -czf "$backup_dir/models_$timestamp.tar.gz" models/PRODUCTION/
        success "Backup creado: $backup_dir/models_$timestamp.tar.gz"
        
        # Mostrar tamaño
        size=$(du -h "$backup_dir/models_$timestamp.tar.gz" | cut -f1)
        info "Tamaño: $size"
    else
        warning "No se encontró el directorio models/PRODUCTION/"
    fi
}

cmd_health() {
    check_docker
    
    echo -e "${CYAN}🏥 HEALTH CHECK COMPLETO${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 1. Verificar contenedores
    echo -e "\n${YELLOW}1. Estado de Contenedores${NC}"
    for bot in btc eth sol; do
        if docker ps -q -f name=trader_$bot | grep -q .; then
            echo -e "   ${GREEN}✅ trader_$bot está corriendo${NC}"
        else
            echo -e "   ${RED}❌ trader_$bot NO está corriendo${NC}"
        fi
    done
    
    # 2. Verificar logs recientes
    echo -e "\n${YELLOW}2. Verificando Logs Recientes${NC}"
    for bot in btc eth sol; do
        container="trader_${bot}_200usd"
        if docker ps -q -f name=$container | grep -q .; then
            errors=$(docker logs --since 1h $container 2>&1 | grep -i "error\|exception\|failed" | wc -l)
            if [ $errors -eq 0 ]; then
                echo -e "   ${GREEN}✅ $container: Sin errores en última hora${NC}"
            else
                echo -e "   ${YELLOW}⚠️  $container: $errors errores en última hora${NC}"
            fi
        fi
    done
    
    # 3. Verificar espacio en disco
    echo -e "\n${YELLOW}3. Espacio en Disco${NC}"
    df_output=$(df -h . | tail -1)
    available=$(echo $df_output | awk '{print $4}')
    usage=$(echo $df_output | awk '{print $5}')
    echo -e "   Disponible: $available | Uso: $usage"
    
    # 4. Verificar memoria
    echo -e "\n${YELLOW}4. Uso de Memoria${NC}"
    free -h | grep Mem | awk '{print "   Total: " $2 " | Usado: " $3 " | Libre: " $4}'
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

cmd_help() {
    print_banner
    echo "USO: $0 <comando> [opciones]"
    echo ""
    echo "COMANDOS DISPONIBLES:"
    echo ""
    echo "  📱 GESTIÓN DE BOTS:"
    echo "    start <bot>         Iniciar bot (btc|eth|sol|all)"
    echo "    stop <bot>          Detener bot (btc|eth|sol|all)"
    echo "    restart <bot>       Reiniciar bot (btc|eth|sol|all)"
    echo "    status              Ver estado de todos los bots"
    echo ""
    echo "  📊 MONITOREO:"
    echo "    logs <bot> [-f]     Ver logs (usa -f para seguir en tiempo real)"
    echo "    stats               Ver estadísticas de recursos"
    echo "    health              Health check completo del sistema"
    echo ""
    echo "  🔧 MANTENIMIENTO:"
    echo "    deploy              Reconstruir y redesplegar todos los bots"
    echo "    clean               Limpiar contenedores y sistema Docker"
    echo "    backup              Crear backup de modelos"
    echo ""
    echo "  📈 UTILIDADES:"
    echo "    tensorboard [port]  Iniciar TensorBoard (default: 6006)"
    echo "    help                Mostrar esta ayuda"
    echo ""
    echo "EJEMPLOS:"
    echo "  $0 start all          # Iniciar todos los bots"
    echo "  $0 logs btc -f        # Ver logs de BTC en tiempo real"
    echo "  $0 restart eth        # Reiniciar bot de Ethereum"
    echo "  $0 health             # Verificar salud del sistema"
    echo "  $0 backup             # Crear backup de modelos"
    echo ""
}

# Main
main() {
    local command=$1
    shift
    
    case $command in
        start)
            print_banner
            cmd_start "$@"
            ;;
        stop)
            print_banner
            cmd_stop "$@"
            ;;
        restart)
            print_banner
            cmd_restart "$@"
            ;;
        status)
            print_banner
            cmd_status
            ;;
        logs)
            cmd_logs "$@"
            ;;
        stats)
            print_banner
            cmd_stats
            ;;
        clean)
            print_banner
            cmd_clean
            ;;
        deploy)
            print_banner
            cmd_deploy
            ;;
        tensorboard)
            print_banner
            cmd_tensorboard "$@"
            ;;
        backup)
            print_banner
            cmd_backup
            ;;
        health)
            print_banner
            cmd_health
            ;;
        help|--help|-h|"")
            cmd_help
            ;;
        *)
            error "Comando desconocido: $command"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
