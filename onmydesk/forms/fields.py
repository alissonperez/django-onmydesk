from django.forms import CharField
from django.core import validators


class SchedulerDateField(CharField):
    default_validators = [validators.RegexValidator('^D[\-+][0-9]+$|^D$')]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.help_text:
            self.help_text = ('Use "D" as current date and sum or sub operations '
                              'to change the date. E.g.: "D-1" represents yesterday.')

        if not self.max_length:
            self.max_length = 5
