# Generated by Django 4.2.1 on 2023-06-22 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0005_packageitem_address_packageitem_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='packageitem',
            name='image2',
            field=models.ImageField(null=True, upload_to='packageimages'),
        ),
        migrations.AddField(
            model_name='packageitem',
            name='image3',
            field=models.ImageField(null=True, upload_to='packageimages'),
        ),
        migrations.AddField(
            model_name='packageitem',
            name='image4',
            field=models.ImageField(null=True, upload_to='packageimages'),
        ),
        migrations.AlterField(
            model_name='packageitem',
            name='image',
            field=models.ImageField(null=True, upload_to='packageimages'),
        ),
    ]
