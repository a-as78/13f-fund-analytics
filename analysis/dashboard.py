import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from math import pi

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('combined_output_transactions.csv')
    df['value_($000)'] = pd.to_numeric(df['value_($000)'].str.replace(',', ''), errors='coerce')
    df['shares'] = pd.to_numeric(df['shares'].str.replace(',', ''), errors='coerce')
    df['change'] = pd.to_numeric(df['change'], errors='coerce')
    df['pct_change'] = pd.to_numeric(df['pct_change'], errors='coerce')
    df.dropna(subset=['stock_symbol', 'fund_name', 'value_($000)', 'quarter'], inplace=True)
    return df

df = load_data()

# --- Sidebar filters ---
funds = df['fund_name'].unique()

DEFAULT_FUNDS = ["325 CAPITAL LLC", "14B Captial Management LP", "1607 Capital Partners, LLC"]
DEFAULT_QUARTER = "2024Q3"
selected_funds = st.sidebar.multiselect("Select Funds", funds, default=DEFAULT_FUNDS)

df['quarter'] = df['quarter'].str.replace(r'(Q\d)\s(\d{4})', r'\2\1', regex=True)
df = df.sort_values('quarter')
quarters = sorted(df['quarter'].unique())
default_ix = quarters.index(DEFAULT_QUARTER)
selected_quarter = st.sidebar.selectbox("Select Quarter", quarters, index=default_ix)

symbols = df['stock_symbol'].unique()
selected_symbols = st.sidebar.multiselect("Select Stock Symbols (Optional)", symbols)


# --- Filter data based on selections ---
filtered_df = df[
    (df['fund_name'].isin(selected_funds)) &
    (df['quarter'] == selected_quarter) 
]

if selected_symbols:
    filtered_df = filtered_df[filtered_df['stock_symbol'].isin(selected_symbols)]

# --- KPIs ---
kpi1 = filtered_df['value_($000)'].sum()
kpi2 = filtered_df['stock_symbol'].nunique()
kpi3 = filtered_df['pct_change'].mean()
kpi4 = filtered_df['pct_change'].std()
kpi5 = len(filtered_df)

