from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from .models import Question, QuestionAnswer, Stage


class QuestionAnswerListSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        ret = []
        for data in validated_data:
            ret.append(self.child.update(instance, data))
        return ret


class QuestionAnswerSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(),
        source='question',
    )

    def update(self, instance, validated_data):
        answer, created = QuestionAnswer.objects.update_or_create(
            question=validated_data['question'],
            experiment=self.instance,
            defaults={
                'answered_by': self.context['request'].user,
                'value': validated_data['value']
            }
        )
        return answer

    class Meta:
        model = QuestionAnswer
        list_serializer_class = QuestionAnswerListSerializer
        fields = (
            'question_id',
            'value',
        )

    def validate(self, data):
        if (
            data['question'].experiment_challenge is not None and
            data['question'].experiment_challenge not in
            self.instance.experiment_challenges.all()
        ):
            raise serializers.ValidationError(_(
                'The question is intended for an experiment challenge this '
                'experiment is not participating.'
            ))
        return data


class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = (
            'id',
            'description',
            'experiment_challenge_id',
            'is_public',
            'question',
        )


class StageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stage
        fields = (
            'description',
            'name',
            'stage_number',
        )
