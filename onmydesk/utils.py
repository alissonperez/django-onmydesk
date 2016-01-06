"""Module with common utilities to this package"""


def my_import(class_name):
    """
    Usage example::

        Report = my_import('myclass.models.Report')

        model_instance = Report()
        model_instance.name = 'Test'
        model_instance.save()

    :param str class_name: Class name
    :returns: Class object
    """

    *packs, class_name = class_name.split('.')
    mod = __import__('.'.join(packs), fromlist=[class_name])
    klass = getattr(mod, class_name)
    return klass
