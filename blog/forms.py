from django import forms
from django.contrib.auth.models import User
from . models import Page, Category, UserProfile


class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    # An inline class to provide additional information on the form.
    class Meta:
        model = Category
        fields = "__all__"
    # class Meta:
        # Provide an association between the ModelForm and a model
        #model = Category


class PageForm(forms.ModelForm):
    title = forms.CharField(
        max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(
        max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # If url is not empty and doesn't start with 'http://' add 'http://' to the beginning
        if url and not url.startswith('http://'):
            url = 'http://' + url

            cleaned_data['url'] = url
        return cleaned_data

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Page

        # What fields do we want to include in our form?
        # This way we don't need every field in the model present.
        # Some fields may allow NULL values, so we may not want to include them...
        # Here, we are hiding the foreign keys
        fields = ('title', 'url', 'views')


class UserForm(forms.ModelForm):
    username = forms.CharField(help_text="Please enter a username.")
    first_name = forms.CharField(help_text="Please enter your First Name.")
    last_name = forms.CharField(help_text="Please enter your First Name.")
    email = forms.CharField(help_text="Please enter your email.")
    password = forms.CharField(
        widget=forms.PasswordInput(), help_text="Please enter a password.")
    # subscription_Level = forms.CharField(
    #     help_text="Please enter your Subscription Level.")
    # industry_id = forms.CharField(widget=forms.Select,
    #                               help_text="Please enter your industry.")
    # membership_id = forms.CharField(
    #     help_text="Please enter your membership.")
    # subscription_level = forms.CharField(
    #     help_text="Please enter your subscription level.")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password',)
        #   'industry_id', 'membership_id', 'subscription_level', 'is_staff')


class UserProfileForm(forms.ModelForm):

    website = forms.URLField(
        help_text="Please enter your website.", required=False)
    contact_number = forms.URLField(
        help_text="Please enter your Contact Number.", required=False)
    picture = forms.ImageField(
        help_text="Select a profile image to upload.", required=False)

    class Meta:
        model = UserProfile
        fields = ('website', 'contact_number', 'picture')
