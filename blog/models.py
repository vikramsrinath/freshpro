from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage


class Post(models.Model):
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.title


class Country(models.Model):
    country_name = models.CharField(max_length=128)
    iso_code = models.CharField(max_length=500)
    phone_code = models.CharField(max_length=500, default=0)
    is_active = models.CharField(max_length=5, default=1)

    def __unicode__(self):
        return self.Country.country_name


class Industry(models.Model):
    industry_name = models.CharField(max_length=128, unique=True)
    is_active = models.CharField(max_length=5, default=1)

    def __unicode__(self):
        return self.Industry.industry_name


class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    industry = models.ForeignKey(
        Industry, related_name='Industry', on_delete=models.CASCADE)
    client_name = models.CharField(max_length=128)
    is_active = models.CharField(max_length=5, default=1)

    def __unicode__(self):
        return self.Industry.industry_name


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_level = models.CharField(max_length=128)
    user_comapany = models.CharField(max_length=128)
    is_active = models.CharField(max_length=5, default=1)

    def __unicode__(self):
        return self.Membership.user_comapany


class MembershipClient(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    is_active = models.CharField(max_length=5, default=1)

    def __unicode__(self):
        return self.Membership.user_comapany


class Assessment(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_score = models.CharField(max_length=5, default=0)
    finance_score = models.CharField(max_length=5, default=0)
    marketing_score = models.CharField(max_length=5, default=0)
    human_score = models.CharField(max_length=5, default=0)
    technology_score = models.CharField(max_length=5, default=0)
    total_score = models.CharField(max_length=5, default=0)
    is_active = models.CharField(max_length=5, default=1)

    def __unicode__(self):
        return self.Membership.user_comapany


class Category(models.Model):
    category_name = models.CharField(max_length=128, unique=True)
    category_desc = models.CharField(max_length=1000)
    category_slug = models.CharField(max_length=200)
    pid = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    is_active = models.CharField(max_length=5, default=1)
    picture = models.ImageField(upload_to='category', blank=True)

    def __unicode__(self):
        return self.category_name


class Page(models.Model):
    category = models.ForeignKey(
        'category',
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_id = models.CharField(max_length=5)
    subscription_level = models.CharField(max_length=5)
    industry_id = models.CharField(max_length=5)
    contact_number = models.CharField(max_length=128, null=True)
    login_type = models.CharField(max_length=5, default=1)
    company_name = models.CharField(max_length=128, null=True)

    dob = models.DateField('date published', null=True)
    gender = models.CharField(max_length=50, null=True)
    category = models.CharField(max_length=50, null=True)
    picture = models.ImageField(
        upload_to='profile_images', max_length=256, blank=True)
    address1 = models.CharField(max_length=150, null=True)
    address2 = models.CharField(max_length=150, null=True)
    login_api = models.CharField(max_length=256, default=0)
    fb_id = models.CharField(max_length=256, default=0)
    gmail_id = models.CharField(max_length=256, default=0)
    city = models.CharField(max_length=150, null=True)
    # country = models.ForeignKey(Country, related_name='country')
    # state = models.ForeignKey(State, related_name='state')
    country = models.CharField(max_length=150, null=True)
    state = models.CharField(max_length=150, null=True)
    country_code = models.CharField(max_length=150, null=True)
    state_code = models.CharField(max_length=150, null=True)
    zip_code = models.CharField(max_length=100, null=True)
    # login_type = models.CharField(max_length=256, default=0)

    #picture = models.FileField(upload_to=lambda instance, filename: '/'.join(['mymodel', str(instance.pk), filename]),)
    def __unicode__(self):
        return self.user.username


class user_audit(models.Model):
    description = models.CharField(max_length=256, default=0)
    meta_key = models.CharField(max_length=256, default=0)
    metavalue = models.CharField(max_length=500, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()

    def __unicode__(self):
        return self.user_audit.description


class State(models.Model):
    country = models.ForeignKey(
        Country, related_name='Country', on_delete=models.CASCADE)
    state_name = models.CharField(max_length=128)
    state_code = models.CharField(max_length=128)
    is_active = models.CharField(max_length=5, default=1)

    def __unicode__(self):
        return self.State.state_name
