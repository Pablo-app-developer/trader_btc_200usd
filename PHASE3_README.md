# 📊 Phase 3: Professional Dashboard & Monitoring

## 🎯 What's Included

### 1. **Web Dashboard** (`dashboard.py`)
Professional real-time monitoring interface built with Streamlit.

**Features:**
- 📈 Real-time balance tracking
- 💹 PnL distribution charts
- 🎯 Win rate analytics
- 📊 Per-asset performance
- 📜 Trade history table
- 🔄 Auto-refresh every 60 seconds

**Access:** `http://localhost:8501`

---

### 2. **Healthcheck API** (`healthcheck.py`)
RESTful API for system monitoring and bot status.

**Endpoints:**

| Endpoint | Description |
|----------|-------------|
| `/health` | Overall system health |
| `/metrics` | Detailed trading metrics |
| `/status/<symbol>` | Status for specific bot (SOL/ETH/BTC) |

**Access:** `http://localhost:5000`

**Example Response:**
```json
{
  "status": "healthy",
  "uptime_hours": 24.5,
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8
  },
  "bots": {
    "SOL": {
      "status": "active",
      "balance": 205.50,
      "wins": 3,
      "losses": 1
    }
  }
}
```

---

## 🚀 Quick Start

### Option 1: Automatic (Recommended)
```powershell
.\start_dashboard.ps1
```

### Option 2: Manual

**Install dependencies:**
```bash
pip install -r requirements_phase3.txt
```

**Start Healthcheck API:**
```bash
python healthcheck.py
```

**Start Dashboard (in another terminal):**
```bash
streamlit run dashboard.py
```

---

## 📸 Screenshots

### Dashboard Overview
- **Metrics Cards:** Total Balance, Trades, Win Rate, PnL
- **Asset Performance:** Individual stats for SOL, ETH, BTC
- **Charts:** Balance evolution, PnL distribution
- **Trade History:** Detailed table of all trades

### Healthcheck API
- **JSON Responses:** Easy integration with monitoring tools
- **System Metrics:** CPU, Memory, Disk usage
- **Bot Status:** Real-time position and balance info

---

## 🔧 Configuration

Dashboard settings are in `bot_config.yaml`:

```yaml
monitoring:
  tensorboard:
    enabled: true
    port: 6007
  
  healthcheck:
    enabled: true
    port: 5000
```

---

## 🌐 Remote Access (VPS)

To access from anywhere:

**Dashboard:**
```
http://YOUR_VPS_IP:8501
```

**Healthcheck:**
```
http://YOUR_VPS_IP:5000/health
```

**Security Note:** Consider using SSH tunneling or VPN for production.

---

## 📱 Mobile Access

The dashboard is mobile-responsive! Access from your phone:
```
http://YOUR_VPS_IP:8501
```

---

## 🔍 Monitoring Best Practices

1. **Check Dashboard Daily:** Review performance and adjust parameters
2. **Monitor Healthcheck:** Set up alerts if status != "healthy"
3. **Export Data:** Use `/metrics` endpoint for external analysis
4. **Backup Database:** Regular backups of `trading_bot.db`

---

## 🆘 Troubleshooting

**Dashboard not loading?**
- Check if port 8501 is available
- Ensure `trading_bot.db` exists
- Run `streamlit run dashboard.py --server.port 8502` for different port

**Healthcheck not responding?**
- Check if port 5000 is available
- Verify Flask is installed: `pip install flask`
- Check firewall settings

---

## 🎨 Customization

### Change Dashboard Theme
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#00d4ff"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#1e2130"
```

### Add Custom Metrics
Edit `dashboard.py` and add your own charts/metrics.

---

## 📊 Integration Examples

### Prometheus Monitoring
```python
# Add to healthcheck.py
from prometheus_client import Counter, Gauge

trades_counter = Counter('bot_trades_total', 'Total trades')
balance_gauge = Gauge('bot_balance', 'Current balance')
```

### Grafana Dashboard
Import `/metrics` endpoint into Grafana for advanced visualization.

---

## 🚀 Next Steps

- ✅ Phase 1: Telegram Notifications
- ✅ Phase 2: Database + YAML Config
- ✅ Phase 3: Dashboard + Healthcheck
- 🔜 Phase 4: CI/CD + Tests (Optional)

---

**Built with ❤️ for professional trading**
