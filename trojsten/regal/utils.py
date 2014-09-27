def get_related(attribute, description="", order=None, boolean=False):
    """
    Creates a function for admin list_display, to create a column with parameter of related object.
    list_select_related = True is recommended for ModelAdmin
    """
    def f(self, obj):
        result = obj
        for attr in attribute:
            result = getattr(result, attr)
        return result() if callable(result) else result
    f.short_description = description
    f.admin_order_field = order
    f.boolean = boolean
    return f


def attribute_format(attribute, description="", order=None, boolean=False):
    """
    Creates a function to reformat column of direct attribute in admin list_display
    """
    return get_related((attribute,), description, order, boolean)
