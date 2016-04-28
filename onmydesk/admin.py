import copy

from django.contrib import admin
from django import forms
from django.conf import settings

from onmydesk import models, utils


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


def reports_available():
    report_class_list = getattr(settings, 'ONMYDESK_REPORT_LIST', [])

    report_list = []

    for class_path in report_class_list:
        klass = utils.my_import(class_path)
        report_list.append(
            (class_path, klass.name)
        )

    return report_list


class BaseReportAdminForm(forms.ModelForm):
    report = forms.fields.ChoiceField(choices=[('', '')] + reports_available(), initial='')

    class Meta:
        model = models.Report
        exclude = []

    def save(self, commit=True, *args, **kwargs):
        instance = super().save(commit, *args, **kwargs)

        if not instance.results:
            data = copy.deepcopy(self.cleaned_data)
            if 'report' in data:
                del data['report']

            instance.process(report_params=data)
            if commit:
                instance.save()

        return instance


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

    form = BaseReportAdminForm

    model = models.Report
    ordering = ('-insert_date',)
    list_display = ('id', 'report_name', 'insert_date', 'update_date', 'status')
    list_display_links = ('id', 'report_name',)
    list_filter = ('report', 'status')
    search_fields = ('report', 'status')

    readonly_fields = ['results', 'status', 'insert_date', 'update_date', 'created_by', results]

    def save_model(self, request, obj, form, change):
        if request.user:
            obj.created_by = request.user

        return super().save_model(request, obj, form, change)

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
                'fields': ('report', 'status')
            }),
            ('Results', {
                'fields': (results,)
            }),
            ('Lifecycle', {
                'fields': ('insert_date', 'update_date', 'created_by')
            }),
        ]

        form = _get_report_form(_get_report_class_name(request))

        if form:
            fieldset.insert(1, ('Filters', {
                'fields': form.base_fields.keys()
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

admin.site.register(models.Report, ReportAdmin)
