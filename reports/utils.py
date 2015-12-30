

def my_import(class_name):
    *packs, class_name = class_name.split('.')
    mod = __import__('.'.join(packs), fromlist=[class_name])
    klass = getattr(mod, class_name)
    return klass
