

status_icons = {
    'COMPLETED': 'Status_Completed_icon.png',
    'CANCELLED': 'Status_Cancelled_icon.png',
    'INPROGRESS': 'Status_In_Progress_icon.png',
    'PENDING': 'Status_Pending_icon.png',
    'UNKNOWN': 'Status_Unknown_icon.png',
    'WAITING': 'Status_Waiting_icon.png',
    'FAILED': 'Status_Failed_icon.png',
    'CAUTION': 'Status_Caution_icon.png',
}


def get_status_icon(modelobj):
    from django.templatetags.static import static
    """
    Returns a static icon based on the status choice field.
    Adjust the icon URLs or classes based on your needs.
    """
    icon_path = status_icons.get(modelobj.status, 'Status_Unknown_icon.png')
    return static(f'CatiaFramework/Status_Icons/{icon_path}')