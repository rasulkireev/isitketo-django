# Generated by Django 5.1.1 on 2024-09-22 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='compressed_ai_generated_image',
            field=models.ImageField(blank=True, upload_to='compressed_ai_product_image/'),
        ),
        migrations.AddField(
            model_name='product',
            name='compressed_image',
            field=models.ImageField(blank=True, upload_to='compressed_product_image/'),
        ),
    ]
