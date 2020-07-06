from django.contrib import admin

from parler.admin import TranslatableAdmin

from .models import Question, QuestionAnswer, Stage


@admin.register(Question)
class QuestionAdmin(TranslatableAdmin):
    fields = (
        'question',
        'description',
        'stage',
        'experiment_challenge',
        'ignore_in_experiment_challenge',
        'is_public',
        'created_at',
        'updated_at',
    )
    filter_horizontal = (
        'ignore_in_experiment_challenge',
    )
    list_display = (
        'id',
        'question',
        'stage',
        'experiment_challenge',
        'is_public',
    )
    list_display_links = (
        'id',
        'question',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    fields = (
        'question',
        'experiment',
        'value',
        'answered_by',
        'created_at',
        'updated_at',
    )
    list_display = (
        'id',
        'question',
        'experiment',
    )
    list_display_links = (
        'id',
        'question',
    )
    readonly_fields = (
        'answered_by',
        'created_at',
        'updated_at',
    )


@admin.register(Stage)
class StageAdmin(TranslatableAdmin):
    fields = (
        'stage_number',
        'name',
        'description',
        'created_at',
        'updated_at',
    )
    list_display = (
        'stage_number',
        'name',
    )
    list_display_links = (
        'stage_number',
        'name',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    def get_readonly_fields(self, request, obj=None):
        """Disable the edit of the `stage_number` field.

        The field is a primary key and thus any modifications to the field
        would create a new instance instead. We want to prevent this for the
        sake of clarity.
        """
        if obj is not None:
            return self.readonly_fields + ('stage_number',)
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False
