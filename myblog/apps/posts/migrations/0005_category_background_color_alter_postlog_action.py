# Generated by Django 5.0.6 on 2024-09-07 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_alter_post_slug_alter_postlog_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='background_color',
            field=models.CharField(default='#000', max_length=7),
        ),
    ]
