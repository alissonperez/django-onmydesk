import copy
from collections import OrderedDict

from django import forms
from django.conf import settings
from django.contrib import admin

from . import forms as local_forms, models, utils


def get_result_link(result):
    link_handler = getattr(settings, 'ONMYDESK_DOWNLOAD_LINK_HANDLER', None)
    if not link_handler:
        return '#'

    handler = utils.my_import(link_handler)

    return handler(result)


def results(obj):
    if not obj.results_as_list:
        return ''

    links = []

    for filepath in obj.results_as_list:
        result_link = get_result_link(filepath)

        link = '<li><a href="{url}" target="_blank">{filename}</a></li>'.format(
            url=result_link, filename=filepath)

        links.append(link)

    return '<ul>{}</ul>'.format(''.join(links))
results.allow_tags = True


def params(obj):
    params = obj.get_params()
    if not params:
        return ''

    params_list = []

    for key, value in params.items():
        str_param = '<li><strong>{}</strong>: {}</li>'.format(
            key, str(value))

        params_list.append(str_param)

    return '<ul>{}</ul>'.format(''.join(params_list))
params.allow_tags = True
params.short_description = 'Parameters'


def status(obj):
    status_classes = {
        models.Report.STATUS_PENDING: '',
        models.Report.STATUS_PROCESSING: 'onm-label-warning',
        models.Report.STATUS_PROCESSED: 'onm-label-success',
        models.Report.STATUS_ERROR: 'onm-label-error',
    }

    status_list = dict(models.Report.STATUS_CHOICES)
    return '<span class="label {}">{}</span>'.format(
        status_classes.get(obj.status, ''),
        status_list.get(obj.status, ''))
status.allow_tags = True


def reports_available():
    report_class_list = getattr(settings, 'ONMYDESK_REPORT_LIST', [])

    report_list = []

    for class_path in report_class_list:
        klass = utils.my_import(class_path)
        report_list.append(
            (class_path, klass.name))

    return report_list


class BaseReportAdminForm(forms.ModelForm):
    report = forms.fields.ChoiceField(choices=[('', '')] + reports_available(), initial='')

    class Meta:
        model = models.Report
        exclude = []


def _get_report_admin_form(request):
    '''Returns admin form to report according with the request'''

    form = _get_report_form(_get_report_class_name(request))

    if form and not issubclass(form, BaseReportAdminForm):
        form = type('ReportModelForm', (form, BaseReportAdminForm), dict())

    return form


def _get_report_form(class_name):
    '''Given a class_name, it returns the form class from report or None
    if it does't have it'''

    if not class_name:
        return None

    if class_name not in [i[0] for i in reports_available()]:
        return None

    return utils.my_import(class_name).get_form()


def _get_report_class_name(request, default=None):
    '''Given a request, it returns the report class name'''

    return request.POST.get(
        'report',
        request.GET.get('report', default))


class ReportAdmin(admin.ModelAdmin):
    class Media:
        js = ('onmydesk/js/common.js',)
        css = {
            'all': ('onmydesk/css/common.css',)
        }

    form = BaseReportAdminForm

    model = models.Report
    ordering = ('-insert_date',)
    list_display = ('id', 'report_name', 'insert_date', 'update_date', status)
    list_display_links = ('id', 'report_name',)
    list_filter = ('report', 'status')
    search_fields = ('report', 'status')

    readonly_fields = ['results', status, 'insert_date', 'update_date', 'created_by',
                       'process_time', results, params]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if request.user and not obj.created_by:
            obj.created_by = request.user

        if not obj.results:
            data = copy.deepcopy(form.cleaned_data)
            if 'report' in data:
                del data['report']

            obj.set_params(data)
            obj.save()

        return obj

    def report_name(self, obj):
        if not getattr(self, '_reports_available_cache', None):
            self._reports_available_cache = dict(reports_available())

        return self._reports_available_cache.get(obj.report, obj.report)
    report_name.allow_tags = True
    report_name.short_description = 'Name'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user:
            queryset = queryset.filter(created_by=request.user)

        return queryset

    def get_form(self, request, obj=None, **kwargs):
        self.form = _get_report_admin_form(request) or self.form
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldset = [
            ('Identification', {
                'fields': ('report', status)
            }),
            ('Results', {
                'fields': (results,)
            }),
            ('Lifecycle', {
                'fields': ('insert_date', 'update_date', 'created_by', 'process_time')
            }),
        ]

        form = _get_report_form(_get_report_class_name(request))

        if form:
            fieldset.insert(1, ('Filters', {
                'fields': form.base_fields.keys()
            }))
        else:
            fieldset.insert(1, ('Filters', {
                'fields': (params,)
            }))

        return fieldset

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        readonly_fields = list(set(readonly_fields))

        if obj and obj.pk:
            readonly_fields.append('report')
        else:
            try:
                readonly_fields.remove('report')
            except ValueError:
                pass

        return readonly_fields


