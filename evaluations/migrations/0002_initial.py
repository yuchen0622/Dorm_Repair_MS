
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('evaluations', '0001_initial'),
        ('workorders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to=settings.AUTH_USER_MODEL, verbose_name='评价学生'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='work_order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='evaluation', to='workorders.workorder', verbose_name='工单'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_evaluations', to=settings.AUTH_USER_MODEL, verbose_name='被评价维修工'),
        ),
        migrations.AddIndex(
            model_name='evaluation',
            index=models.Index(fields=['rating'], name='evaluations_rating_5e2e77_idx'),
        ),
        migrations.AddIndex(
            model_name='evaluation',
            index=models.Index(fields=['worker'], name='evaluations_worker__6b67be_idx'),
        ),
    ]
