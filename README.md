# 📊 Stock Visualization Dashboard

A professional, interactive stock analytics dashboard built with [Dash](https://dash.plotly.com/), [Plotly](https://plotly.com/python/), and [Yahoo Finance](https://finance.yahoo.com/) data — designed to visualize historical price trends, volume, moving averages, RSI, and related news.

---

## Features:

- 📈 **Candlestick Chart** with customizable moving averages (MA9, MA21, MA30)
- 🔁 **Theme Toggle** (Light / Dark mode)
- 📆 **Date Range Picker** for flexible analysis
- 📰 **Live News Feed** per stock (scraped from Yahoo Finance)
- 🔍 **RSI Indicator** (Relative Strength Index)
- 📊 **Volume Bars** with moving average overlay
- 📌 **Trendline Toggle** for close price
- ⚡ **Caching** and optional Pickle-based data loading for performance

---

## 📦 Tech Stack

| Tool | Purpose |
|------|---------|
| `Dash` | Web UI and interactivity |
| `Plotly` | Graphs and indicators |
| `Dash Bootstrap Components` | Layout and styling |
| `yfinance` | Stock price data |
| `Selenium` (optional) | Web scraping news |
| `Flask-Caching` | Efficient UI responsiveness |
