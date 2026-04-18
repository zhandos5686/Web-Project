from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lessonslot",
            name="meeting_url",
            field=models.URLField(blank=True),
        ),
    ]
