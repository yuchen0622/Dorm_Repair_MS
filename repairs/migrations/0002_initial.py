
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('repairs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='repairrequest',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repair_requests', to=settings.AUTH_USER_MODEL, verbose_name='报修学生'),
        ),
        migrations.AddField(
            model_name='repairimage',
            name='repair_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='repairs.repairrequest', verbose_name='报修单'),
        ),
        migrations.AddIndex(
            model_name='repairrequest',
            index=models.Index(fields=['status'], name='repair_requ_status_d59ea3_idx'),
        ),
        migrations.AddIndex(
            model_name='repairrequest',
            index=models.Index(fields=['created_at'], name='repair_requ_created_54cc96_idx'),
        ),
    ]
