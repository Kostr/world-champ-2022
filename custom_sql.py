from django.db import connection

def my_custom_sql(self):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM django_migrations WHERE app = socialaccount")
        cursor.execute("DELETE FROM django_migrations WHERE app = sites")
    return
