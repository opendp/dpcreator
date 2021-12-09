from django.http import FileResponse

from rest_framework import permissions, viewsets, renderers, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from opendp_apps.utils.view_helper import get_json_error, get_json_success
from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis.validate_release_util import ValidateReleaseUtil
from opendp_apps.analysis.serializers import \
    (AnalysisPlanObjectIdSerializer,
     AnalysisPlanSerializer,
     ReleaseInfoFileDownloadSerializer,
     ReleaseInfoSerializer,
     ReleaseValidationSerializer)


class PassthroughRenderer(renderers.BaseRenderer):
    """
        Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class ReleaseFileDownloadView(viewsets.ReadOnlyModelViewSet):
    """
    Download **PUBLIC** JSON and PDF Release Files
    - View ONLY used for PUBLIC files
    """
    serializer_class = ReleaseInfoFileDownloadSerializer
    queryset = ReleaseInfo.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

    @action(detail=True, methods=['GET'], url_path='pdf')
    def pdf(self, request, pk=None):
        """
        Download the PDF release file using the ReleaseInfo object_id
        Note: URL linked to code in opendp_apps/analysis/models.py ->  download_pdf_url()
        Example: http://127.0.0.1:8000/api/release-download/18bc23da-cdbf-420e-a6aa-3d9ecdb10c20/pdf/
        """
        release_info = get_object_or_404(ReleaseInfo, object_id=pk)

        if not release_info.dp_release_pdf_file:
            user_msg = 'The Release does not include a PDF file.'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # get an open file handle
        try:
            file_handle = release_info.dp_release_pdf_file.open()
        except ValueError as err_obj:
            user_msg = f'Not able to read the PDF Release file. (1) ({err_obj})'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as err_obj:
            user_msg = f'Not able to read the PDF Release file. (2) ({err_obj})'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # send file
        response = FileResponse(file_handle, content_type='application/pdf')
        response['Content-Length'] = release_info.dp_release_pdf_file.size
        download_fname = f'release_{release_info.object_id}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{download_fname}"'

        return response

    @action(detail=True, methods=['GET'], url_path='json')
    def json(self, request, pk=None):
        """
        Alternative to the simple "GET" url
        Download the JSON release file using the ReleaseInfo object_id
        Note: URL linked to code in opendp_apps/analysis/models.py ->  download_json_url()
        Example: http://127.0.0.1:8000/api/release-download/18bc23da-cdbf-420e-a6aa-3d9ecdb10c20/json/
        """
        return self.retrieve(request, pk)

    def retrieve(self, request, pk=None, **kwargs):
        """
        Download the JSON release file using the ReleaseInfo object_id
        Example: http://127.0.0.1:8000/api/release-download/18bc23da-cdbf-420e-a6aa-3d9ecdb10c20/
        """
        release_info = get_object_or_404(ReleaseInfo, object_id=pk)

        if not release_info.dp_release_json_file:
            user_msg = 'The Release does not include a JSON file.'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # get an open file handle
        try:
            file_handle = release_info.dp_release_json_file.open()
        except ValueError as err_obj:
            user_msg = f'Not able to read the JSON Release file. (1) ({err_obj})'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as err_obj:
            user_msg = f'Not able to read the JSON Release file. (2) ({err_obj})'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)
            
        # send file
        response = FileResponse(file_handle, content_type='application/json')
        response['Content-Length'] = release_info.dp_release_json_file.size
        download_fname = f'release_{release_info.object_id}.json'
        response['Content-Disposition'] = f'attachment; filename="{download_fname}"'

        return response


class ReleaseView(viewsets.ViewSet):

    analysis_plan = AnalysisPlanSerializer()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']    # 'patch']

    def get_queryset(self):
        """
        AnalysisPlans for the currently authenticated user.
        """
        return AnalysisPlan.objects.filter(analyst=self.request.user)

    def retrieve(self, request, pk=None):
        release_info = get_object_or_404(ReleaseInfo, object_id=pk)
        serializer = ReleaseValidationSerializer(release_info, context={'request': request})
        return Response(data=serializer)

    def create(self, request, *args, **kwargs):
        """
        Override create to create a release based on a saved/pre-validated AnalysisPlan.dp_statistics

        endpoint: /api/release/

        Example POST input: `{"analysis_plan_id": "616b5167-4ce8-4def-85dc-6f0d8de2316c"}`

       -- Example outputs --

        (1) Overall error
            Status code: 400
                {
                    "success": false,
                    "message": "The statistic 'EyeHeight' had error xyz!"
                }

        (2) Release success
            Status code: 201
            {
                    "success": true,
                    "message": "release worked!",
                    "data":
                       (see: opendp_apps.release_info_formatter.get_release_data())

        """
        # Get the AnalysisPlan object_id
        #   - Bit redundant in the serializer re: retrieving plan but only using object_id--but okay!
        #     - e.g. Passing along the object_id only will lead to later running chain
        #       in a separate process and responding by websocket/lambda, etc.
        #
        serializer = AnalysisPlanObjectIdSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            if 'object_id' in serializer.errors:
                user_msg = '"object_id" error: %s' % (serializer.errors['object_id'][0])
            else:
                user_msg = 'Not a valid AnalysisPlan "object_id"'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # We have a good object_id!
        #
        analysis_plan_id = serializer.get_object_id()

        # For longer releases, Async this!!
        # Async: the validate_util process!
        validate_util = ValidateReleaseUtil.compute_mode(request.user,
                                                         analysis_plan_id,
                                                         run_dataverse_deposit=True)
        if validate_util.has_error():
            # This is a big error, check for it before evaluating individual statistics
            #
            user_msg = validate_util.get_err_msg()
            print('release_view.create(...) user_msg', user_msg)

            # Can you return a 400 / raise an Exception here with the error message?
            # How should this be used?
            return Response(get_json_error(user_msg), status=status.HTTP_400_BAD_REQUEST)

        # It worked! Return the release!
        release_info_obj = validate_util.get_new_release_info_object()
        serializer = ReleaseInfoSerializer(release_info_obj, context={'request': request})
        return Response(data=serializer.data,
                        status=status.HTTP_201_CREATED)
