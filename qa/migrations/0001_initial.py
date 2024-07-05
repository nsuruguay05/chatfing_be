# Generated by Django 5.0.6 on 2024-07-03 19:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('generative_model', models.CharField(choices=[('claude-3-haiku-20240307', 'CLAUDE_3_HAIKU')], default='claude-3-haiku-20240307', max_length=50)),
                ('method', models.CharField(choices=[('naive_rag', 'NAIVE_RAG'), ('derivation', 'DERIVATION'), ('long_context', 'LONG_CONTEXT')], default='naive_rag', max_length=20)),
                ('like', models.BooleanField(default=None, null=True)),
                ('comment', models.TextField(null=True)),
                ('evaluation_author', models.TextField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('references', models.ManyToManyField(db_table='answer_reference', to='documents.chunk')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qa.question')),
            ],
        ),
    ]
