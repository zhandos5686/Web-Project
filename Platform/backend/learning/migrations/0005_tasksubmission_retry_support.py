from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0004_tasksubmission_reviewed_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasksubmission',
            name='passed',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='tasksubmission',
            unique_together=set(),
        ),
    ]
