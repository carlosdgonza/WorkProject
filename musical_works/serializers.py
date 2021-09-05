from rest_framework import serializers

from musical_works.models import Work, Contributor


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        exclude = ('work', 'created_at', 'updated_at', 'id')


class WorkSerializer(serializers.ModelSerializer):
    contributors = ContributorSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Work
        exclude = ('created_at', 'updated_at', 'id')
