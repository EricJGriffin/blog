from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import BlogPost
from .forms import BlogPostForm, BlogPostModelForm
from comments.models import Comment
from comments.forms import CommentForm

# Create your views here.

def blog_post_list_view(request):
	qs = BlogPost.objects.published()
	if request.user.is_authenticated:
		my_qs = BlogPost.objects.filter(user=request.user)
		qs = (qs | my_qs).distinct()
	template_name = 'blog/list.html'
	context = {'object_list' : qs}
	return render(request, template_name, context)

# @login_required
@staff_member_required
def blog_post_create_view(request):
	form = BlogPostModelForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		obj = form.save(commit=False)
		obj.user = request.user
		obj.save()
		form = BlogPostModelForm()
	template_name = 'form.html'
	context = {'form': form}
	return render(request, template_name, context)

def blog_post_detail_view(request, slug):
	obj = get_object_or_404(BlogPost, slug=slug)
	template_name = "blog/detail.html"

	comments = obj.comments

	initial_data = {
		"content_type" : obj.get_content_type,
		"object_id" : obj.id
	}
	comment_form = CommentForm(request.POST or None, initial=initial_data)
	if comment_form.is_valid():
		c_type = comment_form.cleaned_data.get("content_type")
		if c_type == 'blog post':
			c_type = BlogPost
		content_type = ContentType.objects.get_for_model(model=c_type)
		obj_id = comment_form.cleaned_data.get("object_id")
		content_data = comment_form.cleaned_data.get("content")
		parent_obj = None
		try:
			parent_id = int(request.POST.get("parent_id"))
		except:
			parent_id = None

		if parent_id:
			parent_qs = Comment.objects.filter(id=parent_id)
			if parent_qs.exists() and parent_qs.count() == 1:
				parent_obj = parent_qs.first()

		new_comment, created = Comment.objects.get_or_create(
									user = request.user,
									content_type = content_type,
									object_id = obj_id,
									content = content_data,
									parent = parent_obj,
								)
		return redirect(new_comment.content_object.get_absolute_url())

	#method 2
	# comments = Comment.objects.filter_by_instance(obj) 

	# method 1
	# content_type = ContentType.objects.get_for_model(BlogPost)
	# obj_id = obj.id 	
	# comments = Comment.objects.filter(content_type = content_type, object_id = obj_id)
	# the above 3 lines are really just saying BlogPost.objects.get(id=obj.id)

	context = {"object": obj, "comments" : comments, "comment_form" : comment_form}
	return render(request, template_name, context)

@staff_member_required
def blog_post_update_view(request, slug):
	obj = get_object_or_404(BlogPost, slug=slug)
	form = BlogPostModelForm(request.POST or None, instance = obj)
	if form.is_valid():
		form.save()
	template_name = 'form.html'
	context = {'form': form, "title" : f"Update {obj.title}"}
	return render(request, template_name, context)

@staff_member_required
def blog_post_delete_view(request, slug):
	obj = get_object_or_404(BlogPost, slug=slug)
	template_name = 'blog/delete.html'
	if request.method == "POST":
		obj.delete()
		return redirect("/blog")
	context = {'object':obj}
	return render(request, template_name, context)