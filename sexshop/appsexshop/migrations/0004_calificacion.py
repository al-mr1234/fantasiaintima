# Generated by Django 5.0.7 on 2025-05-15 05:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsexshop', '0003_carritocompras'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calificacion',
            fields=[
                ('IdCalificacion', models.AutoField(primary_key=True, serialize=False)),
                ('Calificacion', models.IntegerField()),
                ('IdProducto', models.ForeignKey(db_column='IdProducto', on_delete=django.db.models.deletion.CASCADE, to='appsexshop.producto')),
            ],
            options={
                'db_table': 'calificacion',
            },
        ),
    ]
