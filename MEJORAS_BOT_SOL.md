# PLAN DE MEJORAS PARA EL BOT DE SOL - RETO $200 USD
# Fecha: 01 Febrero 2026

## PROBLEMA IDENTIFICADO:
- WinRate 50% pero pérdida neta (-$135 en 4 días)
- Esto indica que las pérdidas son mayores que las ganancias
- Necesitamos mejor gestión de riesgo/beneficio

## MEJORAS PROPUESTAS (En orden de prioridad):

### 1. AJUSTAR RATIO RIESGO/BENEFICIO ⭐⭐⭐⭐⭐
**Problema:** Stop Loss muy amplio (3%) vs Take Profit no definido
**Solución:** Implementar Take Profit automático

```python
# En run_live_trader.py, línea ~183
# AGREGAR TAKE PROFIT MECÁNICO
if self.current_position == 1:
    pnl_pct = (price - self.entry_price) / self.entry_price
    
    # NUEVO: Take Profit al 2% (Ratio 1:1.5 con SL de 3%)
    if pnl_pct >= 0.02:  # 2% ganancia
        logger.info(f"🎯 TAKE PROFIT ACTIVADO a ${price:.2f} (+{pnl_pct*100:.2f}%)")
        action = 2  # Force Sell
    
    # Stop Loss existente
    elif pnl_pct <= -self.stop_loss_pct:
        logger.warning(f"🛡️ STOP LOSS ACTIVADO...")
        action = 2
```

**Impacto Esperado:** Con WinRate 50%, ganar 2% en wins y perder 3% en losses = Balance positivo

---

### 2. REDUCIR STOP LOSS PARA $200 ⭐⭐⭐⭐
**Problema:** SL de 3% = -$6 por operación perdedora (muy alto para cuenta de $200)
**Solución:** Reducir a 1.5% para preservar capital

```python
# En config/assets.py o directamente en run_live_trader.py línea 61
self.stop_loss_pct = 0.015  # 1.5% en lugar de 3%
```

**Impacto:** Pérdida máxima de $3 por trade en lugar de $6

---

### 3. FILTRO DE VOLATILIDAD ⭐⭐⭐⭐
**Problema:** SOL es muy volátil, el bot puede estar entrando en momentos caóticos
**Solución:** Solo operar cuando la volatilidad es moderada

```python
# En fetch_market_data(), después de calcular indicadores
# Agregar ATR (Average True Range)
df['ATR'] = self.calculate_atr(df, 14)
current_atr = df['ATR'].iloc[-1]
atr_ma = df['ATR'].rolling(50).mean().iloc[-1]

# En execute_trade(), antes de comprar
if action == 1:
    # Solo comprar si volatilidad es normal (no extrema)
    if current_atr > atr_ma * 1.5:
        logger.info("⚠️ Volatilidad extrema detectada. Esperando...")
        return  # Skip trade
```

---

### 4. TRAILING STOP DINÁMICO ⭐⭐⭐
**Problema:** No hay trailing stop, dejamos que las ganancias se evaporen
**Solución:** Implementar trailing stop que siga el precio

```python
# Agregar a __init__
self.highest_price_in_trade = 0.0

# En execute_trade(), cuando estamos en posición
if self.current_position == 1:
    # Actualizar máximo
    if price > self.highest_price_in_trade:
        self.highest_price_in_trade = price
    
    # Trailing Stop: Si cae 1% desde el máximo
    trailing_loss = (price - self.highest_price_in_trade) / self.highest_price_in_trade
    if trailing_loss <= -0.01:  # -1% desde pico
        logger.info(f"📉 TRAILING STOP: Cayó 1% desde máximo ${self.highest_price_in_trade:.2f}")
        action = 2
```

---

### 5. FILTRO DE TENDENCIA MÁS ESTRICTO ⭐⭐⭐
**Problema:** Puede estar comprando contra tendencia
**Solución:** Solo comprar si precio está sobre EMA 50 Y EMA 200

```python
# En fetch_market_data(), retornar también las EMAs
return recent_data, current_close, df['EMA_50'].iloc[-1], df['EMA_200'].iloc[-1]

# En execute_trade()
if action == 1:
    # Solo comprar si estamos en tendencia alcista clara
    if price < ema_50 or price < ema_200:
        logger.info("📊 Precio bajo EMAs. Esperando tendencia alcista...")
        return
```

---

### 6. OPTIMIZAR PARÁMETROS CON OPTUNA ⭐⭐⭐⭐⭐
**Mejor opción:** Re-entrenar el modelo con los parámetros optimizados que encontramos

Usar los parámetros del `best_breakout_sol.json`:
```json
{
    "breakout_period": 35,
    "ema_period": 23,
    "stop_loss": 0.0172,
    "ts_trigger": 0.0096,
    "ts_dist": 0.0080
}
```

---

## RECOMENDACIÓN INMEDIATA (Quick Win):

**Implementar las mejoras 1 y 2 AHORA:**
1. Take Profit al 2%
2. Stop Loss reducido a 1.5%

Esto debería convertir el bot de -$135 a positivo con el mismo WinRate del 50%.

¿Quieres que implemente estas mejoras ahora?
