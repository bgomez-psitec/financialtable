from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("auth/verificar/", views.verify_2fa, name="verify_2fa"),
    path("users/", views.users, name="users"),
    path("users/new/", views.user_create, name="user_create"),
    path("users/<int:user_id>/invite/", views.user_invite, name="user_invite"),
    path("users/<int:user_id>/edit/", views.user_edit, name="user_edit"),
    path("users/<int:user_id>/delete/", views.user_delete, name="user_delete"),
    path("companies/", views.companies, name="companies"),
    path("companies/import/", views.company_import, name="company_import"),
    path("companies/export/", views.company_export_select, name="company_export_select"),
    path("companies/export/csv/", views.company_export_csv, name="company_export_csv"),
    path("companies/new/", views.company_create, name="company_create"),
    path("companies/<int:company_id>/invite/", views.company_invite, name="company_invite"),
    path("companies/<int:company_id>/edit/", views.company_edit, name="company_edit"),
    path("companies/<int:company_id>/delete/", views.company_delete, name="company_delete"),
    path("sectors/", views.sectors, name="sectors"),
    path("sectors/<int:sector_id>/delete/", views.sector_delete, name="sector_delete"),
    path("tablas/", views.reference_tables, name="reference_tables"),
    path("config/smtp/", views.smtp_config, name="smtp_config"),
    path("auth/password-reset/", views.password_reset_request, name="password_reset"),
    path("auth/password-reset/done/", views.password_reset_done, name="password_reset_done"),
    path("auth/password-reset/confirm/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("auth/password-reset/complete/", views.password_reset_complete, name="password_reset_complete"),
    path("logout/", views.logout_view, name="logout"),
]