def _get_scheduler_report_form(class_name):
    '''Returns report form to be used by scheduler'''

    form = _get_report_form(class_name)

    if not form:
        return None

    # Handle form fields
    override_fields = OrderedDict()
    for name, value in form.base_fields.items():
        if isinstance(value, forms.fields.DateField):
            override_fields[name] = local_forms.fields.SchedulerDateField(
                required=value.required)

    form = type('NewReportForm', (form,), override_fields)

    return form


def _get_scheduler_report_admin_form(class_name, obj):
    '''Returns form used by admin screen'''

    form = _get_scheduler_report_form(class_name)

    # Fill initial field of form params with what is in object to
    # Enable it's edition.
    if obj:
        params = obj.get_params()
        for name, field in form.base_fields.items():
            if name in params and name in params:
                field.initial = params[name]

    if form and not issubclass(form, BaseReportAdminForm):
        form = type('ParamsSchedulerAdminForm', (form, SchedulerAdminForm), dict())

    return form


class SchedulerAdminForm(forms.ModelForm):
    report = forms.fields.ChoiceField(choices=[('', '')] + reports_available(), initial='')
    notify_emails = forms.fields.CharField(help_text='Separate e-mails by ","',
                                           max_length=1000,
                                           required=False,
                                           widget=forms.Textarea)

    class Meta:
        model = models.Scheduler
        exclude = []


class SchedulerAdmin(admin.ModelAdmin):
    class Media:
        js = ('onmydesk/js/common.js',)

    form = SchedulerAdminForm
    model = models.Scheduler
    ordering = ('-insert_date',)
    list_display = ('id', 'report_name', 'periodicity', 'insert_date', 'update_date', 'created_by')
    list_display_links = ('id', 'report_name',)
    list_filter = ('report',)
    search_fields = ('report',)

    readonly_fields = ['insert_date', 'update_date', 'created_by']

    def report_name(self, obj):
        if not getattr(self, '_reports_available_cache', None):
            self._reports_available_cache = dict(reports_available())

        return self._reports_available_cache.get(obj.report, obj.report)
    report_name.short_description = 'Name'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if request.user and not obj.created_by:
            obj.created_by = request.user

        data = copy.deepcopy(form.cleaned_data)

        # Filtering fields by report form fields
        report_form_fields = _get_report_form(obj.report).base_fields.keys()
        data = {k: v for k, v in data.items() if k in report_form_fields}

        obj.set_params(data)
        obj.save()

        return obj

    def get_form(self, request, obj=None, **kwargs):
        report_class_name = _get_report_class_name(request, obj.report if obj else None)
        form = _get_scheduler_report_admin_form(report_class_name, obj)
        self.form = form or self.form
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Identification', {
                'fields': ('report', 'periodicity')
            }),
            ('Notification', {
                'fields': ('notify_emails',)
            }),
            ('Lifecycle', {
                'fields': ('insert_date', 'update_date', 'created_by')
            }),
        ]

        report_class_name = _get_report_class_name(request, obj.report if obj else None)
        form = _get_scheduler_report_form(report_class_name)

        if form:
            fieldsets.insert(1, ('Filters', {
                'fields': form.base_fields.keys()
            }))

        return fieldsets


admin.site.register(models.Scheduler, SchedulerAdmin)
admin.site.register(models.Report, ReportAdmin)
