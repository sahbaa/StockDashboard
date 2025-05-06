import dash
from dash import dash,html,dcc
from dash import Input,Output
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf
from dash_bootstrap_templates import ThemeSwitchAIO,template_from_url
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import StockScrapper
from flask_caching import Cache



# StockList:
stock_list = ['AAPL', 'MSFT', 'JPM', 'AMZN', 'KO', 'PFE', 'TSLA', 'NVDA', 'MCD', 'XOM']
# Reade Data
df = yf.download("TSLA", start="2022-01-01")

print("Empty?", df.empty)
# Set Date as specific Date
df.reset_index(inplace=True)
# Changing the colName
df.columns = ['date','open','high','low','close','Adj Close','vol']

df = df.drop('Adj Close',axis=1)
# prepare the MA:
df['MA9'] = df['close'].rolling(window=9).mean()
df['MAV9'] = df['vol'].rolling(window=9).mean()
df_long = df.melt(id_vars='date',value_name='cl&ma',value_vars=['close','MA9'],var_name='type')
#Define Themes
lightTheme,darkTheme = dbc.themes.LUX,dbc.themes.CYBORG
bootstrapTheme = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
app = dash.Dash(__name__,title='AAPL Stock',external_stylesheets=[lightTheme,bootstrapTheme])

app.layout = dbc.Container([
                dbc.Row([
                    html.Div([ThemeSwitchAIO(aio_id='themeswithcer',themes=[lightTheme, darkTheme])]),
                    
                    html.Div([
                        html.H4('Here you can watch all News about Stocks')
                    ]),
                    html.Div([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4(id='newsAAPL',className='cardForNews')
                            ])
                        ])

                    ])
                        
                ]),
                dbc.Row([
                    html.Div([dcc.RangeSlider(id='rngSlider',value=[0,1000],step=5,marks=None,
                                              min=0, max= 1000,tooltip={"always_visible": True}) ]),
                    
                    html.Div([ 
                        dcc.DatePickerRange(id='datepicker',start_date="2022-01-01", 
                                            end_date="2023-12-31",
                                            min_date_allowed='2022-01-01',
                                            max_date_allowed='2025-12-31')

                    ]), 

                    html.Div([
                        dbc.Card([
                            dbc.CardHeader('inforamtion'),
                            dbc.CardBody([
                                html.H3(id='infoStock',className='cardInfoAboutStock')
                    ])])]),
                                            
                    html.Div([
                        dbc.Col([
                        dcc.Checklist(id='closeLine',options=[{'label': 'Show TrendLine', 'value': '1'}],value=[]),
                        dcc.Dropdown(id='MaSelctr',value='MA9' , options=[{'label':i , 'value':i} for  i in ['MA9','MA21','MA30']]),
                        dcc.Dropdown(id = 'selectorStock', value='TSLA',options=[{'label':i,'value':i} for i in stock_list]),
                        dcc.Dropdown(id='RSISlctr' , options=[{'label':i,'value':i} for i in [14,26,52]],value=14),
                          ],width=6)]),
                                                                     
                                                                    
                    html.Div([dcc.Loading(dcc.Graph(id='grph',figure={},style={'margin-bottom': '0px', 'padding': '0px'}))])
                ])

            ])
# Cach
# ===============================
cach = Cache(app.server,config={'CACHE_TYPE': 'SimpleCache',
                                'CACHE_DEFAULT_TIMEOUT': 1800 })

@cach.memoize()
def get_data(stock):
    mydf = StockScrapper.scrapping(stock)
    
    return mydf


# ================================
# Define for clickable news
# ================================

@app.callback(
        [Output(component_id='newsAAPL',component_property='children')],
        [Input(component_id='selectorStock', component_property = 'value')]
)

def get_clickable_news(stock):
    my_df = get_data(stock)
    elements = []

    for _, row in my_df.iterrows():
        title = row['news']
        link = row['links']
        if pd.notnull(title) and pd.notnull(link):
            elements.append(
                html.Div(
                    html.A(title, href=link, target="_blank",
                           style={'color': 'blue', 'textDecoration': 'none', 'marginBottom': '5px', 'display': 'block'})
                )
            )
    return [html.Div(elements)]
   
# ==============================
@app.callback(
    [
     Output(component_id='infoStock', component_property='children'),   
     Output(component_id='grph',component_property='figure')
    ]
    ,
    [Input(ThemeSwitchAIO.ids.switch("themeswithcer"),"value"),
     Input(component_id='selectorStock', component_property = 'value'),
     Input(component_id='MaSelctr',component_property='value'),
     Input(component_id='RSISlctr',component_property='value'),
     Input(component_id='closeLine',component_property='value'),
     Input(component_id='rngSlider',component_property='value'),
     Input(component_id='datepicker',component_property='start_date'),
     Input(component_id='datepicker',component_property='end_date')])

