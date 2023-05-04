from dash import Dash, html, dcc, Input, Output, register_page, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc # there are other 3rd party dash components, but let's stick with bootstrap for now.
import pandas as pd

# Register this page to the dash application
register_page(__name__, path="/") # fixed path

# Need to read data from dataframe before layout function definition

"""
Define each component. Get data for each component beforehand.
Can learn from Chich's async method to fasten it up,
though it might not be as important as data crawling
"""
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
rLogoSlogan = dbc.Row( # logo+slogan row
    [
        dbc.Col(html.Img(src=PLOTLY_LOGO, className='w-100'), width=2), # 100% width image
        dbc.Col(dbc.Label("MỘT WEB BAO CẢ THỊ TRƯỜNG"), width=10)
    ],
    class_name='g-0',
    align="center"
)

"""
The search box will be more complicated than it looks
The dropdown menu should be constructed from a list of components
Each component ideally should have a ticker's icon, ticker's abbreviation, and name of company.
Since there are about 1500 active VN companies, this must be done in such a way not to break the UI.
Need to find a way to disable dropdown at first click and/or when search string is empty
For now, let's make it a simple loop without async first.
I intentionally make label to be mixed cased, and value+search to be all uppercase.
This will be more apparent in the search_value update callback
In the future, label can be a component containing icon, ticker, and company name
Value is the ticker (uppercase), and search is the company name (uppercase)
Note: to make the label jump to a link, initially I was using dcc.link as labels:
https://community.plotly.com/t/is-it-possible-to-use-links-inside-a-dropdown/70065
However, the link looks ancient, and when clicking outside the link, it won't redirect.
Yet, bootstrap does have DropdownMenuItem that has href property (which dcc does not).
So the way to go is to use dbc.DropdownMenuItem as label, with href point to correct page.
The search box is now completed.
"""
searchOptions = [
    {
        'label':dbc.DropdownMenuItem('Abc: Alpha Beta Cell',href='/ticker/ABC'),
        'value':'ABC',
        'search':'ALPHA BETA CELL',
    },
    {
        'label':dbc.DropdownMenuItem('Def: Delta Epslion Femi',href='/ticker/DEF'),
        'value':'DEF',
        'search':'DELTA EPSILON FEMI'
    },
    {
        'label':dbc.DropdownMenuItem('Ghi: Gamma Hippo Iphone',href='/ticker/'),
        'value':'GHI',
        'search':'GAMMA HIPPO IPHONE'
    },
]
ddSearch = dcc.Dropdown( # 
    placeholder='Tìm kiếm mã chứng khoán...',
    id='ticker_search_box'
)
@callback(# Search box function when user start typing
    Output('ticker_search_box', "options"),
    Input('ticker_search_box', "search_value")
)
def updateTickerSearchDropdown(search_value):
    if not search_value:
        raise PreventUpdate # leave it as-is if not searching
    uc_search_value = search_value.strip().upper() # turn search value to upper case
    return [o for o in searchOptions if uc_search_value in o["value"] or uc_search_value in o["search"]]
    # If it matches either value or search pattern, accept it

# Menu button. Right now only two: home button, and dummy one for whatever purpose later
# 'd-grid' make the buttons expand to all available space
# 'd-md-flex' make it mobile friendly.
# Source: button and buttongroup in dash bootstrap documentation
bgMenu = dbc.ButtonGroup(
    [
        dbc.Button("Home", id='bhome', href='/'),
        dbc.Button("Dummy", id='bdummy', href='/ticker/') # 404
    ], class_name='d-grid d-lg-flex'
)

# This will be a column containing the slogan row, search box, and (maybe?) top menu bar
cTitle = dbc.Col(
    [
        rLogoSlogan,
        ddSearch,
        bgMenu
    ],
    lg=6
)

cAdTop = dbc.Col(dbc.Label("Top Ad placement", size="sm"),lg=6,align='center') # Top advertisement placement

rTop = dbc.Row( # top row, containing title column and top ad column
    [
        cTitle,
        cAdTop
    ]
)

