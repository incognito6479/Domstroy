# Generated by Django 3.2.2 on 2022-05-14 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_action_page_permission'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.branch')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.client')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('count', models.FloatField(default=0)),
                ('price', models.FloatField(default=0)),
                ('total', models.FloatField(default=0)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.product')),
            ],
        ),
    ]