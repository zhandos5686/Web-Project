from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0003_enrollmentrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasksubmission',
            name='feedback',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