# Generate some mockup dataframe for good signal table (top gainer, etc...)
dfGood = pd.DataFrame({
    'Mã CK': ['VCB', 'AGB', 'SCB', 'VNM'],
    'Giá (x1000 VNĐ)': [132.48, 39.54, 100, 70.1],
    'Thay đổi': [1.35, 1.2135, 0.4123, -0.084],
    'Khối lượng': [1758239, 247194, 72834115, 2213415],
    'Tín hiệu': ['Top Gainer', 'New High', 'Unusual Volume', 'Earning Before']
})
dictGoodSignal = { # signal tooltip definitions
    'Top Gainer': 'Stock that has the most price increase',
    'New High': 'Stock that reached highest price',
    'Unusual Volume': 'Stock that were trade in unusually large volume',
    'Earning Before': 'I think this stock is just before earning report',
}

theaderGood = html.Thead(html.Tr([ # Table header, just a bunch of texts
    html.Th(dfGood.columns[0], className='p-0'), # left aligned
    html.Th(dfGood.columns[1], className='p-0 text-end'), # right aligned
    html.Th(dfGood.columns[2], className='p-0 text-end'), # right aligned
    html.Th(dfGood.columns[3], className='p-0 text-end'), # right aligned
    html.Th(dfGood.columns[4], className='p-0 text-center'), # center aligned
]))

rtbGood = []
ttGoodTicker = []
ttGoodSignal = []
for jr in dfGood.index: # define each row in the table
    tgGoodTicker = "good_ticker_%d" %jr
    tgGoodSignal = "good_signal_%d" %jr
    ticker = dfGood[dfGood.columns[0]][jr]
    price = dfGood[dfGood.columns[1]][jr]
    change = dfGood[dfGood.columns[2]][jr]*100.0
    volume = dfGood[dfGood.columns[3]][jr]
    signal = dfGood[dfGood.columns[4]][jr]
    if change > 0:
        text_color = 'text-success'
    else:
        text_color = 'text-danger'
    rtbGood.append(html.Tr([
        html.Td(dbc.DropdownMenuItem(ticker, id=tgGoodTicker, href=f'/ticker/{ticker}/'), className='p-0'), # ticker name
        html.Td(dbc.DropdownMenuItem(f'{price:.2f}', href=f'/ticker/{ticker}/'), className='p-0 text-end'), # price
        html.Td(dbc.DropdownMenuItem(f'{change:.2f}%', href=f'/ticker/{ticker}/'), className=f'p-0 text-end {text_color}'), # change in percentage
        html.Td(dbc.DropdownMenuItem(f'{volume:,}', href=f'/ticker/{ticker}/'), className='p-0 text-end'), # volume
        html.Td(dbc.DropdownMenuItem(signal, id=tgGoodSignal, href=f'/ticker/{ticker}/'), className='p-0 text-center'), # signal
    ]))
    ttGoodTicker.append(dbc.Tooltip(dbc.Stack(
            [
                html.Img(src=PLOTLY_LOGO, className='w-100'),
                dbc.Label(ticker, class_name='my-0'), # no vertical margin
            ],
            class_name='text-start',
        ),
        target=tgGoodTicker,
        style={'max-width': '300px', 'font-size': '0.5rem'}
    ))
    ttGoodSignal.append(dbc.Tooltip(
        dictGoodSignal[signal],
        target=tgGoodSignal,
        style={'max-width': '300px', 'font-size': '0.5rem'}
    ))

tbodyGood = html.Tbody(rtbGood)

tbGood = dbc.Table([theaderGood,tbodyGood], borderless=True, striped=True, hover=True, size='sm',
                  style={'font-size': '0.65rem'})

rSignal = dbc.Row([
    dbc.Col([tbGood],lg=4)
])

# At the end, merging all components into the layout
layout = dbc.Container([
        rTop,
        rSignal,
    ]
    + ttGoodTicker
    + ttGoodSignal
, fluid=True) # must be named "layout"


