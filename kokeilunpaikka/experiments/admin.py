from django.contrib import admin

from parler.admin import TranslatableAdmin

from .models import (
    Experiment,
    ExperimentChallenge,
    ExperimentChallengeMembership,
    ExperimentChallengeTimelineEntry,
    ExperimentLookingForOption,
    ExperimentPost,
    ExperimentPostComment
)


class ExperimentChallengeMembershipInlineAdmin(admin.TabularInline):
    model = ExperimentChallengeMembership
    extra = 0


class ExperimentPostInlineAdmin(admin.StackedInline):
    model = ExperimentPost
    extra = 0
    fields = (
        'title',
        'content',
        'created_by',
        'images',
    )


class ExperimentChallengeTimelineEntryInlineAdmin(admin.TabularInline):
    model = ExperimentChallengeTimelineEntry
    extra = 0


@admin.register(ExperimentChallenge)
class ExperimentChallengeAdmin(TranslatableAdmin):
    fields = (
        'name',
        'slug',
        'starts_at',
        'ends_at',
        'lead_text',
        'description',
        'image',
        'themes',
        'is_visible',
        'created_at',
        'updated_at',
    )
    filter_horizontal = (
        'themes',
    )
    inlines = (
        ExperimentChallengeMembershipInlineAdmin,
        ExperimentChallengeTimelineEntryInlineAdmin,
    )
    list_display = (
        'id',
        'name',
        'starts_at',
        'ends_at',
        'is_visible',
    )
    list_display_links = (
        'id',
        'name',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )

    def get_prepopulated_fields(self, request, obj=None):
        # Can't use `prepopulated_fields` because it breaks the admin
        # validation for translated fields.
        #
        # This is the official django-parler workaround.
        return {
            'slug': ('name',)
        }


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'slug',
        'organizer',
        'description',
        'stage',
        'image',
        'created_by',
        'is_published',
        'responsible_users',
        'looking_for',
        'themes',
        'success_rating',
        'created_at',
        'published_at',
        'updated_at',
    )
    filter_horizontal = (
        'looking_for',
        'experiment_challenges',
        'themes',
        'responsible_users',
    )
    inlines = (
        ExperimentChallengeMembershipInlineAdmin,
        ExperimentPostInlineAdmin,
    )
    list_display = (
        'id',
        'name',
        'stage',
        'created_at',
        'is_published',
    )
    list_display_links = (
        'id',
        'name',
    )
    readonly_fields = (
        'created_at',
        'published_at',
        'updated_at',
    )

    def get_prepopulated_fields(self, request, obj=None):
        # Can't use `prepopulated_fields` because it breaks the admin
        # validation for translated fields.
        #
        # This is the official django-parler workaround.
        return {
            'slug': ('name',)
        }


class ExperimentPostCommentInlineAdmin(admin.TabularInline):
    extra = 0
    fields = (
        'content',
        'created_by',
        'created_at',
    )
    model = ExperimentPostComment
    readonly_fields = (
        'created_at',
    )


@admin.register(ExperimentPost)
class ExperimentPostAdmin(admin.ModelAdmin):
    fields = (
        'title',
        'content',
        'experiment',
        'created_by',
        'images',
        'created_at',
        'updated_at',
    )
    inlines = (
        ExperimentPostCommentInlineAdmin,
    )
    list_display = (
        'id',
        'title',
        'experiment',
        'created_at',
        'count_of_comments',
    )
    list_display_links = (
        'id',
        'title',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )


@admin.register(ExperimentLookingForOption)
class ExperimentLookingForOptionAdmin(TranslatableAdmin):
    fields = (
        'value',
    )
    list_display = (
        'id',
        'value',
    )
    list_display_links = (
        'id',
        'value',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
    )