def declaration (tgl,dslctr,maslctr,rsiperiod,chkTrndL,rngslider,startdate,enddate):

    # create Dateset for analysis 
    df = yf.download(dslctr, start="2022-01-05")
    # Set Date as specific Date
    df = df.reset_index()
    # Changing the colName
    df.columns = ['date','open','high','low','close','Adj Close','vol']
    df = df.drop('Adj Close',axis=1)
    # datafraame after rangeslider 
    
    dff = df.copy(deep= True)
    startdate = str(startdate).split('T')[0]
    enddate = str(enddate).split('T')[0]
    dff['date'] = pd.to_datetime(dff['date']).dt.strftime('%Y-%m-%d')
    dff = dff[(dff['date']>=startdate) & (dff['date']<=enddate)]
    
 
    # defining the card for duration-incr/decr of close price in percentage
    if startdate in dff['date'].values: 
        close_start = float(dff[dff['date']==startdate]['close'].values[0])
    else:
        close_start = dff.iloc[0]['close']
    if enddate in dff['date'].values : 
        close_end = dff[dff['date']==enddate]['close'].values[0]
    else:
        close_end = dff.iloc[-1]['close']

    change = (close_end-close_start)/close_start  
    if close_end > close_start :
        tcolor = 'green'
        change = (close_end-close_start)/close_start  
    else :
        tcolor = 'red'
        change = (close_start-close_end)/close_start    
    info = [
    html.P(f"SURVAY RANGE IS {startdate} UNTILL {enddate}"),
    html.Div([html.Div("Changing During This Period"),
    html.Div(f"{change:.2f}%",style = {'color':tcolor})],style={'display':'flex'}),
    html.Div(f"In This Period Max Price In Close Price is : {dff['close'].max():.2f} And Min Price is {dff['close'].min():.2f} ")
    ]

     # prepare the MA
    dff['MA9'] = dff['close'].rolling(window=9).mean()
    dff['MA21'] = dff['close'].rolling(window=21).mean()
    dff['MA30'] = dff['close'].rolling(window=30).mean()
    dff['MAV9'] = dff['vol'].rolling(window=9).mean()



    # Adding RSI indicator  :
    # 100-(100/(1+mean of gain in 14 days /mean of loss in 14 days)) AND gain = delta.clip(lower=0) AND loss = -delta.clip(upper=0)
    # delta.rolling(window =14).mean()
    delta = dff['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=int(rsiperiod)).mean()
    avg_loss = loss.rolling(window=int(rsiperiod)).mean()
    rs = avg_gain / avg_loss
    dff['RSI'] = 100 - (100 / (1 + rs))


    # specify the theme
    tem = template_from_url(lightTheme if tgl else darkTheme)
    # Base Plot :
    #===================
    base_fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[1.2, 0.4 , 0.4]
    )

    # ------------------------
    #  candle Stick by go
    base_fig.add_trace(
        go.Candlestick(
            x=dff['date'],
            open=dff['open'],
            high=dff['high'],
            low=dff['low'],
            close=dff['close'],
            name='Candlestick'
        ),
        row=1, col=1
    )
    # ------------------------

    # if check list for trendline has been checked:
    # ====================================
    if '1' in chkTrndL:
        line_fig = px.line(dff, x='date', y='close', template=tem)
        for trace in line_fig.data:
            base_fig.add_trace(trace, row=1, col=1)

    # MA
    # ===================================
    ma_fig = px.line(dff, x='date', y=maslctr, template=tem)
    for trace in ma_fig.data:
        base_fig.add_trace(trace, row=1, col=1)


    # Volume Chart
    # ====================================
    vol_fig = px.bar(dff, x='date', y='vol', template=tem)
    for trace in vol_fig.data:
        base_fig.add_trace(trace, row=2, col=1)

    # MA on Volume chart
    mav_fig = px.line(dff, x='date', y='MAV9', template=tem)
    for trace in mav_fig.data:
        base_fig.add_trace(trace, row=2, col=1)

    # latest version 
    base_fig.update_layout(template=tem, xaxis_rangeslider_visible=False)
    

    # add Rsi in the thirs row  :
    rsi_plot = px.line(dff,x='date' , y = 'RSI')

    for fig  in rsi_plot.data:
        base_fig.add_trace(fig,row=3,col=1)
    tmp = dff.copy()
    tmp['70'] = 70
    tmp['30'] = 30
    line70= px.line(tmp,x='date',y='70', template=tem)
    line30 = px.line(tmp,x='date', y='30'  , template= tem)
    for fig in line30.data:
        base_fig.add_trace(fig,row=3,col=1)
    for fig in line70.data :
        base_fig.add_trace(fig,row = 3,col = 1)
    return   info , base_fig

    

if __name__ == '__main__':
    app.run_server(debug=True)