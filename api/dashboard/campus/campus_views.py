from rest_framework.views import APIView

from db.organization import UserOrganizationLink
from db.task import Level
from utils.permission import CustomizePermission, JWTUtils, role_required
from utils.response import CustomResponse
from utils.types import OrganizationType, RoleType
from utils.utils import CommonUtils
from . import serializers


class CampusDetailsAPI(APIView):
    authentication_classes = [CustomizePermission]

    @role_required([RoleType.CAMPUS_LEAD.value, ])
    def get(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        user_org_link = UserOrganizationLink.objects.filter(user_id=user_id,
                                                            org__org_type=OrganizationType.COLLEGE.value).first()
        serializer = serializers.CampusDetailsSerializer(user_org_link, many=False)
        return CustomResponse(response=serializer.data).get_success_response()


class CampusStudentInEachLevelAPI(APIView):
    authentication_classes = [CustomizePermission]

    @role_required([RoleType.CAMPUS_LEAD.value, ])
    def get(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        user_org_link = UserOrganizationLink.objects.filter(user_id=user_id).first()
        level = Level.objects.all()
        serializer = serializers.CampusStudentInEachLevelSerializer(level, many=True,
                                                                    context={'user_org': user_org_link.org.title})
        return CustomResponse(response=serializer.data).get_success_response()


class CampusStudentDetailsAPI(APIView):
    authentication_classes = [CustomizePermission]

    @role_required([RoleType.CAMPUS_LEAD.value, ])
    def get(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        user_org_link = UserOrganizationLink.objects.filter(user_id=user_id).first()
        user_org_links = UserOrganizationLink.objects.filter(org_id=user_org_link.org_id,
                                                             org__org_type=OrganizationType.COLLEGE.value)
        paginated_queryset = CommonUtils.get_paginated_queryset(
            user_org_links, request,
            ['user__first_name',
             'user__mu_id',
             'user__total_karma_user__karma'],
            {'name': 'user__first_name',
             'muid': 'user__mu_id',
             'karma': 'user__total_karma_user__karma'})
        serializer = serializers.CampusStudentDetailsSerializer(paginated_queryset.get('queryset'), many=True).data
        return CustomResponse(response={"data": serializer, 'pagination': paginated_queryset.get(
            'pagination')}).get_success_response()


class CampusStudentDetailsCSVAPI(APIView):
    authentication_classes = [CustomizePermission]

    @role_required([RoleType.CAMPUS_LEAD.value, ])
    def get(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        user_org_link = UserOrganizationLink.objects.filter(user_id=user_id).first()

        user_org_links = UserOrganizationLink.objects.filter(org_id=user_org_link.org_id,
                                                             org__org_type=OrganizationType.COLLEGE.value)
        serializer = serializers.CampusStudentDetailsSerializer(user_org_links, many=True)
        return CommonUtils.generate_csv(serializer.data, 'Campus Details')


class WeeklyKarmaAPI(APIView):
    authentication_classes = [CustomizePermission]

    @role_required([RoleType.CAMPUS_LEAD.value])
    def get(self, request):
        user_id = JWTUtils.fetch_user_id(request)
        user_org_link = UserOrganizationLink.objects.filter(user_id=user_id,
                                                            org__org_type=OrganizationType.COLLEGE.value).first()
        serializer = serializers.WeeklyKarmaSerializer(user_org_link)
        return CustomResponse(response=serializer.data).get_success_response()