st.title("📊 Fund Analysis Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("Total Value ($000)", f"{kpi1:,.0f}")
col2.metric("Unique Stocks", f"{kpi2}")
col3.metric("Avg. % Change", f"{kpi3:.2f}%")

st.caption(f"Average Volatility (Std. Dev.): {kpi4:.2f}%")
st.caption(f"Total Transactions: {kpi5}")

# --- Fund Value ---
# Sort quarters

portfolio = df.groupby(['quarter', 'fund_name'])['value_($000)'].sum().reset_index()
portfolio = portfolio[portfolio['fund_name'].isin(selected_funds)]
quarter_order = sorted(portfolio['quarter'].unique(), key=lambda x: (int(x[:4]), int(x[-1])))
funds = df['fund_name'].unique()

# Apply ordered categorical to the quarter column
portfolio['quarter'] = pd.Categorical(portfolio['quarter'], categories=quarter_order, ordered=True)
complete_index = pd.MultiIndex.from_product([quarter_order, funds], names=['quarter', 'fund_name'])

# Step 5 — Reindex portfolio to include ALL quarter + fund pairs → fill missing with 0
portfolio = portfolio.set_index(['quarter', 'fund_name']).reindex(complete_index, fill_value=0).reset_index()

fig_perf = px.line(
    portfolio[portfolio['fund_name'].isin(selected_funds)],
    x='quarter', y='value_($000)', color='fund_name',
    title="Fund Value"
)
st.plotly_chart(fig_perf, use_container_width=True)

# --- Box Plot ---
st.subheader("Distribution of Stock Values by Fund")
fig_box = px.box(filtered_df, x='fund_name', y='value_($000)', points='all', title="Stocks Value Distribution")
st.plotly_chart(fig_box, use_container_width=True)

# --- Heatmap ---
st.subheader("Heatmap of Top Holdings Across Funds")

quarter_df = df[df['quarter'] == selected_quarter]

top_n = 10
top_stocks = (
    filtered_df.groupby('stock_symbol')['value_($000)']
    .sum()
    .sort_values(ascending=False) 
    .nlargest(top_n)
    .index
)

heat_df = filtered_df[filtered_df['stock_symbol'].isin(top_stocks)].reset_index()

heat_table = heat_df.pivot_table(
    index='fund_name',
    columns='stock_symbol',
    values='value_($000)',
    aggfunc='sum'
).fillna(0)

heat_table = heat_table[top_stocks] 

fig_heat = px.imshow(
    heat_table,
    aspect='auto',
    title=f"Top Stocks Allocation Heatmap - {selected_quarter}",
    labels=dict(x='Stock Symbol', y='Fund Name', color='Value ($000)'),
    color_continuous_scale='Viridis'  

)

st.plotly_chart(fig_heat, use_container_width=True)

# Top stock bar chart
st.subheader("Top Stocks by Value")
top_stocks_df = filtered_df.groupby('stock_symbol')['value_($000)'].sum().nlargest(10).reset_index()

fig_top_stocks = px.bar(
    top_stocks_df,
    x='stock_symbol', y='value_($000)',
    title="Top Stocks by Value",
    color='value_($000)',
    color_continuous_scale='Viridis'
)
st.plotly_chart(fig_top_stocks, use_container_width=True)
# --- Treemap ---
st.subheader("Treemaps of Fund Holdings")
for fund in selected_funds:
    fund_data = filtered_df[filtered_df['fund_name'] == fund].groupby('stock_symbol')['value_($000)'].sum()
    if not fund_data.empty:
        fig_tree = px.treemap(fund_data.reset_index(), path=['stock_symbol'], values='value_($000)', title=f"{fund}: Top Holdings Treemap")
        st.plotly_chart(fig_tree, use_container_width=True)

# --- Radar Chart ---
st.subheader("Peer Radar Chart")
def radar_plot():
    metrics = filtered_df.groupby('fund_name').agg({
        'value_($000)': 'sum',
        'stock_symbol': pd.Series.nunique,
        'pct_change': 'mean',
        'shares': 'sum' 
    }).rename(columns={
        'value_($000)': 'Total Value',
        'stock_symbol': 'Unique Stocks',
        'pct_change': 'Avg % Change',
        'shares': 'Total Shares'
    })

    metrics['Total Shares'] = metrics['Total Shares'] / metrics['Total Shares'].max()
    metrics['Total Value'] = metrics['Total Value'] / metrics['Total Value'].max()
    metrics['Avg % Change'] = metrics['Avg % Change'] / metrics['Avg % Change'].max()
    metrics['Unique Stocks'] = metrics['Unique Stocks'] / metrics['Unique Stocks'].max()

    if metrics.empty:
        st.warning("No data for radar plot.")
        return

    categories = metrics.columns.tolist()
    N = len(categories)
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    for fund in metrics.index:
        values = metrics.loc[fund].tolist() + [metrics.loc[fund].tolist()[0]]
        angles = [n / float(N) * 2 * pi for n in range(N)] + [0]
        ax.plot(angles, values, label=fund)
        ax.fill(angles, values, alpha=0.1)
    ax.set_xticks([n / float(N) * 2 * pi for n in range(N)])
    ax.set_xticklabels(categories)
    ax.set_title("Radar: Peer Metrics")
    ax.legend(loc='upper right')
    st.pyplot(fig)

radar_plot()

# --- % Change Distribution ---
st.subheader("Distribution of % Change")
fig_dist = px.histogram(filtered_df, x='pct_change', nbins=50, title="Histogram: % Change", color='fund_name')
st.plotly_chart(fig_dist, use_container_width=True)

# --- Bubble Chart ---
st.subheader("Bubble Chart: Change vs. Value vs. Shares")
filtered_df = filtered_df.dropna(subset=['pct_change', 'value_($000)', 'shares'])
fig_bubble = px.scatter(
    filtered_df, x='pct_change', y='value_($000)', size='shares',
    color='fund_name', hover_name='stock_symbol',
    title="Bubble Chart: % Change vs. Value vs. Shares"
)
st.plotly_chart(fig_bubble, use_container_width=True)

# --- Dual Axis Chart ---
st.subheader("Volume vs. Average % Change")
vol = filtered_df.groupby('stock_symbol')['shares'].sum().reset_index(name='Total Shares')
chg = filtered_df.groupby('stock_symbol')['pct_change'].mean().reset_index(name='Avg % Change')
combo = pd.merge(vol, chg, on='stock_symbol')
fig_dual = px.bar(combo.sort_values('Total Shares', ascending=False).head(20), x='stock_symbol', y='Total Shares',
                  color='Avg % Change', title="Volume vs. Avg % Change", color_continuous_scale='Viridis')
st.plotly_chart(fig_dual, use_container_width=True)


# --- Top Movers ---
st.subheader("Top Holdings Changes")
mov = filtered_df[['fund_name', 'stock_symbol', 'pct_change', 'value_($000)']].sort_values('pct_change', ascending=False)
st.write("### Top Increases in Fund Allocation")
st.dataframe(mov.head(10))
st.write("### Top Decreases in Fund Allocation")
st.dataframe(mov.tail(10))

