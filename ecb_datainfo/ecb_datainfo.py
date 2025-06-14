import io
from typing import List, Dict
import pandas as pd
import requests
import sdmx
import logging
logging.basicConfig(level=logging.INFO)


# Set the static global variables
API_ENDPOINT = "https://sdw-wsrest.ecb.europa.eu"
# Main purposes of the class:
# Primary purpose: 1) Download Data for a provided series key
# Secondary purpose: 2) Get information and search for certain properties

class ECB_DATA_INFO():
    # main ECB API Page: https://data.ecb.europa.eu/help/api/overview
    # sdmx1 library implementation: https://github.com/khaeru/sdmx
    # sdmx handling: https://github.com/dr-leo/pandaSDMX/blob/master/doc/walkthrough.rst
    # other already available wrapper ecb api: from ecbdata import ecbdata
    def __init__(
        self,
        proxies: Dict[str, str]=None,
        verify: bool=None,
        api_endpoint: str=API_ENDPOINT
        ):
        # Set proxies
        self.proxies = proxies
        # verify
        self.verify = verify
        # Set the API endpoint
        self.api_endpoint = api_endpoint
        # establish connection - handling/testing is integrated
        self.__ecb_connect(proxies=proxies, verify=verify)


    ### Connection related class methods
    # Testing the connection
    def __connection_handler(
        self,
        response: requests.models.Response
        ):
        """Testing the response and checking for robustness of returned
           content. Supporting method is used for both the
           sdmx.Client/Response as well as for the generic requests.get

        Args:
            response (requests.models.Response): direct requests response

        Raises:
            Exception: Error Message
                       (Error) Status Code are defined here:
                       https://data.ecb.europa.eu/help/api/status-codes
        """
        # Test the established connection for robustness and validity
        if "dataflow" in dir(response):
            connector_response = response.dataflow().response
        else:
            connector_response = response
        status_code = connector_response.status_code
        response_url = connector_response.url
        response_headers = connector_response.headers
        # Define the potential occuring errors
        errors_msgs = {
            304: "No changes. There have been no changes to the data since the timestamp supplied in the If-Modified-Since header.",
            400: "Syntax error. Syntactic or semantic issue with the parameters supplied.",
            404: "No results found. There are no results matching the query.",
            406: "Not Acceptable.",
            500: "Internal Server Error. Feel free to try again later or to contact the support hotline https://ecb-registration.escb.eu/statistical-information.",
            501: "Not implemented.",
            503: "Service unavailable: Web service is temporarily unavailable.",
            }
        if status_code == 200:
            logging.info(f'Connection established with url: {response_url} and headers: {response_headers}')
        else:
            if status_code in errors_msgs:
                raise Exception(f'Request Error Code: {status_code} - {errors_msgs.get(status_code, "")}')
            else:
                logging.error(f'Unexpected Error: {response_url} - {response_headers}')
                logging.error(f'Request Error Code: {status_code}')
                connector_response.raise_for_status()


    # Establishing the connection
    def __ecb_connect(
        self,
        proxies: Dict[str, str],
        verify: bool
        ):
        """Connect to the ECB sdmx.Client with specified optional
           proxy and validation parameters.
           
           Load directly all available dataflows:
           Dataflows represent groupings of related data from a
           particular statistical domain (e.g. balance of payments).
           They provide a reference to the DSD that applies for a
           particular domain, thereby indicating how the data for that
           domain will look.
           Reference: https://data.ecb.europa.eu/help/api/overview

        Args:
            proxies (Dict[str, str]): proxy dict like:
                                      proxies={'https': '<https-proxy>',
                                               'http': '<http-proxy>'}
            verify (bool): root certificate which can be used to
                           verify the authenticity of the server-side
                           certificate, if False it is used on own risk
        """
        # establish connection via sdmx client for the basic setting
        ecb_connection = sdmx.Client("ECB", proxies=proxies, verify=verify)
        # Test connection for robustness
        self.__connection_handler(response=ecb_connection)
        # set connection
        self.ecb_connection = ecb_connection
        # directly load all available dataflows to be searchable
        self.all_dataflows = sdmx.to_pandas(self.ecb_connection.dataflow().dataflow)


    ### Explanatory class methods - retrieve ECB API Metadata
    def search_dataflows(
        self,
        key_word: str,
        case: bool=False
        ) -> pd.Series:
        """Search in the title of the dataflows for matches, either case
           sensitive or not

        Args:
            key_word (str): key word to search for in the dataflows
            case (bool, optional): Should the search be case sensitive or not.
                                   Defaults to False.

        Returns:
            pd.Series: matches, the abbreviation of the respective
                       dataflow(s) is of importance
        Example:
            >>> ecb_data_info_instance = ECB_DATA_INFO()
            >>> ecb_data_info_instance.search_dataflows(key_word="exchange", case=False)
            EXR                              Exchange Rates
            FXI                 Foreign Exchange Statistics
            SEE    Securities exchange - Trading Statistics
            dtype: object
        """
        return self.all_dataflows[self.all_dataflows.str.contains(key_word, case=case)]


    def search_dataflow_attributes(
        self,
        dataflow: str
        ) -> List[str]:
        """Attributes do not help in identifying statistical data;
           they are characteristics that add useful qualitative
           information, such as the number of decimal places to which
           the data are measured.
           The single attribute values ecaxtly identify a unique time
           series key that can be loaded. I.e:
           "FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA" the single by a .
           separated values represent the attributes.
           Reference: https://data.ecb.europa.eu/help/api/overview

        Args:
            dataflow (str): chosen dataflow

        Returns:
            List[str]: attributes for the dataflow

        Example:
            >>> ecb_data_info_instance = ECB_DATA_INFO()
            >>> ecb_data_info_instance.search_dataflow_attributes(dataflow="SEE")
            ['TIME_FORMAT', 'OBS_STATUS', 'OBS_CONF', 'OBS_PRE_BREAK', 'OBS_COM',
            'COLLECTION', 'COMPILING_ORG', 'DISS_ORG', 'PUBL_ECB', 'PUBL_MU',
            'PUBL_PUBLIC', 'DECIMALS', 'SOURCE_AGENCY', 'TITLE', 'TITLE_COMPL',
            'UNIT', 'UNIT_MULT']
        """
        # Extract the metadata related to a dataflow
        metadata_dataflow = self.ecb_connection.dataflow(dataflow)
        # Explicitly retrieve the DataflowDefinition object
        metadata_dataflow_flow = metadata_dataflow.dataflow.get(dataflow)
        if metadata_dataflow_flow is None:
            raise ValueError(f"No DataflowDefinition found for dataflow: {dataflow}")

        # Access the Data Structure Definition (DSD)
        # data structure definition: DSD
        # this object contains metadata that describes the structure of data in the dataflow
        dsd_flow = metadata_dataflow_flow.structure

        # Extract the attributes and return them as a Pandas DataFrame
        # identifying attributes of a series that belongs to this dataflow
        return sdmx.to_pandas(dsd_flow.attributes.components)


    def search_dataflow_dimensions(
        self,
        dataflow: str
        ) -> List[str]:
        """Dimensions can be used in combination to specifically identify
           statistical data. Dimensions are the measured aspects of a
           phenomenon (e.g. time, place, product, customer) which, in
           unique combinations, specifically identify statistical data.
           --> Actual columns that will be retrieved when loading a time series
           Reference: https://data.ecb.europa.eu/help/api/overview

        Args:
            dataflow (str): chosen dataflow

        Returns:
            List[str]: dimensions (columns) for the dataflow

        Example:
            >>> ecb_data_info_instance = ECB_DATA_INFO()
            >>> ecb_data_info_instance.search_dataflow_dimensions(dataflow="EXR")
            ['FREQ', 'CURRENCY', 'CURRENCY_DENOM', 'EXR_TYPE', 'EXR_SUFFIX', 'TIME_PERIOD']
        """
        # Extract the metadata related to a data flow
        metadata_dataflow = self.ecb_connection.dataflow(dataflow)

        # Explicitly retrieve the DataflowDefinition object
        metadata_dataflow_flow = metadata_dataflow.dataflow.get(dataflow)
        if metadata_dataflow_flow is None:
            raise ValueError(f"No DataflowDefinition found for dataflow: {dataflow}")

        # Access the Data Structure Definition (DSD)
        # data structure definition: DSD
        # this object contains metadata that describes the structure of data in the dataflow
        dsd_flow = metadata_dataflow_flow.structure

        # Extract the dimensions and return them as a Pandas DataFrame
        # here we can see all the columns we would get from a request
        # of a time series belonging to this dataflow
        return sdmx.to_pandas(dsd_flow.dimensions.components)


    def search_dataflow_dimension_values(
        self,
        dataflow: str,
        dimension: str
        ) -> List[str]:
        """Dimensions can be used in combination to specifically identify
           statistical data. Dimensions are the measured aspects of a
           phenomenon (e.g. time, place, product, customer) which, in
           unique combinations, specifically identify statistical data.
           --> Actual columns that will be retrieved when loading a time series
           Reference: https://data.ecb.europa.eu/help/api/overview

        Args:
            dataflow (str): chosen dataflow

        Returns:
            List[str]: dimensions (columns) for the dataflow

        Example:
            >>> ecb_data_info_instance = ECB_DATA_INFO()
            >>> ecb_data_info_instance.search_dataflow_dimension_values(dataflow="EXR", dimension="EXR_TYPE")
                            CL_EXR_TYPE
                BRC0           Real bilateral exchange rate, CPI deflated
                CR00                                         Central rate
                DFC0      Real effective exch. rate deflator based on CPI
                DFC1    Real effective exch. rate deflator based on re...
                DFD0    Real effective exch. rate deflator based on GD...
                DFM0    Real effective exch. rate deflator based on im...
                DFP0    Real effective exch. rate deflator based on pr...
                DFU0    Real effective exch. rate deflator based on UL...
                DFU1    Real effective exch. rate deflator based on UL...
                DFW0    Real effective exch. rate deflator based on wh...
                DFX0    Real effective exch. rate deflator based on ex...
                EN00                         Nominal effective exch. rate
                ER00                        Constant (real) exchange rate
                ERC0               Real effective exch. rate CPI deflated
                ERC1     Real effective exch. rate retail prices deflated
                ERD0     Real effective exch. rate GDP deflators deflated
                ERM0    Real effective exch. rate import unit values d...
                ERP0    Real effective exch. rate producer prices defl...
                ERU0    Real effective exch. rate ULC manufacturing de...
                ERU1    Real effective exch. rate ULC total economy de...
                ERW0    Real effective exch. rate wholesale prices def...
                ERX0    Real effective exch. rate export unit values d...
                F01M                                           1m-forward
                F03M                                           3m-forward
                F06M                                           6m-forward
                F12M                                          12m-forward
                IR00                                      Indicative rate
                NN00    Nominal harmonised competitiveness indicator (...
                NRC0    Real harmonised competitiveness indicator CPI ...
                NRD0    Real harmonised competitiveness indicator GDP ...
                NRP0    Real harmonised competitiveness indicator Prod...
                NRU0    Real harmonised competitiveness indicator ULC ...
                NRU1    Real harmonised competitiveness indicator ULC ...
                OF00                                      Official fixing
                RR00                                       Reference rate
                SP00                                                 Spot
                Name: Exchange rate type code list, dtype: object
        """
        # Extract the metadata related to a data flow
        metadata_dataflow = self.ecb_connection.dataflow(dataflow)

        # Explicitly retrieve the DataflowDefinition object
        metadata_dataflow_flow = metadata_dataflow.dataflow.get(dataflow)
        if metadata_dataflow_flow is None:
            raise ValueError(f"No DataflowDefinition found for dataflow: {dataflow}")

        # Access the Data Structure Definition (DSD)
        # data structure definition: DSD
        # this object contains metadata that describes the structure of data in the dataflow
        dsd_flow = metadata_dataflow_flow.structure

        # Extract dimensions and ensure it's a valid DataFrame
        # here we can see all the columns we would get from a request
        # of a time series belonging to this dataflow
        dimensions_list = sdmx.to_pandas(dsd_flow.dimensions.components)
        # Check if the dimension exists in the dataflow
        if dimension not in dimensions_list:
            raise ValueError(f"Dimension '{dimension}' not found in dataflow: {dataflow}")

        # Retrieve the enumerated values for the specified dimension
        dataflow_dimension_values = dsd_flow.dimensions.get(dimension).local_representation.enumerated

        # Convert the enumerated values to a Pandas DataFrame and return as a list
        values_series = sdmx.to_pandas(dataflow_dimension_values)

        return values_series


    def search_dataflow_constraints(
        self,
        dataflow: str
        ) -> Dict[str, pd.Series]:
        """Look up the value constraints for a dataflow. What unique
           values can be expected and/or given as further filtering
           constraint for specific dimensions (columns).

        Args:
            dataflow (str): Chosen dataflow

        Returns:
            Dict[str, pd.Series]: Dict of the dimension and its
                                  constraints for further filtering on
                                  dimensions (columns).

        Example:
            >>> ecb_data_info_instance = ECB_DATA_INFO()
            >>> ecb_data_info_instance.search_dataflow_constraints(dataflow="EXR")
                    {0: {'CURRENCY_DENOM': 0     ATS
                    1     CHF
                    2     HRK
                    3     ITL
                    4     MXN
                        ... 
                    57    SKK
                    58    PEN
                    59    NZD
                    60    FRF
                    61    BRL
                    Name: CURRENCY_DENOM, Length: 62, dtype: object, 'EXR_SUFFIX': 0    P
                    1    A
                    2    R
                    3    S
                    4    T
                    5    E
                    Name: EXR_SUFFIX, dtype: object, 'FREQ': 0    A
        """
        # Extract the metadata related to a data flow
        metadata_dataflow = self.ecb_connection.dataflow(dataflow)
        # Constraints on valid parameter values for a dataflow
        attribute = f"{dataflow}_CONSTRAINTS"
        return sdmx.to_pandas(metadata_dataflow.constraint.get(attribute, None))


    def search_dataflow_measures(
        self,
        dataflow: str
        ) -> List[str]:
        """In SDMX, the measurement of a phenomenon is known as an
            Observation. A grouping of several Observations is called a
            Dataset.
            Reference: https://data.ecb.europa.eu/help/api/overview

        Args:
            dataflow (str): Chosen dataflow.

        Returns:
            List[str]: Measures of the time series.

        Example:
            >>> ecb_data_info_instance = ECB_DATA_INFO()
            >>> ecb_data_info_instance.search_dataflow_measures(dataflow="SEE")
                    ['OBS_VALUE']
        """
        # Extract the metadata related to a data flow
        metadata_dataflow = self.ecb_connection.dataflow(dataflow)

        # Explicitly retrieve the DataflowDefinition object
        metadata_dataflow_flow = metadata_dataflow.dataflow.get(dataflow)
        if metadata_dataflow_flow is None:
            raise ValueError(f"No DataflowDefinition found for dataflow: {dataflow}")

        # Access the Data Structure Definition (DSD)
        dsd_flow = metadata_dataflow_flow.structure

        return sdmx.to_pandas(dsd_flow.measures.components)


    def all_data_keys_for_dataflow(
        self,
        dataflow: str
        ) -> pd.DataFrame:
        """The single attribute values ecaxtly identify a unique time
           series key that can be loaded. I.e:
           "FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA" where the single by a .
           separated values represent the attributes.
           Here, for a given dataflow, all directly retrievable time series
           (keys) are returned with their comprising attribute values.

        Args:
            dataflow (str): Chosen dataflow

        Returns:
            pd.DataFrame: All available time series (keys) to load and
                          their comprising attribute values, uniquely 
                          identifying them.
        Example:
            >>> ecb_data_info_instance = ECB_DATA_INFO()
            >>> ecb_data_info_instance.all_data_keys_for_dataflow(dataflow="SEE")
                                    KEY FREQ  ...       UNIT UNIT_MULT
                0      SEE.A.AT.WBR0.D00.Z.Q    A  ...  PURE_NUMB         1
                1      SEE.A.AT.WBR0.D00.Z.Q    A  ...  PURE_NUMB         1
                2      SEE.A.AT.WBR0.D00.Z.Q    A  ...  PURE_NUMB         1
                3      SEE.A.AT.WBR0.D01.Z.Q    A  ...  PURE_NUMB         1
                4      SEE.A.AT.WBR0.D01.Z.Q    A  ...  PURE_NUMB         1
                ...                      ...  ...  ...        ...       ...
                23978  SEE.A.X0.OMX0.MKP.W.E    A  ...        EUR         6
                23979  SEE.A.X0.OMX0.MKP.W.E    A  ...        EUR         6
                23980  SEE.A.X0.OMX0.MKP.W.E    A  ...        EUR         6
                23981  SEE.A.X0.OMX0.MKP.W.E    A  ...        EUR         6
                23982  SEE.A.X0.OMX0.MKP.W.E    A  ...        EUR         6
        """
        # CAUTION: This can take very long depending on how many timeseries
        #          are related to the dataflow
        # Check if provided argument is indeed in the existing list
        if dataflow in self.all_dataflows.index:
            req_url = f"https://data-api.ecb.europa.eu/service/data/{dataflow}"
            response = requests.get(req_url,
                                    headers={'Accept': 'text/csv'},
                                    timeout=90)
            # Check for robustness
            self.__connection_handler(response=response)
            df = pd.read_csv(io.StringIO(response.text))
            return df
        else:
            logging.error(f"Provided dataflow: {dataflow} is not existing")


    def search_data_keys_for_dataflow(
        self,
        key_word: str,
        all_data_keys_for_dataflow: pd.DataFrame
        ) -> pd.DataFrame:
        """Search for a keyword in the dimension (column) TITLE_COMPL to
           filter down the potential series key results.

        Args:
            key_word (str): ke word to look for
            all_data_keys_for_dataflow (pd.DataFrame): all available
                                                       series keys for a
                                                       dataflow
        Returns:
            pd.DataFrame: Filtering results.

        Example:
            >>> ecb_data_info_instance = ECB_DATA_INFO()
            >>> ecb_data_info_instance.search_data_keys_for_dataflow(key_word="trade",
                                                     all_data_keys_for_dataflow=all_data_keys_for_dataflow)
                                    KEY FREQ  ...       UNIT UNIT_MULT
                    0      SEE.A.AT.WBR0.EXL.E.E    A  ...        EUR         6
                    1      SEE.A.AT.WBR0.EXL.E.E    A  ...        EUR         6
                    2      SEE.A.AT.WBR0.EXL.E.E    A  ...        EUR         6
                    3      SEE.A.AT.WBR0.EXL.E.E    A  ...        EUR         6
                    4      SEE.A.AT.WBR0.EXL.E.E    A  ...        EUR         6
                    ...                      ...  ...  ...        ...       ...
                    13559  SEE.A.X0.OMX0.EXT.X.Q    A  ...  PURE_NUMB         3
                    13560  SEE.A.X0.OMX0.EXT.X.Q    A  ...  PURE_NUMB         3
                    13561  SEE.A.X0.OMX0.EXT.X.Q    A  ...  PURE_NUMB         3
                    13562  SEE.A.X0.OMX0.EXT.X.Q    A  ...  PURE_NUMB         3
                    13563  SEE.A.X0.OMX0.EXT.X.Q    A  ...  PURE_NUMB         3

                    [13564 rows x 26 columns]
        """
        title_compl_lower = [title_c.lower() for title_c in all_data_keys_for_dataflow.TITLE_COMPL.unique().tolist()]
        key_word_results = [title_c for title_c in title_compl_lower if key_word in title_c]
        return all_data_keys_for_dataflow.query('TITLE_COMPL.str.lower().isin(@key_word_results)').reset_index(drop=True)


    def all_category_schemes(
            self
            ) -> pd.Series:
        """Retrieve all available category schemes, which are
           collections of related categories that can be used to
           classify data. Each category scheme contains a set of
           categories, which are the actual values that can be used to
           filter or group data.

        Returns:
            pd.Series: _description_
        
        Example:
            >>> ecb_data_info_instance = ECB_DATA_INFO()
            >>> ecb_data_info_instance.all_category_schemes()
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
        """ 
        cat_schemes = self.ecb_connection.categoryscheme()
        return sdmx.to_pandas(cat_schemes.category_scheme.MOBILE_NAVI)


    ### Data retrieval class methods - load actual time series data
    def _build_url(
        self,
        series_key: str,
        start_date: str,
        end_date: str,
        detail: str,
        update_after: str,
        first_n_observations: int,
        last_n_observations: int,
        include_history: bool
        ) -> str:
        """Builds the url that will be requested. With additional optional
           parameters to set. Data examples of optional additional
           attributes to set and full documentation:
           https://data.ecb.europa.eu/help/api/data

        Args:
            series_key (str): _description_
            start_date (str): It is possible to define a date range for
                              which Observations are to be returned by
                              using the startPeriod and/or endPeriod
                              parameters. The values should be given
                              according to the syntax defined in ISO 8601
                              or as SDMX reporting periods. The format
                              will vary depending on the frequency.
                              The supported formats are:
                              YYYY for annual data (e.g. 2013);
                              YYYY-S[1-2] for semi-annual data (e.g. 2013-S1);
                              YYYY-Q[1-4] for quarterly data (e.g. 2013-Q1);
                              YYYY-MM for monthly data (e.g. 2013-01);
                              YYYY-W[01-53] for weekly data (e.g. 2013-W01);
                              YYYY-MM-DD for daily data (e.g. 2013-01-01).
            end_date (str): same as for start_date
            detail (str): Using the detail parameter, it is possible to
                          specify the desired amount of information to
                          be returned by the web service.
                          Possible options are:
                          full: the data (Time series and Observations)
                                and the Attributes will be returned.
                                This is the default.
                          dataonly: the Attributes will be excluded from
                                    the returned message.
                          serieskeysonly: only the Time series will be
                                          returned, excluding the
                                          Attributes and the Observations.
                                          This can be used to list Time
                                          series that match a certain
                                          query without returning the
                                          actual data.
                          nodata: the Time series will be returned,
                                  including the Attributes, but the
                                  Observations will not.
            update_after (str): By supplying a percent-encoded ISO 8601
                                timestamp for the updatedAfter parameter,
                                it is possible to retrieve the latest
                                version of changed values in the database
                                after a certain point in time
                                (i.e. updates and revisions).
                                This will include:
                                the Observations that have been added
                                since the supplied timestamp; the
                                Observations that have been revised 
                                since the supplied timestamp; the
                                Observations that have been deleted 
                                since the supplied timestamp.
                                For example, the percent-encoded
                                representation for 2009-05-15T14:15:00+01:00
                                would be: 2009-05-15T14%3A15%3A00%2B01%3A00.
                                
                                Developers who update their local
                                databases with data stored in the ECB
                                Data Portal should make use of the
                                updatedAfter parameter, as this will
                                significantly improve performance.
                                Instead of systematically downloading
                                data that have not changed, you will
                                only receive the changes that were made
                                in the database after you last performed
                                the same query.

                                Should you not be able to handle updates
                                and revisions, or if you would prefer
                                to perform a full refresh of your local
                                database when something has changed,
                                you can use an If-Modified-Since header
                                as an alternative to the updatedAfter
                                parameter described above. This triggers
                                a HTTP conditional request, which will
                                return the data only if something has
                                changed since the timestamp supplied in
                                the If-Modified-Since header. If nothing
                                has changed, the server will respond with
                                a HTTP 304 response code.
            first_n_observations (int): Using the firstNObservations and/or
                                       lastNObservations parameters, it
                                       is possible to specify the maximum
                                       number of Observations to be
                                       returned for each of the matching
                                       Time series, starting from the
                                       first Observation (firstNObservations)
                                       or counting back from the most
                                       recent Observation (lastNObservations).
            last_n_observations (int): same as for first_n_observations
            include_history (bool): Using the includeHistory parameter,
                                    you can instruct the web service to
                                    return previous versions of the
                                    matching data. This allows you to see
                                    how the data have evolved over time
                                    (i.e. see when new data were released,
                                    revised or deleted).
                                    Possible options are:
                                    false: only the version currently
                                            in production will be
                                            returned. This is the default.
                                    true: the version currently in
                                            production and all previous
                                            versions will be returned.
        Returns:
            str: Complete url for request.
        """
        data_flow, series_key_rest = series_key.split(".", 1)
        req_url = f'{self.api_endpoint}/service/data/{data_flow}/{series_key_rest}?format=csvdata'
        # if additional paramters are specified add them to the created url
        if start_date: req_url += f'&startPeriod={start_date}'
        if end_date: req_url += f'&endPeriod={end_date}'
        if detail: req_url += f'&detail={detail}'
        if update_after: req_url += f'&updatedAfter={update_after}'
        if first_n_observations: req_url += f'&firstNObservations={first_n_observations}'
        if last_n_observations: req_url += f'&lastNObservations={last_n_observations}'
        if include_history: req_url += f'&includeHistory={include_history}'
        return req_url


    def get_ecb_data(
        self,
        series_key: str,
        start_date: str=None,
        end_date: str=None,
        detail: str=None,
        update_after: str=None,
        first_n_observations: int=None,
        last_n_observations: int=None,
        include_history: bool=None,
        ascending: bool=True
        ) -> pd.DataFrame:
        """Fetches the specified time series key with given parameters.

        Args:
            series_key (str): time series key to fetch
            start_date (str, optional): see _build_url. Defaults to None.
            end_date (str, optional): see _build_url. Defaults to None.
            detail (str, optional): see _build_url. Defaults to None.
            update_after (str, optional): see _build_url. Defaults to None.
            first_n_observations (int, optional): see _build_url. Defaults to None.
            last_n_observations (int, optional): see _build_url. Defaults to None.
            include_history (bool, optional): see _build_url. Defaults to None.
            ascending (bool, optional): see _build_url. Defaults to True.

        Returns:
            pd.DataFrame: Fetched data for time series key with data
                          dimensions (columns) for respective dataflow.

        Example:
            >>> ecb_data_info_instance = ECB_DATA_INFO()
            >>> start_date = "2020-01-01"
            >>> end_date = "2024-10-23"
            >>> ecb_data_info_instance.get_ecb_data(
                            series_key="FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA",
                            start_date=start_date,
                            end_date=end_date,
                            include_history=True)
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
        """
        if series_key is not None:
            req_url = self._build_url(series_key=series_key, start_date=start_date,
                                      end_date=end_date, detail=detail,
                                      update_after=update_after,
                                      first_n_observations=first_n_observations,
                                      last_n_observations=last_n_observations,
                                      include_history=include_history)
            response = requests.get(req_url,
                                    # headers={'Accept': 'text/csv'},
                                    timeout=90)
            # Test the response with response handler
            self.__connection_handler(response=response)
            df = pd.read_csv(io.StringIO(response.content.decode()))
            if "TIME_PERIOD" in df.columns:
                df = df.rename({"TIME_PERIOD": "Date"},
                                            axis=1).set_index("Date")
                df.index = pd.to_datetime(df.index)
            return df.sort_index(ascending=ascending)


# Test the class methods
ecb_data_info = ECB_DATA_INFO()
