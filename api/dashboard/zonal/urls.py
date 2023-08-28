from django.urls import path

from . import dash_zonal_views

urlpatterns = [
    path("zonal-details/", dash_zonal_views.ZonalDetailsAPI.as_view(), name='zonal-details'),
    path("top-districts/", dash_zonal_views.ZonalTopThreeDistrictAPI.as_view(), name='top-3-districts'),
    path("student-level/", dash_zonal_views.ZonalStudentLevelStatusAPI.as_view(), name='student-level-status'),
    path("student-details/", dash_zonal_views.ZonalStudentDetailsAPI.as_view()),
    path("student-details/csv/", dash_zonal_views.ZonalStudentDetailsCSVAPI.as_view()),
    path("college-list/", dash_zonal_views.ListAllDistrictsAPI.as_view(), name='list-all-colleges'),
    path("college-list/csv/", dash_zonal_views.ListAllDistrictsCSVAPI.as_view(), name='list-all-college-csv'),
]
