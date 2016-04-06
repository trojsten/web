from datetime import datetime

def is_true(value):
    """Converts GET parameter value to bool
    """
    return bool(value) and value.lower() not in ('false', '0')


def default_start_time():
    return datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )


def default_end_time():
    return datetime.now().replace(
        hour=23, minute=59, second=59, microsecond=0
    )


def get_related(attribute_chain, description='', order=None, boolean=False):
    """
    Creates a member function for ModelAdmin.
    This function creates a column of table in admin list view
    when included in list_display.
    However, this can also display attributes of related models.
    list_select_related = True is recommended for ModelAdmin

    Example of getting related "task name" for "submit" model:
    get_task_name = get_related(attribute_chain=('task', 'name'),
                                description='uloha',
                                order='task__name')
    list_display = (get_task_name, )
    """
    def get_attribute_of_related_model(self, obj):
        result = obj
        for attr in attribute_chain:
            result = getattr(result, attr)
        return result() if callable(result) else result
    get_attribute_of_related_model.short_description = description
    get_attribute_of_related_model.admin_order_field = order
    get_attribute_of_related_model.boolean = boolean
    return get_attribute_of_related_model


def attribute_format(attribute, description='', order=None, boolean=False):
    """
    Creates a function for ModelAdmin
    to change format of column in admin list view.
    This function can be used only to reformat a direct attribute of model.
    """
    return get_related((attribute,), description, order, boolean)
