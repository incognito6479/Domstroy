from django.urls import path

from app.api.router import router
from app.api.views import GetActionApiView, GetPageApiView

urlpatterns = [
    path('action/list', GetActionApiView.as_view()),
    path('page/list', GetPageApiView.as_view()),
]

urlpatterns += router.urls

