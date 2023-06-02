# Generated by Django 4.2.1 on 2023-06-02 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0003_alter_packageitem_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='packageitem',
            name='description',
            field=models.TextField(blank=True, max_length=800),
        ),
    ]
