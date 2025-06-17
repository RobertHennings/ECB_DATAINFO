import os
import sys
import pandas as pd

# Testing related variables
MANUAL_TEST = True
PROXY_SETTINGS = False

# Correctly set the parent directory to the project root
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Debugging: Print the Python path
print("Python Path:", sys.path)

# Import the module after updating the Python path
if MANUAL_TEST:
    if PROXY_SETTINGS:
        print("Importing the general class for setting custom proxy settings.")
        from ecb_datainfo import ECB_DATA_INFO
        ecb_data_info_instance = ECB_DATA_INFO(
            proxies={
                "http": "http://your_proxy:port",
                "https": "https://your_proxy:port"
            },
            verify=True)
        print(ecb_data_info_instance)

    else:
        print("Importing the prespecified instance.")
        from ecb_datainfo import ecb_data_info
        ecb_data_info_instance = ecb_data_info
        # One is interested in a specific dataset, e.g. the "Exchange Rates" dataset or lets say the EURIBOR interest
        # rate.
        # So we could first get an overview about all available main categories, the ECB is grouping data into:
        # 1. Get an overview about the available main categories
        print(ecb_data_info_instance.all_category_schemes())
        # 2. Get an overview about the available subcategories
        print(ecb_data_info_instance.all_dataflows)
        # 3. Searching dataflows for a specific keyword
        print(ecb_data_info_instance.search_dataflows(key_word="market", case=False))
        # 4. Loading all available series keys in a specific dataflow
        # 4.1. Loading all available series keys in the "FM" category:
        print(ecb_data_info_instance.all_data_keys_for_dataflow(dataflow="FM"))
        # 4.2. Directly searching for the EURIBOR interest rate series key:
        all_data_keys_for_dataflow = ecb_data_info_instance.all_data_keys_for_dataflow(dataflow="FM")
        # Safe the sample data
        all_data_keys_for_dataflow.to_excel(
            "daily_euribor_series_keys.xlsx", index=False)
        ecb_data_info_instance.search_data_keys_for_dataflow(
            key_word="euribor",
            all_data_keys_for_dataflow=all_data_keys_for_dataflow)
        # 5. Loading all available dimensions for series keys in a specific dataflow
        print(ecb_data_info_instance.search_dataflow_dimensions(dataflow="FM"))
        # 6. Inspecting specific dimensions for series keys in a specific dataflow
        print(ecb_data_info_instance.search_dataflow_dimensions(dataflow="FM"))
        print(ecb_data_info_instance.search_dataflow_dimension_values(dataflow="FM", dimension="FREQ"))
        # 7. Inspecting measures for series keys in a specific dataflow
        print(ecb_data_info_instance.search_dataflow_measures(dataflow="FM"))
        # 8. Inspecting constraints for series keys in a specific dataflow
        print(ecb_data_info_instance.search_dataflow_constraints(dataflow="FM"))
        # 9. Loading data for a series key
        start_date = "2020-01-01"
        end_date = "2024-10-23"
        sample_data = ecb_data_info_instance.get_ecb_data(
            series_key="FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA",
            start_date=start_date,
            end_date=end_date,
            include_history=True)
        print(sample_data)
        sample_data_series_only = ecb_data_info_instance.get_ecb_data(
            series_key="FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA",
            detail="serieskeysonly")
        print(sample_data_series_only)
        # 10. All Short Term Interest Rates available here: https://data.ecb.europa.eu/publications/financial-markets-and-interest-rates/3030673
        # Euro-Area
        # 1. Unsecured - overnight - short-term rate - Historical close, average of observations through period, Euro area (changing composition), Monthly
        # Series Key: FM.M.U2.EUR.4F.MM.UONSTR.HSTA (Euro short-term rate (€STR))
        # 2. Euribor 1-month - Historical close, average of observations through period, Euro area (changing composition), Monthly
        # Series Key: FM.M.U2.EUR.RT.MM.EURIBOR1MD_.HSTA (1-month deposits (EURIBOR))
        # 3. Euribor 3-month - Historical close, average of observations through period, Euro area (changing composition), Monthly
        # Series Key: FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA (3-month deposits (EURIBOR))
        # 4. Euribor 6-month - Historical close, average of observations through period, Euro area (changing composition), Monthly
        # Series Key: FM.M.U2.EUR.RT.MM.EURIBOR6MD_.HSTA (6-month deposits (EURIBOR))
        # 5. Euribor 12-month - Historical close, average of observations through period, Euro area (changing composition), Monthly
        # Series Key: FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA (12-month deposits (EURIBOR))
        # US-Area
        # 1. USD Federal Reserve Secured Overnight Financing Rate SOFR - FRB - Historical close, average of observations through period, United States, Monthly
        # Series Key: FM.M.US.USD.RT.KR.USDSOFR_.HSTA (Secured overnight financing rate (SOFR))
        # Japan
        # 1. MUTAN (Uncollateralized Overnight Call Rate) - Historical close, average of observations through period, Japan, Monthly
        # Series Key: FM.M.JP.JPY.RT.MM.JPONMU_RR.HSTA (Tokyo overnight average rate (TONAR))
