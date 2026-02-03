"""
Professional Trading Bot Dashboard
Real-time monitoring and analytics for your trading bots
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from trading_database import TradingDatabase
from config_loader import load_bot_config
import os

# Page configuration
st.set_page_config(
    page_title="Trading Bot Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1 {
        color: #00d4ff;
        font-weight: 700;
    }
    h2, h3 {
        color: #00d4ff;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_database():
    """Get database connection"""
    db_path = "trading_bot.db"
    if not os.path.exists(db_path):
        st.warning(f"⚠️ Database not found: {db_path}")
        return None
    return TradingDatabase(db_path)

@st.cache_data(ttl=60)
def load_data():
    """Load data from database"""
    db = get_database()
    if db is None:
        return None, None, None
    
    recent_trades = db.get_recent_trades(limit=100)
    performance = db.get_performance_summary(days=30)
    
    stats = {}
    for symbol in ['SOL', 'ETH', 'BTC']:
        stats[symbol] = db.get_statistics(symbol)
    
    return recent_trades, performance, stats

def create_balance_chart(trades_df, symbol):
    """Create balance evolution chart"""
    if trades_df.empty:
        return None
    
    symbol_trades = trades_df[trades_df['symbol'] == symbol].copy()
    if symbol_trades.empty:
        return None
    
    symbol_trades = symbol_trades.sort_values('timestamp')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=symbol_trades['timestamp'],
        y=symbol_trades['balance_after'],
        mode='lines+markers',
        name='Balance',
        line=dict(color='#00d4ff', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=f"{symbol} Balance Evolution",
        xaxis_title="Time",
        yaxis_title="Balance (USD)",
        template="plotly_dark",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_pnl_chart(trades_df):
    """Create PnL distribution chart"""
    if trades_df.empty:
        return None
    
    sell_trades = trades_df[trades_df['action'] == 'SELL'].copy()
    if sell_trades.empty:
        return None
    
    fig = go.Figure()
    
    colors = ['#00ff88' if x > 0 else '#ff4444' for x in sell_trades['pnl_usd']]
    
    fig.add_trace(go.Bar(
        x=sell_trades['timestamp'],
        y=sell_trades['pnl_usd'],
        marker_color=colors,
        name='PnL'
    ))
    
    fig.update_layout(
        title="Trade PnL Distribution",
        xaxis_title="Time",
        yaxis_title="PnL (USD)",
        template="plotly_dark",
        height=400,
        showlegend=False
    )
    
    return fig

def create_win_rate_pie(stats):
    """Create win rate pie chart"""
    if not stats or stats['total_trades'] == 0:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=['Wins', 'Losses'],
        values=[stats['wins'], stats['losses']],
        marker=dict(colors=['#00ff88', '#ff4444']),
        hole=0.4
    )])
    
    fig.update_layout(
        title="Win/Loss Distribution",
        template="plotly_dark",
        height=300
    )
    
    return fig

# Main Dashboard
def main():
    st.title("📈 Trading Bot Dashboard")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        # Asset selector
        selected_asset = st.selectbox(
            "Select Asset",
            ["All", "SOL", "ETH", "BTC"]
        )
        
        st.markdown("---")
        
        # Time range
        time_range = st.selectbox(
            "Time Range",
            ["Last 24h", "Last 7 days", "Last 30 days", "All time"]
        )
        
        st.markdown("---")
        st.caption("Last updated: " + datetime.now().strftime("%H:%M:%S"))
    
    # Load data
    recent_trades, performance, stats = load_data()
    
    if recent_trades is None:
        st.error("❌ No database found. Start trading to see data!")
        return
    
    # Convert to DataFrame
    trades_df = pd.DataFrame(recent_trades) if recent_trades else pd.DataFrame()
    
    # Overall Metrics
    st.header("📊 Overall Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_trades = len(trades_df[trades_df['action'] == 'SELL']) if not trades_df.empty else 0
    total_pnl = trades_df[trades_df['action'] == 'SELL']['pnl_usd'].sum() if not trades_df.empty else 0
    
    wins = len(trades_df[(trades_df['action'] == 'SELL') & (trades_df['win'] == 1)]) if not trades_df.empty else 0
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    current_balance = trades_df['balance_after'].iloc[0] if not trades_df.empty else 200
    
    with col1:
        st.metric(
            "Total Balance",
            f"${current_balance:.2f}",
            f"{((current_balance - 200) / 200 * 100):+.2f}%"
        )
    
    with col2:
        st.metric(
            "Total Trades",
            total_trades,
            f"{wins} wins"
        )
    
    with col3:
        st.metric(
            "Win Rate",
            f"{win_rate:.1f}%",
            "Good" if win_rate >= 50 else "Needs improvement"
        )
    
    with col4:
        pnl_delta = "Profit" if total_pnl > 0 else "Loss"
        st.metric(
            "Total PnL",
            f"${total_pnl:.2f}",
            pnl_delta
        )
    
    st.markdown("---")
    
    # Asset Performance
    st.header("💎 Asset Performance")
    
    col1, col2, col3 = st.columns(3)
    
    for idx, (symbol, col) in enumerate(zip(['SOL', 'ETH', 'BTC'], [col1, col2, col3])):
        with col:
            st.subheader(f"{symbol}")
            
            asset_stats = stats.get(symbol)
            if asset_stats and asset_stats['total_trades'] > 0:
                st.metric("Trades", asset_stats['total_trades'])
                st.metric("Win Rate", f"{asset_stats['win_rate']:.1f}%")
                st.metric("Total PnL", f"${asset_stats['total_pnl_usd']:.2f}")
                
                # Win rate pie chart
                pie_fig = create_win_rate_pie(asset_stats)
                if pie_fig:
                    st.plotly_chart(pie_fig, use_container_width=True)
            else:
                st.info("No trades yet")
    
    st.markdown("---")
    
    # Charts
    if not trades_df.empty:
        st.header("📈 Charts")
        
        tab1, tab2, tab3 = st.tabs(["Balance Evolution", "PnL Distribution", "Trade History"])
        
        with tab1:
            if selected_asset == "All":
                for symbol in ['SOL', 'ETH', 'BTC']:
                    fig = create_balance_chart(trades_df, symbol)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            else:
                fig = create_balance_chart(trades_df, selected_asset)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No trades for {selected_asset} yet")
        
        with tab2:
            fig = create_pnl_chart(trades_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No completed trades yet")
        
        with tab3:
            st.subheader("Recent Trades")
            
            # Filter trades
            display_df = trades_df.copy()
            if selected_asset != "All":
                display_df = display_df[display_df['symbol'] == selected_asset]
            
            # Format for display
            if not display_df.empty:
                display_df['timestamp'] = pd.to_datetime(display_df['timestamp'])
                display_df = display_df.sort_values('timestamp', ascending=False)
                
                # Select columns to display
                cols_to_show = ['timestamp', 'symbol', 'action', 'entry_price', 'exit_price', 
                               'pnl_pct', 'pnl_usd', 'balance_after', 'reason']
                
                display_df = display_df[cols_to_show].head(50)
                
                # Format numbers
                display_df['pnl_pct'] = display_df['pnl_pct'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")
                display_df['pnl_usd'] = display_df['pnl_usd'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
                display_df['balance_after'] = display_df['balance_after'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
                
                st.dataframe(display_df, use_container_width=True, height=400)
            else:
                st.info("No trades to display")
    else:
        st.info("📭 No trading data available yet. Start trading to see analytics!")
    
    # Footer
    st.markdown("---")
    st.caption("🤖 Trading Bot Dashboard v1.0 | Data updates every 60 seconds")

if __name__ == "__main__":
    main()
