# Generated by Django 4.1.1 on 2023-06-24 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0009_alter_contentrecommendation_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewratingpackage',
            name='sentiment',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]