# Generated by Django 5.1.1 on 2024-09-07 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_move'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='currnt_move',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
    ]
