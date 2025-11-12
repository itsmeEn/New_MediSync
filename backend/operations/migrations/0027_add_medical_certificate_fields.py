# Generated migration for medical certificate request fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0026_medicalrecordrequest_clarification_notes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalrecordrequest',
            name='purpose',
            field=models.CharField(blank=True, help_text='Purpose of the medical certificate request', max_length=200),
        ),
        migrations.AddField(
            model_name='medicalrecordrequest',
            name='requested_date_range_start',
            field=models.DateField(blank=True, help_text='Start date for the requested certificate period', null=True),
        ),
        migrations.AddField(
            model_name='medicalrecordrequest',
            name='requested_date_range_end',
            field=models.DateField(blank=True, help_text='End date for the requested certificate period', null=True),
        ),
        migrations.AddField(
            model_name='medicalrecordrequest',
            name='doctor_notes',
            field=models.TextField(blank=True, help_text='Additional notes from the doctor'),
        ),
        migrations.AddField(
            model_name='medicalrecordrequest',
            name='certificate_file',
            field=models.FileField(blank=True, help_text='Uploaded medical certificate file', null=True, upload_to='medical_certificates/'),
        ),
        migrations.AddField(
            model_name='medicalrecordrequest',
            name='rejection_reason',
            field=models.TextField(blank=True, help_text='Reason for rejection if request is rejected'),
        ),
        migrations.AddField(
            model_name='medicalrecordrequest',
            name='rejected_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rejected_record_requests', to='users.user'),
        ),
        migrations.AddField(
            model_name='medicalrecordrequest',
            name='rejected_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='medicalrecordrequest',
            name='request_reference_number',
            field=models.CharField(blank=True, help_text='Unique reference number for the request', max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='medicalrecordrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('delivered', 'Delivered'), ('completed', 'Completed')], default='pending', max_length=10),
        ),
    ]

