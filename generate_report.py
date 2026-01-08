import json
import os

def create_markdown_report():
    results_file = "reports/results_summary.json"
    report_file = "ESTADO_DE_LAS_PRUEBAS.md"
    
    if not os.path.exists(results_file):
        print("❌ No results found. Run backtest.py first.")
        return
        
    with open(results_file, 'r') as f:
        results = json.load(f)
        
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 🏛️ Informe de Desempeño: Trading Bot Multi-Activo\n\n")
        f.write("Este informe resume los resultados de las pruebas realizadas con el cerebro institucional graduado de Bitcoin y evolucionado para otros activos.\n\n")
        
        f.write("## 📊 Resumen Comparativo\n\n")
        f.write("| Activo | Retorno (%) | Sharpe Ratio | Drawdown Máx (%) | Nª de Trades | Balance Final |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :--- |\n")
        
        for asset, data in results.items():
            sharpe = data.get('sharpe_ratio', 0)
            f.write(f"| **{asset}** | {data['return_pct']:.2f}% | {sharpe:.2f} | {data['max_drawdown_pct']:.2f}% | {data['total_trades']} | ${data['final_balance']:,.2f} |\n")
            
        f.write("\n---\n\n")
        
        for asset, data in results.items():
            f.write(f"## 📈 Análisis Detallado: {asset}\n")
            f.write(f"- **Retorno Total**: {data['return_pct']:.2f}%\n")
            f.write(f"- **Riesgo Máximo (Drawdown)**: {data['max_drawdown_pct']:.2f}%\n")
            f.write(f"- **Actividad**: {data['total_trades']} operaciones ejecutadas.\n")
            f.write(f"- **Eficiencia**: Blindaje institucional del 2% activo.\n\n")
            
            # Note: For markdown to display local images, we use the path relative to the md file.
            f.write(f"![Equity Curve {asset}]({data['chart_path']})\n\n")
            f.write("---\n\n")
            
        f.write("💡 *Informe generado automáticamente por Antigravity Agent.*\n")

    print(f"✅ Reporte generado: {report_file}")

if __name__ == "__main__":
    create_markdown_report()
