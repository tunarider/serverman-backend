# Generated by Django 2.2 on 2019-09-04 04:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=20)),
                ('comment', models.CharField(blank=True, max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host_name', models.CharField(db_index=True, max_length=64)),
                ('os', models.CharField(blank=True, db_index=True, max_length=64)),
                ('cpu', models.CharField(blank=True, max_length=64)),
                ('memory', models.CharField(blank=True, max_length=64)),
                ('disk', models.CharField(blank=True, max_length=64)),
                ('network', models.CharField(blank=True, max_length=64)),
                ('state', models.CharField(choices=[('ST', 'stopped'), ('RN', 'running'), ('FA', 'fault')], db_index=True, default='ST', max_length=2)),
                ('comment', models.CharField(blank=True, max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='BareMetal',
            fields=[
                ('server_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='serverman_api.Server')),
                ('is_hypervisor', models.BooleanField()),
                ('serial', models.CharField(blank=True, max_length=64)),
                ('model', models.CharField(blank=True, max_length=64)),
            ],
            bases=('serverman_api.server',),
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cidr', models.CharField(db_index=True, max_length=18)),
                ('gateway', models.CharField(blank=True, max_length=15)),
                ('comment', models.CharField(blank=True, max_length=1024)),
                ('environment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='serverman_api.Environment')),
            ],
        ),
        migrations.CreateModel(
            name='Ip',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(db_index=True, max_length=15)),
                ('is_vip', models.BooleanField()),
                ('comment', models.CharField(blank=True, max_length=1024)),
                ('network', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='serverman_api.Network')),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=64)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('environment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='serverman_api.Environment')),
                ('ips', models.ManyToManyField(blank=True, to='serverman_api.Ip')),
            ],
        ),
        migrations.CreateModel(
            name='VirtualMachine',
            fields=[
                ('server_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='serverman_api.Server')),
                ('hypervisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='serverman_api.BareMetal')),
            ],
            bases=('serverman_api.server',),
        ),
    ]
