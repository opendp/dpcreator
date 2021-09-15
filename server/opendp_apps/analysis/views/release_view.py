from rest_framework import viewsets, status
from rest_framework.response import Response
from opendp_apps.utils.view_helper import get_json_error, get_json_success

from opendp_apps.analysis.serializers import AnalysisPlanSerializer, \
    ReleaseValidationSerializer, ComputationChainSerializer


class ReleaseView(viewsets.ViewSet):

    statistics = ReleaseValidationSerializer()
    analysis_plan = AnalysisPlanSerializer()

    http_method_names = ['get', 'post', 'patch']

    def create(self, request, *args, **kwargs):
        """
        Note: No data is saved. This endpoint is used for validation.

        endpoint: /api/release/

        Example POST input:
            {
                "analysis_plan_id": "616b5167-4ce8-4def-85dc-6f0d8de2316c",
                "dp_statistics": [
                    {
                        "statistic": "mean",
                        "variable": "EyeHeight",
                        "epsilon": 0.6,
                        "delta": 0,
                        "error": "",
                        "missing_values_handling": "insert_fixed",
                        "handle_as_fixed": false,
                        "fixed_value": "5.0",
                        "locked": false,
                        "label": "EyeHeight"
                    }
                ]
            }

        -- Example outputs --

        (1) Overall error
            Status code: 400
                {
                    "success": false,
                    "message": "The depositor setup info has an invalid epsilon value: 4.0"
                }

        (2) Single statistic error -- even if only 1 statistic submitted
            Status code: 200  - NOTE status code is 200!
            {
                "success": true,
                "message": "validation results returned",
                "data": [
                    {
                        "var_name": "BlinkDuration",
                        "statistic": "mean",
                        "valid": false,
                        "message": "As a rule of thumb, epsilon should not be less than 0.001 nor greater than 1."
                    }
                ]
            }

        (2) Single statistic success -- even if only 1 statistic submitted
            Status code: 200  - NOTE status code is 200!

            {
                "success": true,
                "message": "validation results returned",
                "data": [
                    {
                        "var_name": "EyeHeight",
                        "statistic": "mean",
                        "valid": true,
                        "message": null
                    }
                ]
            }

        (3) Mixed success and error -- even if only 1 statistic submitted
            Status code: 200  - NOTE status code is 200!
            {
                "success": true,
                "message": "validation results returned",
                "data": [
                    {
                        "var_name": "EyeHeight",
                        "statistic": "mean",
                        "valid": true,
                        "message": null
                    },
                    {
                        "var_name": "BlinkDuration",
                        "statistic": "mean",
                        "valid": false,
                        "message": "The running epsilon (1.45) exceeds the max epsilon (1.0)"
                    }
                ]
            }

        """
        #print('>> ReleaseView.create >>>', request.data)
        release_info_serializer = ReleaseValidationSerializer(data=request.data)
        if not release_info_serializer.is_valid():
            print('release_info_serializer.errors', release_info_serializer.errors)
            return Response(get_json_error('Field validation failed',
                                           errors=release_info_serializer.errors),
                            status=status.HTTP_200_OK)
                            #status=status.HTTP_400_BAD_REQUEST)


        save_result = release_info_serializer.save(**dict(opendp_user=request.user))
        #print(save_result.success)
        if not save_result.success:
            #print(save_result.message)

            return Response(get_json_error(save_result.message),
                            status=status.HTTP_400_BAD_REQUEST)

        #print(save_result.data)
        return Response(get_json_success('validation results returned',
                                         data=save_result.data),
                        status=status.HTTP_200_OK)

        #print('stats_valid', stats_valid)
        #return Response({'valid': stats_valid}, status=status.HTTP_201_CREATED)

    def update(self, request, object_id=None):
        # TODO: This maybe should be under the POST method but with a flag (validation=false actually runs the chain)
        computation_chain_serializer = ComputationChainSerializer(data=request.data)
        if not computation_chain_serializer.is_valid():
            raise Exception(f"Invalid Computation Chain request: {computation_chain_serializer.errors}")
        results = computation_chain_serializer.run_computation_chain()
        return Response({'results': results}, status=status.HTTP_201_CREATED)