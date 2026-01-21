#!/bin/bash
echo "=== SOL Sniper Bot VPS Deployment ==="
echo "Checking Python version..."
python3 --version

echo ""
echo "Checking dependencies..."
python3 -c "import ccxt; import pandas; import numpy; print('✅ All dependencies OK')" 2>&1

echo ""
echo "Testing bot startup..."
cd /root/sol-bot-200
timeout 30 python3 sol_sniper_bot.py 2>&1 | head -30

echo ""
echo "To run bot in background:"
echo "  nohup python3 sol_sniper_bot.py > bot.log 2>&1 &"
echo ""
echo "To view logs:"
echo "  tail -f bot.log"
