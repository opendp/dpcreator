"""
Validate and appropriately handle Dataverse signed urls
"""
from datetime import datetime
from urllib.parse import urlparse, parse_qsl

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.model_helpers.basic_response import BasicResponse, ok_resp, err_resp


class SignedUrlHandler(BasicErrCheck):
    """Validate, save, and appropriately use the signed urls"""

    @staticmethod
    def validate_signed_url_params(signed_url: str) -> BasicResponse:
        """
        Check that the signed url contains the expected parameters
        Example signed url: "signedUrl":"http://host.docker.internal:8089/api/users/:me
            ?until=2022-08-08T11:18:28.368
            &user=dataverseAdmin
            &method=GET
            token=bad3cbfff29bb2c3f8baa168dd20c86444c3a710195b9e25915eca
                4cc41791f84c5c3be08ec6a0a5f52573fa86876714d00e807c223572e143f9
                2149525f29b2",
        @rtype: BasicResponse
        """
        parse_result = urlparse(signed_url)
        dict_result = {}
        for pkey, pval in parse_qsl(parse_result.query):
            dict_result[pkey] = pval

        print('dict_result', dict_result)
        expected_keys = ['until', 'user', 'method', 'token']
        for ekey in expected_keys:
            if ekey not in dict_result:
                user_msg = f'The key "{ekey}" was not found in the signed url.'
                return err_resp(user_msg)
            if not dict_result[ekey]:
                user_msg = f'The signed url did not have a value for key "{ekey}".'
                return err_resp(user_msg)

        # Is the method valid?
        if not dict_result['method'] in ['GET', 'POST']:
            user_msg = f'This method for this url is not a GET or POST: ' + dict_result['method']
            return err_resp(user_msg)

        # Is the date/time string valid?
        #
        date_time_str = dict_result['until']  # until=2022-08-08T11:18:28.368

        try:
            dt_obj = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%f')

            # Has the date/time expired?
            if datetime.now() > dt_obj:
                user_msg = f'This date/time for this url has expired: {date_time_str}'
                return err_resp(user_msg)

        except ValueError:
            user_msg = f'The date/time in the signed url is not valid: {date_time_str}'
            return err_resp(user_msg)

        return ok_resp('Valid signed url')

    @staticmethod
    def validate_signed_urls(signed_urls: dict) -> BasicResponse:
        """
        Check that the signed_urls data contains the correct keys and valid dates
        @rtype: object
        """
        if not signed_urls:
            return err_resp('There are no signed urls.')

        if dv_static.DV_URL_KEY_APIS not in signed_urls:
            return err_resp('The "apis" keys was not found in the signed urls data.')

        """
        Example data:
        {
           "apis":[
              {
                 "name":"userInfo",
                 "httpMethod":"GET",
                 "signedUrl":"http://host.docker.internal:8089/api/users/:me?until=2022-08-08T11:18:28.368&user=dataverseAdmin&method=GET&token=bad3cbfff29bb2c3f8baa168dd20c86444c3a710195b9e25915eca4cc41791f84c5c3be08ec6a0a5f52573fa86876714d00e807c223572e143f92149525f29b2",
                 "timeOut":10
              },
              ...
            ]
        }
        """

        # Convert the API info into a dict, with the url "name" as the key
        signed_urls_dict = {}
        for api_info in signed_urls[dv_static.DV_URL_KEY_APIS]:

            # Unexpected chunk of data.
            if dv_static.DV_URL_KEY_NAME not in api_info:
                user_msg = (f'Unknown data. Expected to find the attribute "{dv_static.DV_URL_KEY_NAME}"'
                            f' in the JSON data. JSON data: {api_info}')
                return err_resp(user_msg)

            # Update the signed_urls_dict
            signed_urls_dict[api_info[dv_static.DV_URL_KEY_NAME]] = api_info

        names_not_found = []
        for url_name in dv_static.REQUIRED_DV_URLS:
            # Is the required url type found?
            if not url_name in signed_urls_dict:
                # Nope! Continue on
                names_not_found.append(url_name)
                continue

            # Yes, name found. Validate the remaining data
            api_info = signed_urls_dict.get(url_name)

            # Is the 'timeOut' key found?
            if dv_static.DV_URL_KEY_TIMEOUT not in api_info:
                user_msg = (f'Signed url key "{dv_static.DV_URL_KEY_TIMEOUT}" not found in the JSON data.'
                            f' (Signed url name: {url_name})')
                return err_resp(user_msg)

            # Is the 'timeOut' value an integer?
            if str(api_info[dv_static.DV_URL_KEY_TIMEOUT]).isdigit() is False:
                user_msg = (f'The value for the key "{dv_static.DV_URL_KEY_TIMEOUT}" is not an integer.'
                            f' e.g. It must be an integer. (Signed url name: {url_name})')
                return err_resp(user_msg)

            # Is the 'httpMethod' key found?
            if dv_static.DV_URL_KEY_HTTP_METHOD not in api_info:
                user_msg = (f'Signed url key "{dv_static.DV_URL_KEY_HTTP_METHOD}" not found in the JSON data.'
                            f' (Signed url name: {url_name})')
                return err_resp(user_msg)

            # Is the 'httpMethod' the expected value
            expected_method = dv_static.REQUIRED_DV_URL_METHODS.get(url_name)
            if api_info[dv_static.DV_URL_KEY_HTTP_METHOD] != expected_method:
                user_msg = (f'The value for the key "{dv_static.DV_URL_KEY_HTTP_METHOD}" is not'
                            f' "{expected_method}". (Signed url name: {url_name})')
                print(f'!!!! api_info: {api_info}')
                print(f'expected_method: {expected_method}')
                print(f'url_name: {url_name}')
                return err_resp(user_msg)

            # Is the 'signedUrl' key found?
            if dv_static.DV_URL_KEY_SIGNED_URL not in api_info:
                user_msg = (f'Signed url key "{dv_static.DV_URL_KEY_SIGNED_URL}" not found in the JSON data.'
                            f' (Signed url name: {url_name})')
                return err_resp(user_msg)

            # Check the signed url parameters
            signed_url_valid = SignedUrlHandler.validate_signed_url_params( \
                api_info[dv_static.DV_URL_KEY_SIGNED_URL])
            if not signed_url_valid.success:
                user_msg = f'{signed_url_valid.message}. (Signed url name: {url_name})'
                return err_resp(user_msg)

        if names_not_found:
            expected_names = ', '.join(names_not_found)
            user_msg = (f'The data did contain the expected url name(s): {expected_names}')

            return err_resp(user_msg)

        return ok_resp('looks good')
