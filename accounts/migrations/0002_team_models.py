# Generated migration for Team models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Create through models first
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('backend', 'Backend Developer'), ('frontend', 'Frontend Developer'), ('fullstack', 'Full-Stack Developer'), ('design', 'Designer'), ('devops', 'DevOps Engineer'), ('ml', 'ML Engineer'), ('other', 'Other')], default='other', max_length=20)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['joined_at'],
            },
        ),
        migrations.CreateModel(
            name='TeamInvite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending', max_length=10)),
                ('message', models.TextField(blank=True, default='Join our team!')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        # Create Team model
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('web', 'Web Development'), ('mobile', 'Mobile App'), ('ai-ml', 'AI/ML'), ('backend', 'Backend'), ('devops', 'DevOps'), ('design', 'Design'), ('other', 'Other')], default='other', max_length=30)),
                ('status', models.CharField(choices=[('recruiting', '🔍 Recruiting'), ('full', '✓ Full'), ('closed', '✕ Closed')], default='recruiting', max_length=15)),
                ('skills_required', models.CharField(blank=True, default='', max_length=500)),
                ('members_needed', models.PositiveSmallIntegerField(default=2, help_text='Target team size')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('leader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams_led', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        # Add foreign keys to through models
        migrations.AddField(
            model_name='teammember',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_records', to='accounts.team'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_roles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='teaminvite',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invite_records', to='accounts.team'),
        ),
        migrations.AddField(
            model_name='teaminvite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_invites', to=settings.AUTH_USER_MODEL),
        ),
        # Add M2M fields to Team
        migrations.AddField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='teams_in', through='accounts.TeamMember', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='team',
            name='pending_invites',
            field=models.ManyToManyField(blank=True, related_name='team_invites', through='accounts.TeamInvite', to=settings.AUTH_USER_MODEL),
        ),
        # Add constraints
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together={('team', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='teaminvite',
            unique_together={('team', 'user')},
        ),
    ]
