from django.contrib.auth.decorators import user_passes_test, login_required

#@staff_required
def staff_required(view_func):
    @login_required
    @user_passes_test(lambda user: user.is_staff)
    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapped_view

#@superuser_required
def superuser_required(view_func):
    @login_required
    @user_passes_test(lambda user: user.is_superuser)
    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapped_view