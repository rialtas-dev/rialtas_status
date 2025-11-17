# Generated migration to rename problem field to comments

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0002_migrate_created_by_to_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statusupdate',
            old_name='problem',
            new_name='comments',
        ),
    ]
