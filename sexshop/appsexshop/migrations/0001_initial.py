# Generated by Django 5.0.7 on 2025-04-07 00:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='categoria',
            fields=[
                ('IdCategoria', models.AutoField(primary_key=True, serialize=False)),
                ('NombreCategoria', models.CharField(max_length=80)),
            ],
            options={
                'db_table': 'categoria',
            },
        ),
        migrations.CreateModel(
            name='roles',
            fields=[
                ('IdRol', models.AutoField(primary_key=True, serialize=False)),
                ('TipoRol', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'roles',
            },
        ),
        migrations.CreateModel(
            name='domiciliario',
            fields=[
                ('IdDomiciliario', models.AutoField(primary_key=True, serialize=False)),
                ('TipoDocumento', models.CharField(max_length=45)),
                ('Documento', models.IntegerField(unique=True)),
                ('NombreDomiciliario', models.CharField(max_length=100)),
                ('PrimerApellido', models.CharField(max_length=45)),
                ('SegundoApellido', models.CharField(blank=True, max_length=45, null=True)),
                ('Celular', models.BigIntegerField()),
                ('Ciudad', models.CharField(blank=True, max_length=45, null=True)),
                ('Correo', models.EmailField(max_length=255, unique=True)),
                ('Contraseña', models.CharField(max_length=256)),
                ('IdRol', models.ForeignKey(blank=True, db_column='IdRol', null=True, on_delete=django.db.models.deletion.CASCADE, to='appsexshop.roles')),
            ],
            options={
                'db_table': 'domiciliario',
            },
        ),
        migrations.CreateModel(
            name='subcategoria',
            fields=[
                ('IdSubCategoria', models.AutoField(primary_key=True, serialize=False)),
                ('NombresubCategoria', models.CharField(max_length=45)),
                ('categoria', models.ForeignKey(db_column='IdCategoria', on_delete=django.db.models.deletion.CASCADE, to='appsexshop.categoria')),
            ],
            options={
                'db_table': 'subcategoria',
            },
        ),
        migrations.CreateModel(
            name='producto',
            fields=[
                ('IdProducto', models.AutoField(primary_key=True, serialize=False)),
                ('Img', models.ImageField(upload_to='productos/')),
                ('Nombre', models.CharField(max_length=100)),
                ('Descripcion', models.CharField(max_length=255)),
                ('Cantidad', models.IntegerField()),
                ('Precio', models.FloatField()),
                ('FechaVence', models.DateField()),
                ('IdSubCategoria', models.ForeignKey(db_column='IdSubCategoria', on_delete=django.db.models.deletion.CASCADE, to='appsexshop.subcategoria')),
            ],
            options={
                'db_table': 'productos',
            },
        ),
        migrations.CreateModel(
            name='usuario',
            fields=[
                ('IdUsuario', models.AutoField(primary_key=True, serialize=False)),
                ('PrimerNombre', models.CharField(max_length=255)),
                ('OtrosNombres', models.CharField(max_length=255)),
                ('PrimerApellido', models.CharField(max_length=255)),
                ('SegundoApellido', models.CharField(max_length=255)),
                ('Correo', models.EmailField(max_length=255, unique=True)),
                ('NombreUsuario', models.CharField(max_length=45)),
                ('Contraseña', models.CharField(max_length=128)),
                ('imagen_perfil', models.ImageField(blank=True, null=True, upload_to='profile_images/')),
                ('idRol', models.ForeignKey(db_column='IdRol', on_delete=django.db.models.deletion.CASCADE, to='appsexshop.roles')),
            ],
            options={
                'db_table': 'usuario',
            },
        ),
    ]
