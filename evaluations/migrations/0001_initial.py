
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(help_text='1-5星评分', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='评分')),
                ('comment', models.TextField(blank=True, default='', verbose_name='评价内容')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='评价时间')),
            ],
            options={
                'verbose_name': '评价',
                'verbose_name_plural': '评价',
                'db_table': 'evaluations',
                'ordering': ['-created_at'],
            },
        ),
    ]
