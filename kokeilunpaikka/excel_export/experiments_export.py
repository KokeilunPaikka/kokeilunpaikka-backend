import logging

from .export_template import ExperimentWorkbookTemplate, ExperimentWorksheetTemplate
from kokeilunpaikka.stages.models import Question
from django.db.models import Q

logger = logging.getLogger(__name__)


class ExperimentChallengeReport(ExperimentWorkbookTemplate):
    def __init__(self, experiment_challenge, constant_memory=True):
        self.experiment_challenge = experiment_challenge
        super(ExperimentChallengeReport, self).__init__(experiment_challenge)

    def create(self):
        super().create()
        self.add_experiments_tab()
        return self.xlsx.generate()

    def add_experiments_tab(self):
        headers = [
            "Experiment id",
            "Experiment status",
            "Experiment name",
            "Experiment description"
        ]
        questions = Question.objects.filter(
            Q(
                questionanswer__experiment__in=self.experiment_challenge.experiment_set.all()
            ) | Q(
                experiment_challenge=self.experiment_challenge
            )
        ).order_by('id').distinct()
        for q in questions:
            headers.append(q.translations.first().question)
        headers += [
            "Experiment owner",
            "Organizer",
            "Responsible user name",
            "Responsible user email",
            "Responsible user description",
            "Responsible user facebook",
            "Responsible user twitter",
            "Responsible user instagram",
            "Responsible user linkedin"
        ]

        worksheet_dict = self.xlsx.add_worksheet(
            "Experiment Challenge", ExperimentWorksheetTemplate)
        self.xlsx.set_worksheet_settings(worksheet_dict, len(headers))

        self.xlsx.add_batch_horizontally(worksheet_dict,
                                         start_position=(0, 0),
                                         cells=headers,
                                         cell_format=self.styles[self.TITLE])
        x = 0

        for experiment in self.experiment_challenge \
                              .experiment_set.all() \
                              .order_by('name') \
                              .distinct():
            x += 1
            fields = [
                (experiment.id, self.styles[self.CELL]),
                ('Published' if experiment.is_published else 'Draft', self.styles[self.CELL]),
                (experiment.name, self.styles[self.CELL]),
                (experiment.description, self.styles[self.CELL]),
            ]
            for q in questions:
                answers = experiment.questionanswer_set.filter(question=q)
                if answers.count():
                    answer = answers.first()
                    fields += (answer.value, self.styles[self.CELL]),
                else:
                    fields += ('', self.styles[self.CELL]),
            fields += [
                (experiment.created_by.get_full_name() if experiment.created_by else '',
                    self.styles[self.CELL]),
                (experiment.organizer, self.styles[self.CELL]),
                (', '.join([
                    res_user.get_full_name() for res_user in experiment.responsible_users.all()
                ]), self.styles[self.CELL]),
                (', '.join([
                    res_user.email for res_user in experiment.responsible_users.all()
                ]), self.styles[self.CELL]),
                (', '.join([
                    res_user.profile.description
                    for res_user in experiment.responsible_users.all()
                    if hasattr(res_user, 'profile') and res_user.profile.description
                ]), self.styles[self.CELL]),
                (', '.join([
                    res_user.profile.facebook_url
                    for res_user in experiment.responsible_users.all()
                    if hasattr(res_user, 'profile') and res_user.profile.facebook_url
                ]), self.styles[self.CELL]),
                (', '.join([
                    res_user.profile.twitter_url
                    for res_user in experiment.responsible_users.all()
                    if hasattr(res_user, 'profile') and res_user.profile.twitter_url
                ]), self.styles[self.CELL]),
                (', '.join([
                    res_user.profile.instagram_url
                    for res_user in experiment.responsible_users.all()
                    if hasattr(res_user, 'profile') and res_user.profile.instagram_url
                ]), self.styles[self.CELL]),
                (', '.join([
                    res_user.profile.linkedin_url
                    for res_user in experiment.responsible_users.all()
                    if hasattr(res_user, 'profile') and res_user.profile.linkedin_url
                ]), self.styles[self.CELL])
            ]
            for y, field in enumerate(fields):
                self.xlsx.add_cell(worksheet_dict, content=field[0], position=(x, y),
                                   cell_format=field[1])

        worksheet_dict['worksheet'].autofilter(0, 0, 0, len(headers))
        worksheet_dict['worksheet'].freeze_panes(1, 0)


class UserDetailsReport(ExperimentWorkbookTemplate):
    def __init__(self, users, constant_memory=True):
        self.users = users
        super(UserDetailsReport, self).__init__(users)

    def create(self):
        super().create()
        self.add_details_tab()
        return self.xlsx.generate()

    def add_details_tab(self):
        headers = [
            "User name",
            "User email"
        ]
        worksheet_dict = self.xlsx.add_worksheet(
            "User details", ExperimentWorksheetTemplate)
        self.xlsx.set_worksheet_settings(worksheet_dict, len(headers))

        self.xlsx.add_batch_horizontally(worksheet_dict,
                                         start_position=(0, 0),
                                         cells=headers,
                                         cell_format=self.styles[self.TITLE])

        x = 0
        for user in self.users:
            x += 1
            fields = [
                (user.get_full_name(), self.styles[self.CELL]),
                (user.email, self.styles[self.CELL]),
            ]
            for y, field in enumerate(fields):
                self.xlsx.add_cell(worksheet_dict, content=field[0], position=(x, y),
                                   cell_format=field[1])

        worksheet_dict['worksheet'].autofilter(0, 0, 0, len(headers))
        worksheet_dict['worksheet'].freeze_panes(1, 0)
