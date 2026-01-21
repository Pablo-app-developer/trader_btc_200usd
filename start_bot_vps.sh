#!/bin/bash
# Script to run SOL Sniper Bot on VPS with auto-restart

cd /root/sol-bot-200

# Activate virtual environment if exists, otherwise run directly
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run bot with nohup to survive terminal disconnections
nohup python3 sol_sniper_bot.py > bot_output.log 2>&1 &

echo "Bot started in background. PID: $!"
echo "Log file: bot_output.log"
echo "To view live logs: tail -f bot_output.log"
echo "To stop bot: pkill -f sol_sniper_bot.py"
