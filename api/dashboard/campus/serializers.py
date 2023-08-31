from datetime import timedelta

from django.db.models import Case, F, IntegerField, Sum, Value, When
from rest_framework import serializers

from db.organization import UserOrganizationLink
from db.task import KarmaActivityLog, Level, TotalKarma, UserLvlLink
from utils.types import OrganizationType
from utils.utils import DateTimeUtils


class CampusDetailsSerializer(serializers.ModelSerializer):
    college_name = serializers.ReadOnlyField(source="org.title")
    campus_code = serializers.ReadOnlyField(source="org.code")
    campus_zone = serializers.ReadOnlyField(source="org.district.zone.name")
    campus_lead = serializers.ReadOnlyField(source="user.fullname")
    total_karma = serializers.SerializerMethodField()
    total_members = serializers.SerializerMethodField()
    active_members = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    class Meta:
        model = UserOrganizationLink
        fields = [
            "college_name",
            "campus_lead",
            "campus_code",
            "campus_zone",
            "total_karma",
            "total_members",
            "active_members",
            "rank",
        ]

    def get_total_members(self, obj):
        return obj.org.user_organization_link_org_id.count()

    def get_active_members(self, obj):
        last_month = DateTimeUtils.get_current_utc_time() - timedelta(days=30)
        return obj.org.user_organization_link_org_id.filter(
            verified=True,
            user__active=True,
            user__total_karma_user__isnull=False,
            user__total_karma_user__created_at__gte=last_month,
        ).count()

    def get_total_karma(self, obj):
        karma = obj.org.user_organization_link_org_id.filter(
            org__org_type=OrganizationType.COLLEGE.value,
            verified=True,
            user__total_karma_user__isnull=False,
        ).aggregate(total_karma=Sum("user__total_karma_user__karma"))
        return karma["total_karma"] or 0

    def get_rank(self, obj):
        rank = (
            UserOrganizationLink.objects.filter(
                org__org_type=OrganizationType.COLLEGE.value,
                verified=True,
                user__total_karma_user__isnull=False,
            )
            .values("org")
            .annotate(total_karma=Sum("user__total_karma_user__karma"))
            .order_by("-total_karma")
        )

        college_ranks = {college["org"]: i + 1 for i, college in enumerate(rank)}
        college_id = obj.org.id
        return college_ranks.get(college_id)


class CampusStudentInEachLevelSerializer(serializers.ModelSerializer):
    level = serializers.ReadOnlyField(source="level_order")
    students = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = ["level", "students"]

    def get_students(self, obj):
        user_org = self.context.get("user_org")
        user_level_link = UserLvlLink.objects.filter(
            level__level_order=obj.level_order,
            user__user_organization_link_user_id__org__title=user_org,
        ).all()
        return len(user_level_link)


class CampusStudentDetailsSerializer(serializers.ModelSerializer):
    fullname = serializers.ReadOnlyField(source="user.fullname")
    muid = serializers.ReadOnlyField(source="user.mu_id")
    karma = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = TotalKarma
        fields = ("fullname", "karma", "muid", "rank", "level", "created_at")

    def get_karma(self, obj):
        return obj.user.total_karma_user.karma or 0

    def get_rank(self, obj):
        rank = (
            TotalKarma.objects.filter(user__total_karma_user__isnull=False)
            .annotate(rank=F("user__total_karma_user__karma"))
            .order_by("-rank")
            .values_list("rank", flat=True)
        )

        ranks = {karma: i + 1 for i, karma in enumerate(rank)}
        return ranks.get(obj.user.total_karma_user.karma, None)

    def get_level(self, obj):
        if user_level_link := UserLvlLink.objects.filter(user=obj.user).first():
            return user_level_link.level.name
        return None


class WeeklyKarmaSerializer(serializers.ModelSerializer):
    college_name = serializers.ReadOnlyField(source="org.title")

    class Meta:
        model = UserOrganizationLink
        fields = ["college_name"]

    def to_representation(self, instance):
        response = super().to_representation(instance)

        today = DateTimeUtils.get_current_utc_time().date()
        date_range = [today - timedelta(days=i) for i in range(7)]

        karma_logs = (
            KarmaActivityLog.objects.filter(
                user__user_organization_link_user_id__org=instance.org,
                created_at__date__in=date_range,
            )
            .annotate(
                date_index=Case(
                    *[
                        When(created_at__date=date, then=Value(i))
                        for i, date in enumerate(date_range)
                    ],
                    output_field=IntegerField(),
                )
            )
            .values("date_index")
            .annotate(total_karma=Sum("karma"))
            .values_list("total_karma", flat=True)
        ) or []
        karma_data = {
            i + 1: karma_logs[i] if i < len(karma_logs) else 0
            for i in range(len(date_range))
        }
        response["karma"] = karma_data

        return response
