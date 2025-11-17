from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def migrate_created_by_to_user(apps, schema_editor):
    """Convert string usernames to User foreign keys"""
    StatusUpdate = apps.get_model('status', 'StatusUpdate')
    User = apps.get_model('auth', 'User')

    for update in StatusUpdate.objects.all():
        if update.created_by:
            # Try to find user by username
            try:
                user = User.objects.get(username=update.created_by)
                # Store user ID temporarily in a separate field we'll create
                update.temp_user_id = user.id
                update.save(update_fields=['temp_user_id'])
            except User.DoesNotExist:
                # If user doesn't exist, leave it null
                pass


def reverse_migration(apps, schema_editor):
    """Convert User foreign keys back to string usernames"""
    StatusUpdate = apps.get_model('status', 'StatusUpdate')
    User = apps.get_model('auth', 'User')

    for update in StatusUpdate.objects.all():
        if update.created_by_id:
            try:
                user = User.objects.get(id=update.created_by_id)
                update.created_by = user.username
                update.save(update_fields=['created_by'])
            except User.DoesNotExist:
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add temporary field to store user IDs
        migrations.AddField(
            model_name='statusupdate',
            name='temp_user_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        # Migrate data from string to temp field
        migrations.RunPython(migrate_created_by_to_user, reverse_migration),
        # Remove old string field
        migrations.RemoveField(
            model_name='statusupdate',
            name='created_by',
        ),
        # Add new ForeignKey field
        migrations.AddField(
            model_name='statusupdate',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Copy data from temp field to new ForeignKey field
        migrations.RunSQL(
            "UPDATE status_statusupdate SET created_by_id = temp_user_id WHERE temp_user_id IS NOT NULL",
            reverse_sql="UPDATE status_statusupdate SET temp_user_id = created_by_id WHERE created_by_id IS NOT NULL",
        ),
        # Remove temporary field
        migrations.RemoveField(
            model_name='statusupdate',
            name='temp_user_id',
        ),
    ]
