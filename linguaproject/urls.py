from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from accounts.api import router as accounts_router
from logical_analysis.api import router as analysis_router

api = NinjaAPI()
api.add_router("/account", accounts_router)
api.add_router("/analysis", analysis_router)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
]