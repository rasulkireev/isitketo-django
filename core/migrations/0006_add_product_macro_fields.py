# Generated manually to add macro fields to Product model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_generatedkeywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='serving_description',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='calories',
            field=models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='protein',
            field=models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='fat',
            field=models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='carbohydrates',
            field=models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='fiber',
            field=models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='sugar',
            field=models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='saturated_fat',
            field=models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='sodium',
            field=models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True),
        ),
    ]