# ECB Data Info (Python SDMX Wrapper Client API)
<p align="center">
  <img src="https://raw.githubusercontent.com/RobertHennings/ECB_DATAINFO/refs/heads/main/ecb_datainfo/src/Logo/ECB_Logo.png" 
       width="400"/>
</p>

# DISCLAIMER: This API Client is not associated with the ECB in any kind - it is a pure personal - nonprofit/non commercial open source software project
The main purpose of this simple API client is the comfortable retrieval of data via Python. Since the ECB does not provide a Python API client, this project is intended to fill this gap. The API client is based on the ECB's SDMX Web Services and provides a simple interface for accessing ECB data. Additionally users can access and filter all
available metadata to find the exact data series they are looking for.

## Credits
Credits go to **Luca Mingarelli** and his already [present Solution](https://github.com/LucaMingarelli/ecbdata) that my personal project is based on but offers some more functionalities as well as robustness and documentation, explaining the usage.
This newer version heavily uses the [SDMX Python Client](https://sdmx1.readthedocs.io/en/latest/walkthrough.html).

## Installation - Not yet available on PyPi
`pip install ecb_datainfo`
<br>or:</br>
`pip3 install ecb_datainfo`

Via git clone:
`git clone https://github.com/RobertHennings/ECB_DATAINFO`

# Class methods documentation
The Python Client can either be used in the default, prespecified setting, by just using:
```python
from ecb_datainfo import ecb_data_info
ecb_data_info_instance = ecb_data_info
```
or by importing the general class and providing optional parameters, such as the SDMX Web Service URL, proxies and whether they should be verified or not:
```python
from ecb_datainfo import ECB_DATA_INFO
ecb_data_info_instance = ECB_DATA_INFO(
    proxies={
        "http": "http://your_proxy:port",
        "https": "https://your_proxy:port"
    },
    verify=True)
```
The normal workflow would look like follows:
<br>
One is interested in a specific dataset, e.g. the "Exchange Rates" dataset or lets say the EURIBOR interest
rate.
## 1. Get an overview about the available main categories
So we could first get an overview about all available main categories, the ECB is grouping data into,
what broadly refer to the ones found [here](https://data.ecb.europa.eu/data/data-categories):
```python
from ecb_datainfo import ecb_data_info
ecb_data_info_instance = ecb_data_info
print(ecb_data_info_instance.all_category_schemes())

MOBILE_NAVI
01                                  Monetary operations
02             Prices, output, demand and labour market
03                    Monetary and financial statistics
04                                   Euro area accounts
05                                   Government finance
06                  External transactions and positions
07                                       Exchange rates
08    Payments and securities trading, clearing, set...
09                                  Banknotes and Coins
10                  Indicators of Financial Integration
11               Real Time Database (research database)
Name: Economic concepts, dtype: object
```
When we look at a sample dataset online in the Statistical Data Warehouse (SDW) of the ECB, we can see that the dataset identifiers/Series Keys follow a certain structure, here see the example of the
[Rate for the overnight maturity calculated as the euro short-term rate plus a spread of 8.5 basis points, Daily](https://data.ecb.europa.eu/data/datasets/EON/EON.D.EONIA_TO.RATE)
```zsh
Last updated: 4 January 2022 09:15 CET
Series key: EON.D.EONIA_TO.RATE
```
For later requesting the actual data and metadata, we want to rebuild this series key and find its components that tell us where the data is located/grouped in the ECB's SDMX Web Services.

The more detailed sub categories in which we can find grouped data can be retrieved by the following method, or alternatively see the Website [Version](https://data.ecb.europa.eu/data/datasets).
## 2. Get an overview about the available subcategories
```python
print(ecb_data_info_instance.all_dataflows)

AGR
AME                                            AMECO
BKN                             Banknotes statistics
BLS                   Bank Lending Survey Statistics
BNT    Shipments of Euro Banknotes Statistics (ESCB)
                           ...                      
SUR                                  Opinion Surveys
TGB                                  Target Balances
TRD                                   External Trade
WTS                                    Trade weights
YC               Financial market data - yield curve
Length: 102, dtype: object
```
## 3. Searching dataflows for a specific keyword
Assume that we suspect the needed EURIBOR interest rate data to be related to the broad financial market "market" category, therefore we try to see whether there is a matching subcategory with a matching abbreviation:

```python
ecb_data_info_instance.search_dataflows(key_word="market", case=False)

FM                    Financial market data
MMS                     Money Market Survey
MMSR     Money Market Statistical Reporting
OMO                  Open market operations
YC      Financial market data - yield curve
dtype: object
```
## 4. Loading all available series keys in a specific dataflow
We suspect that the first category "FM" is the one we are looking for, so we can now either retrieve all available series keys in this category and again search for a name maatching or we directly restrict the search to this category:

4.1. Loading all available series keys in the "FM" category:
```python
ecb_data_info_instance.all_data_keys_for_dataflow(dataflow="FM")

KEY FREQ  ...  UNIT UNIT_MULT
0      FM.A.GB.EUR.4F.CY.EUCRBRDT.HSTA    A  ...  PCPA         0
1      FM.A.GB.EUR.4F.CY.EUCRBRDT.HSTA    A  ...  PCPA         0
2      FM.A.GB.EUR.4F.CY.EUCRBRDT.HSTA    A  ...  PCPA         0
3      FM.A.GB.EUR.4F.CY.EUCRBRDT.HSTA    A  ...  PCPA         0
4      FM.A.GB.EUR.4F.CY.EUCRBRDT.HSTA    A  ...  PCPA         0
...                                ...  ...  ...   ...       ...
83491  FM.Q.US.USD.RT.KR.USDSOFR_.HSTA    Q  ...  PCPA         0
83492  FM.Q.US.USD.RT.KR.USDSOFR_.HSTA    Q  ...  PCPA         0
83493  FM.Q.US.USD.RT.KR.USDSOFR_.HSTA    Q  ...  PCPA         0
83494  FM.Q.US.USD.RT.KR.USDSOFR_.HSTA    Q  ...  PCPA         0
83495  FM.Q.US.USD.RT.KR.USDSOFR_.HSTA    Q  ...  PCPA         0

[83496 rows x 40 columns]
```
4.2. Directly searching for the EURIBOR interest rate series key:
```python
all_data_keys_for_dataflow = ecb_data_info_instance.all_data_keys_for_dataflow(dataflow="FM")
ecb_data_info_instance.search_data_keys_for_dataflow(key_word="euribor",
                                                     all_data_keys_for_dataflow=all_data_keys_for_dataflow)
KEY FREQ  ...  UNIT UNIT_MULT
0     FM.A.U2.EUR.RT.MM.EURIBOR1MD_.HSTA    A  ...  PCPA         0
1     FM.A.U2.EUR.RT.MM.EURIBOR1MD_.HSTA    A  ...  PCPA         0
2     FM.A.U2.EUR.RT.MM.EURIBOR1MD_.HSTA    A  ...  PCPA         0
3     FM.A.U2.EUR.RT.MM.EURIBOR1MD_.HSTA    A  ...  PCPA         0
4     FM.A.U2.EUR.RT.MM.EURIBOR1MD_.HSTA    A  ...  PCPA         0
...                                  ...  ...  ...   ...       ...
2504  FM.Q.U2.EUR.RT.MM.EURIBOR6MD_.HSTA    Q  ...  PCPA         0
2505  FM.Q.U2.EUR.RT.MM.EURIBOR6MD_.HSTA    Q  ...  PCPA         0
2506  FM.Q.U2.EUR.RT.MM.EURIBOR6MD_.HSTA    Q  ...  PCPA         0
2507  FM.Q.U2.EUR.RT.MM.EURIBOR6MD_.HSTA    Q  ...  PCPA         0
2508  FM.Q.U2.EUR.RT.MM.EURIBOR6MD_.HSTA    Q  ...  PCPA         0

[2509 rows x 40 columns]
```
## 5. Loading all available dimensions for series keys in a specific dataflow
Since these are still a lot of possible series keys, we can further filter the results by adding a further constraints, i.e. using the available frequency of the data. We would like to get the daily EURIBOR interest rate, so we can filter the results by the frequency "D" for daily data, but before we can do so, we should check if this parameter is defined for these series keys:
```python
ecb_data_info_instance.search_dataflow_dimensions(dataflow="FM")

['FREQ', 'REF_AREA', 'CURRENCY', 'PROVIDER_FM', 'INSTRUMENT_FM', 'PROVIDER_FM_ID', 'DATA_TYPE_FM', 'TIME_PERIOD']
```

Since 'FREQ' is included in the dataflow dimensions, we can filter the results by this parameter. For filtering even further we can have a look at the attributes of every single series key, that we saved in the pd.DataFrame `all_data_keys_for_dataflow`:
```python
print(all_data_keys_for_dataflow.columns)

Index(['KEY', 'FREQ', 'REF_AREA', 'CURRENCY', 'PROVIDER_FM', 'INSTRUMENT_FM',
       'PROVIDER_FM_ID', 'DATA_TYPE_FM', 'TIME_PERIOD', 'OBS_VALUE',
       'OBS_STATUS', 'OBS_CONF', 'OBS_PRE_BREAK', 'OBS_COM', 'TIME_FORMAT',
       'BREAKS', 'COLLECTION', 'COMPILING_ORG', 'DISS_ORG', 'DOM_SER_IDS',
       'FM_CONTRACT_TIME', 'FM_COUPON_RATE', 'FM_IDENTIFIER', 'FM_LOT_SIZE',
       'FM_MATURITY', 'FM_OUTS_AMOUNT', 'FM_PUT_CALL', 'FM_STRIKE_PRICE',
       'PUBL_MU', 'PUBL_PUBLIC', 'UNIT_INDEX_BASE', 'COMPILATION', 'COVERAGE',
       'DECIMALS', 'SOURCE_AGENCY', 'SOURCE_PUB', 'TITLE', 'TITLE_COMPL',
       'UNIT', 'UNIT_MULT'],
      dtype='object')
```
## 6. Inspecting specific dimensions for series keys in a specific dataflow
Here we again see the 'FREQ' parameter, so we can filter the results by this parameter, but first we should check if the dataflow even offers daily data, since not all dataflows do so.
```python
# First again see what dimensions are available for the dataflow "FM"
ecb_data_info_instance.search_dataflow_dimensions(dataflow="FM")
['FREQ', 'REF_AREA', 'CURRENCY', 'PROVIDER_FM', 'INSTRUMENT_FM', 'PROVIDER_FM_ID', 'DATA_TYPE_FM', 'TIME_PERIOD']
# Check if daily data even exists for the dataflow "FM"
ecb_data_info_instance.search_dataflow_dimension_values(dataflow="FM", dimension="FREQ")

CL_FREQ
A                                               Annual
B                                 Daily - businessweek
D                                                Daily
E                                Event (not supported)
H                                          Half-yearly
M                                              Monthly
N                                             Minutely
Q                                            Quarterly
S    Half-yearly, semester (value introduced in 200...
W                                               Weekly
Name: Frequency code list, dtype: object
```
We see daily data is offered and we directly get the needed abbreviation for filtering down all the retrieved series keys.
```python
daily_euribor_series_keys = all_data_keys_for_dataflow.query('FREQ == "D"').reset_index(drop=True)
print(daily_euribor_series_keys)

KEY FREQ  ...  UNIT UNIT_MULT
0         FM.D.U2.EUR.4F.KR.DFR.CHG    D  ...    PC         0
1         FM.D.U2.EUR.4F.KR.DFR.CHG    D  ...    PC         0
2         FM.D.U2.EUR.4F.KR.DFR.CHG    D  ...    PC         0
3         FM.D.U2.EUR.4F.KR.DFR.CHG    D  ...    PC         0
4         FM.D.U2.EUR.4F.KR.DFR.CHG    D  ...    PC         0
...                             ...  ...  ...   ...       ...
57963  FM.D.U2.EUR.4F.KR.MRR_RT.LEV    D  ...  PCPA         0
57964  FM.D.U2.EUR.4F.KR.MRR_RT.LEV    D  ...  PCPA         0
57965  FM.D.U2.EUR.4F.KR.MRR_RT.LEV    D  ...  PCPA         0
57966  FM.D.U2.EUR.4F.KR.MRR_RT.LEV    D  ...  PCPA         0
57967  FM.D.U2.EUR.4F.KR.MRR_RT.LEV    D  ...  PCPA         0
```
For further understanding we can look at the exact titles:
```python
daily_euribor_series_keys.TITLE_COMPL.unique()

array(['Euro area (changing composition) - Key interest rate - Deposit facility - date of changes (raw data) - Change in percentage points compared to previous rate - Euro, source: ECB',
       'Euro area (changing composition) - Key interest rate - Deposit facility - date of changes (raw data) - Level - Euro, source: ECB',
       'Euro area (changing composition) - Key interest rate - Marginal lending facility - date of changes (raw data) - Change in percentage points compared to previous rate - Euro, source: ECB',
       'Euro area (changing composition) - Key interest rate - Marginal lending facility - date of changes (raw data) - Level - Euro, source: ECB',
       'Euro area (changing composition) - Key interest rate - Main refinancing operations - fixed rate tenders (fixed rate) (date of changes) - Level - Euro, source: ECB',
       'Euro area (changing composition) - Key interest rate - ECB Main refinancing operations - variable rate tenders (minimun bid rate) (date of changes) - Level - Euro, provided by ECB',
       'Euro area (changing composition) - Key interest rate - Main refinancing operations - Minimum bid rate/fixed rate (date of changes) - Level - Euro, source: ECB'],
      dtype=object)

len(daily_euribor_series_keys.TITLE_COMPL.unique())

7
```
## 7. Inspecting measures for series keys in a specific dataflow
We can also see, how the data points are measured:
```python
ecb_data_info_instance.search_dataflow_measures(dataflow="FM")

['OBS_VALUE']
```
How can we now retrieve the actual data for the EURIBOR interest rate?
From the available dimensions: ['FREQ', 'REF_AREA', 'CURRENCY', 'PROVIDER_FM', 'INSTRUMENT_FM', 'PROVIDER_FM_ID', 'DATA_TYPE_FM', 'TIME_PERIOD'], we also want to know what the abbreviations in the 
PROVIDER_FM_ID column mean, since we want to filter the results by the EURIBOR interest rate, which is provided by the ECB.
```python
ecb_data_info_instance.search_dataflow_dimension_values(dataflow="FM", dimension="PROVIDER_FM_ID")

CL_PROVIDER_FM_ID
CPXTIRI              Eurostat Ireland HICP All Items Ex Tobacco NSA
CPTFEMU           Eurostat Eurozone HICP Ex Tobacco Unrevised Se...
FRCPXTOB                                      France CPI Ex Tobacco
ITCPIUNR                         Italy CPI FOI Ex Tobacco Unrevised
BEREALE                      Bloomberg Europe 500 Real Estate Index
                                        ...                        
FEI100125X7       ICE Europe Euro 3 Month EURIBOR Interest Rate ...
MFFM5             MEFF Renta Fija and Variable (MEFF) - Euro 10-...
MCSINDEX                                       Morocco CFG 25 Index
DE0001141554          Bundesobligation DE0001141554 10/10/2014 2.5%
XS1222590488_R                               EDP 2.000 04/22/25 MTN
Name: Financial market data provider identifier code list, Length: 98346, dtype: object

daily_euribor_series_keys.PROVIDER_FM_ID.unique()
array(['DFR', 'MLFR', 'MRR_FR', 'MRR_MBR', 'MRR_RT'], dtype=object)
filter_ids = provider_ids.index.isin(daily_euribor_series_keys.PROVIDER_FM_ID.unique())
print(provider_ids[filter_ids])
CL_PROVIDER_FM_ID
DFR            Deposit facility - date of changes (raw data)
MLFR       Marginal lending facility - date of changes (r...
MRR_FR     Main refinancing operations - fixed rate tende...
MRR_MBR    Main refinancing operations - variable rate te...
MRR_RT     Main refinancing operations - Minimum bid rate...
Name: Financial market data provider identifier code list, dtype: object

daily_euribor_series_keys.query("PROVIDER_FM_ID == 'DFR'")
KEY FREQ  ...  UNIT UNIT_MULT
0      FM.D.U2.EUR.4F.KR.DFR.CHG    D  ...    PC         0
1      FM.D.U2.EUR.4F.KR.DFR.CHG    D  ...    PC         0
2      FM.D.U2.EUR.4F.KR.DFR.CHG    D  ...    PC         0
3      FM.D.U2.EUR.4F.KR.DFR.CHG    D  ...    PC         0
4      FM.D.U2.EUR.4F.KR.DFR.CHG    D  ...    PC         0
...                          ...  ...  ...   ...       ...
19317  FM.D.U2.EUR.4F.KR.DFR.LEV    D  ...  PCPA         0
19318  FM.D.U2.EUR.4F.KR.DFR.LEV    D  ...  PCPA         0
19319  FM.D.U2.EUR.4F.KR.DFR.LEV    D  ...  PCPA         0
19320  FM.D.U2.EUR.4F.KR.DFR.LEV    D  ...  PCPA         0
19321  FM.D.U2.EUR.4F.KR.DFR.LEV    D  ...  PCPA         0

[19322 rows x 40 columns]

```
## 8. Inspecting constraints for series keys in a specific dataflow
To even further filter down, we can display all the constraints we could impose when searching for data:
```python
ecb_data_info_instance.search_dataflow_constraints(dataflow="FM")
{0: {'CURRENCY': 0    JPY
1    EUR
2    GBP
3    DKK
4    USD
5    SEK
Name: CURRENCY, dtype: object, 'PROVIDER_FM_ID': 0         JPONMU_RR
1             U2_5Y
2         US10YT_RR
3         GBP3MFSR_
4             EONIA
5      US10YT_US1YT
6              MLFR
7               DFR
8            UONSTR
9       EURIBOR3MD_
10           U2_10Y
11          CIBOR3M
12          S1ESFNE
13          S1ESH1E
14          S1EST1E
15          S1ESIDE
16      EURIBOR1YD_
17            U2_2Y
18        JP10YT_RR
19          MRR_MBR
20          SIBOR3M
21         USDSOFR_
22          DJES50I
23          S_PCOMP
24          S1ESCGE
25            U2_7Y
26      R_JP10YT_RR
27              MRR
28            U2_3Y
29          OILBRNI
30    R_EURIBOR3MD_
31      EURIBOR1MD_
32          S1ESBME
33          S1ESCSE
34      R_US10YT_RR
35          DJEURST
36          S1ESO1E
37         EUCRBRDT
38          S1ESU1E
39         R_U2_10Y
40        JPY3MFSR_
41          JAPDOWA
42           MRR_FR
43     GB10YT_GB1YT
44        USD10YZ_R
45        JPY10YZ_R
46          S1ESG1E
47           MRR_RT
48        USD3MFSR_
49      EURIBOR6MD_
Name: PROVIDER_FM_ID, dtype: object, 'INSTRUMENT_FM': 0    MM
1    BB
2    EI
3    CY
4    KR
5    BZ
6    SP
Name: INSTRUMENT_FM, dtype: object, 'REF_AREA': 0    SE
1    JP
2    DK
3    GB
4    U2
5    US
Name: REF_AREA, dtype: object, 'PROVIDER_FM': 0    4F
1    RT
2    DS
Name: PROVIDER_FM, dtype: object, 'DATA_TYPE_FM': 0     YLD
1     CHG
2    ASKA
3    SPRE
4    HSTA
5    YLDA
6     LEV
7    YLDE
Name: DATA_TYPE_FM, dtype: object, 'FREQ': 0    A
1    Q
2    B
3    D
4    M
Name: FREQ, dtype: object}}
```
## 9. Loading data for a series key
When we found the correct identifying series key for the data we need, we can simply load the data:
```python
# Load an actual data series
start_date = "2020-01-01"
end_date = "2024-10-23"
sample_data = ecb_data_info_instance.get_ecb_data(series_key="FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA", start_date=start_date, end_date=end_date, include_history=True)
print(sample_data)

KEY  ... VALID_TO
Date                                            ...         
2020-01-01  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA  ...      NaN
2020-02-01  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA  ...      NaN
2020-03-01  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA  ...      NaN
2020-04-01  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA  ...      NaN
2020-05-01  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA  ...      NaN
...                                        ...  ...      ...
2024-05-01  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA  ...      NaN
2024-06-01  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA  ...      NaN
2024-07-01  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA  ...      NaN
2024-08-01  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA  ...      NaN
2024-09-01  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA  ...      NaN

[65 rows x 42 columns]
```
If we are only interested in the observation values of the series, we can simply access the 'OBS_VALUE' column or directly specify to get the series only:
```python
sample_data_series_only = ecb_data_info_instance.get_ecb_data(series_key="FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA", detail="serieskeysonly")
print(sample_data_series_only)

KEY FREQ  ... PROVIDER_FM_ID DATA_TYPE_FM
0  FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA    M  ...    EURIBOR1YD_         HSTA

[1 rows x 8 columns]
```


## Running the ecb_datainfo client locally in a scripting file (.py)
To run the ecb_datainfo client locally (i.e. after cloning the repository), one can just simply create a virtual environment. See the dedetailed documentation [here](https://docs.python.org/3/library/venv.html)
Depending on your python version, open a terminal window, move to the desired loaction via `cd` and create a new virtual environment.
### Creating a virtual environment 
<br><strong>ON MAC</strong></br>
Python < 3:
```zsh
python -m venv name_of_your_virtual_environment
```
Or provide the full path directly:
```zsh
python -m venv /path/to/new/virtual/name_of_your_virtual_environment
```
Python >3:
```zsh
python3 -m venv name_of_your_virtual_environment
```
Or provide the full path directly:
```zsh
python3 -m venv /path/to/new/virtual/name_of_your_virtual_environment
```
### Activating a virtual environment
Activate the virtual environment by:
```zsh
source /path/to/new/virtual/name_of_your_virtual_environment/bin/activate
```
or move into the virtual environment directly and execute:
```zsh
source /bin/activate
```
### Deactivating a virtual environment
Deactivate the virtual environment from anywhere via:
```zsh
deactivate
```
### Downloading dependencies inside the virtual environment
Move to the virtual environment or create a new one, activate it and install the dependencies from the requirements.txt file via:
```zsh
pip install -r requirements.txt
```
or:
```zsh
pip3 install -r requirements.txt
```
Alternatively by providing the full path to the requirements.txt file:
```zsh
pip3 install -r /Users/path/to/project/requirements.txt
```
Make sure the dependencies were correctly loaded:
```zsh
pip list
```
or:
```zsh
pip3 list
```
## Examples

Some further examples on how to run and set up the client in a scripting file can be found
in the `tests` folder in the `local.py` file.
## Contributing
### Commit Style
Please also consider writting meaningful messages in your commits.
```zsh
API: an (incompatible) API change
BENCH: changes to the benchmark suite
BLD: change related to building numpy
BUG: bug fix
DEP: deprecate something, or remove a deprecated object
DEV: development tool or utility
DOC: documentation
ENH: enhancement
MAINT: maintenance commit (refactoring, typos, etc.)
REV: revert an earlier commit
STY: style fix (whitespace, PEP8)
TST: addition or modification of tests
REL: related to releasing numpy
```

## Author
Robert Hennings, 2025
