from django.shortcuts import render
from django.http import HttpResponse
from .forms import ContactForm
from blog.models import BlogPost

def home_page(request):
	my_title = "Welcome to My Journal!"
	qs = BlogPost.objects.published()[:5]
	context = {
		"message" : my_title, 

		"blog_list" : qs
	}
	return render(request, "home.html", context)

def contact_page(request):
	form = ContactForm(request.POST or None)
	if form.is_valid():
		print(form.cleaned_data)
		form = ContactForm()
	context = {
		"title" : "Contact us",
		"form" : form
	}
	return render(request, "form.html", context)