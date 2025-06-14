import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
# Testing related variables
MANUAL_TEST = True
PROXY_SETTINGS = False
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

if MANUAL_TEST:
    if PROXY_SETTINGS:
            logging.info("Importing the general class for setting custom proxy settings.")
            from ecb_datainfo import ECB_DATA_INFO
            ecb_data_info_instance = ECB_DATA_INFO(
                proxies={
                    "http": "http://your_proxy:port",
                    "https": "https://your_proxy:port"
                },
                verify=True)
            print(ecb_data_info_instance)

    else:
        logging.info("Importing the prespecified instance.")
        from ecb_datainfo import ecb_data_info
        ecb_data_info_instance = ecb_data_info

        start_date = "2020-01-01"
        end_date = "2024-10-23"
        sample_data = ecb_data_info_instance.get_ecb_data(
            series_key="FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA",
            start_date=start_date,
            end_date=end_date,
            include_history=True)
        logging.info(f"Sample data loaded successfully. Columns: {sample_data.columns}")
        logging.info(f"Sample data: {sample_data}")
