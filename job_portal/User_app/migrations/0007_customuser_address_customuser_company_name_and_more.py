# Generated by Django 5.1.1 on 2024-09-06 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User_app', '0006_remove_customuser_repassword_customuser_isemployeer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='address',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='company_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone_no',
            field=models.IntegerField(null=True),
        ),
    ]
