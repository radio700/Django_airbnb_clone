# Generated by Django 3.2.7 on 2021-12-14 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0008_alter_room_room_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='file',
            field=models.ImageField(upload_to='room_photos'),
        ),
    ]