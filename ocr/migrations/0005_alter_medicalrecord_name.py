# Generated by Django 4.2.3 on 2023-07-26 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocr', '0004_medicalrecord_task_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicalrecord',
            name='name',
            field=models.CharField(default='Unnamed', max_length=100),
        ),
    ]