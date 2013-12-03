from ocean import utils


def index(request):
    return utils.render(request, 'base/welcome.html')


def sign_in(request):
    return utils.render(request, 'base/sign_in.html')


def edit_profile(request):
    return utils.render(request, 'base/edit_profile.html')


def mission(request):
    return utils.render(request, 'base/mission.html')