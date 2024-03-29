from django import forms
from rango.models import Page, Category, UserProfile


class CategoryForm(forms.ModelForm):
	name = forms.CharField(max_length=128, help_text="Please enter the category name")
	views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

	class Meta:
		model = Category


class PageForm(forms.ModelForm):
	title = forms.CharField(max_length=128, help_text="Please enter the page title")
	url = forms.URLField(max_length=200, help_text="Please enter the page url")
	views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

	class Meta:
		model = Page

		fields = ('title', 'url', 'views')

	def clean(self):
		cleaned_data = self.cleaned_data
		url = cleaned_data.get('url')

		if url and not url.startswith('http://'):
			url = url + 'http://'
			cleaned_data['url'] = url

		return cleaned_data

from django.contrib.auth.models import User
class UserForm(forms.ModelForm):
	username = forms.CharField(help_text="Please enter a username.")
	email = forms.CharField(help_text="Please enter your email.")
	password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter a password")

	class Meta:
		model = User
		fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
	website = forms.URLField(help_text="Please enter your website.", required=False)
	picture = forms.ImageField(help_text="Select a profile image to upload.", required=False)
	class Meta:
		model = UserProfile
		fields = ('website', 'picture')