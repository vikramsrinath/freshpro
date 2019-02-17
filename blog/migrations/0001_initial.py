# Generated by Django 2.0.7 on 2019-02-17 16:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_score', models.CharField(default=0, max_length=5)),
                ('finance_score', models.CharField(default=0, max_length=5)),
                ('marketing_score', models.CharField(default=0, max_length=5)),
                ('human_score', models.CharField(default=0, max_length=5)),
                ('technology_score', models.CharField(default=0, max_length=5)),
                ('total_score', models.CharField(default=0, max_length=5)),
                ('is_active', models.CharField(default=1, max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=128, unique=True)),
                ('category_desc', models.CharField(max_length=1000)),
                ('category_slug', models.CharField(max_length=200)),
                ('pid', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=0)),
                ('is_active', models.CharField(default=1, max_length=5)),
                ('picture', models.ImageField(blank=True, upload_to='category')),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=128)),
                ('is_active', models.CharField(default=1, max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_name', models.CharField(max_length=128)),
                ('iso_code', models.CharField(max_length=500)),
                ('phone_code', models.CharField(default=0, max_length=500)),
                ('is_active', models.CharField(default=1, max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry_name', models.CharField(max_length=128, unique=True)),
                ('is_active', models.CharField(default=1, max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_level', models.CharField(max_length=128)),
                ('user_comapany', models.CharField(max_length=128)),
                ('is_active', models.CharField(default=1, max_length=5)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MembershipClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.CharField(default=1, max_length=5)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Client')),
                ('membership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Membership')),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('url', models.URLField()),
                ('views', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state_name', models.CharField(max_length=128)),
                ('state_code', models.CharField(max_length=128)),
                ('is_active', models.CharField(default=1, max_length=5)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Country', to='blog.Country')),
            ],
        ),
        migrations.CreateModel(
            name='user_audit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(default=0, max_length=256)),
                ('meta_key', models.CharField(default=0, max_length=256)),
                ('metavalue', models.CharField(default=0, max_length=500)),
                ('date', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('membership_id', models.CharField(max_length=5)),
                ('subscription_level', models.CharField(max_length=5)),
                ('industry_id', models.CharField(max_length=5)),
                ('contact_number', models.CharField(max_length=128, null=True)),
                ('login_type', models.CharField(default=1, max_length=5)),
                ('company_name', models.CharField(max_length=128, null=True)),
                ('dob', models.DateField(null=True, verbose_name='date published')),
                ('gender', models.CharField(max_length=50, null=True)),
                ('category', models.CharField(max_length=50, null=True)),
                ('picture', models.ImageField(blank=True, max_length=256, upload_to='profile_images')),
                ('address1', models.CharField(max_length=150, null=True)),
                ('address2', models.CharField(max_length=150, null=True)),
                ('login_api', models.CharField(default=0, max_length=256)),
                ('fb_id', models.CharField(default=0, max_length=256)),
                ('gmail_id', models.CharField(default=0, max_length=256)),
                ('city', models.CharField(max_length=150, null=True)),
                ('country', models.CharField(max_length=150, null=True)),
                ('state', models.CharField(max_length=150, null=True)),
                ('country_code', models.CharField(max_length=150, null=True)),
                ('state_code', models.CharField(max_length=150, null=True)),
                ('zip_code', models.CharField(max_length=100, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='industry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Industry', to='blog.Industry'),
        ),
        migrations.AddField(
            model_name='client',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assessment',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Client'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='membership',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Membership'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]