import requests

from utils.response import CustomResponse
from utils.permission import JWTUtils
from db.user import User

from rest_framework.views import APIView
from django.conf import settings

class WadhwaniAuthToken(APIView):
    def post(self, request):
        url = settings.WADHWANI_CLIENT_AUTH_URL

        data = {
            'grant_type': 'client_credentials',
            'client_id': 'mulearn',
            'client_secret': settings.WADHWANI_CLIENT_SECRET,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, data=data, headers=headers)
        return CustomResponse(response=response.json()).get_success_response()
    
class WadhwaniUserLogin(APIView):
    def post(self, request):
        url = settings.WADHWANI_BASE_URL + "api/v1/iamservice/oauth/login"
        user_id = JWTUtils.fetch_user_id(request)
        user = User.objects.get(id=user_id)
        token = request.headers.get('Client-Auth-Token')
        data = {
            "name": user.full_name,
            "candidateId": user.id,
            "userName": user.email,
            "email": user.email,
            "mobile": f"+91-{user.mobile}",
            "countryCode": "IN",
            "userLanguageCode": "en",
            "token": token
        }
        response = requests.post(url, data=data)
        return CustomResponse(response=response.json()).get_success_response()
    
class WadhwaniCourseDetails(APIView):
    def get(self, request):
        url = settings.WADHWANI_BASE_URL + "api/v1/courseservice/oauth/client/courses"
        token = request.headers.get('Client-Auth-Token')
        headers = {'Authorization': token}
        response = requests.get(url, headers=headers)
        return CustomResponse(response=response.json()).get_success_response()

class WadhwaniCourseEnrollStatus(APIView):
    def get(self, request):
        url = settings.WADHWANI_BASE_URL + "api/v1/courseservice/oauth/client/courses"
        token = request.headers.get('Client-Auth-Token')
        headers = {'Authorization': token}
        user_id = JWTUtils.fetch_user_id(request)
        user = User.objects.get(id=user_id)
        response = requests.get(url, params={"username": user.email}, headers=headers)
        return CustomResponse(response=response.json()).get_success_response()

class WadhwaniCourseQuizData(APIView):
    def get(self, request):
        url = settings.WADHWANI_BASE_URL + f"api/v1/courseservice/oauth/course/{course_id}/reports/quiz/student/{user.email}"
        token = request.headers.get('Client-Auth-Token')
        headers = {'Authorization': token}
        course_id = request.query_params.get('course_id')
        user_id = JWTUtils.fetch_user_id(request)
        user = User.objects.get(id=user_id)
        response = requests.get(url, headers=headers)
        return CustomResponse(response=response.json()).get_success_response()