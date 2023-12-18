from django.shortcuts import render, get_object_or_404
from .models import Post, Ip
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
import re
from taggit.models import Tag
from django.db.models import Count
from django.urls import reverse
from pathlib import Path
from django.views.decorators.http import require_POST
from django.http import JsonResponse

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Pagination with 3 posts per page
    # paginator is an iterable derived from post_list
    paginator = Paginator(post_list, 6)
    page_number = request.GET.get('page', 1)
    try:
        # Deliver the posts of page number derived from GET['page'].
        # posts is an iterable derived from paginator.
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html',
                  {'posts': posts,
                   'tag': tag})


def post_detail(request, year, month, day, slug):

    raw_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if raw_ip is not None:
        ip = raw_ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')


    post = get_object_or_404(Post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             slug=slug,
                             status=Post.Status.PUBLISHED)

    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()

    # List of similar posts
    # post_tags_ids = post.tags.values_list('id', flat=True)
    # similar_posts = Post.published.filter(tags__in=post_tags_ids)\
    #     .exclude(id=post.id)
    # similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
    #     .order_by('-same_tags', '-publish')[:4]
    similar_posts = post.tags.similar_objects()[0:4]

    # List of tags
    post_tags = post.tags.all()

    # get absolute url (just need to call post.get_absolute_url method)
    # absolute_url = reverse('blog:post_detail', args=[year, month, day, slug])

    return render(request, 'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts,
                   'post_tags': post_tags,
                   'ip': ip})


# class PostListView(ListView):
#     """
#     Alternative post list view
#     """
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


# class PostListView(ListView):
#     """
#     2nd Alternative post list view.
#     Need to change the list.html file name to post_list.html,
#     its directory to blog\, and 1st iterable to object_list. (Django default)
#     """
#     model = Post  # (Django default) object_list = Post.objects.all()
#     paginate_by = 3


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            sender_email = None
            recipients_email = re.split(r"[-;,\s]\s*", cd['to'])
            # send_mail(subject, message, sender_email, recipients_email)
            send_mail(subject, message, sender_email, recipients_email)
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html',
                  {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})

def about(request):
    file_path = Path('static/text/about_paragraph.txt')
    with open(file_path, 'r') as file:
        file_contents = file.read()
    return render(request, 'blog/about.html', {'about_paragraph': file_contents})


@require_POST
def post_like(request):

    raw_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if raw_ip is not None:
        ip = raw_ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')


    post_id = request.POST.get('id')
    action = request.POST.get('action')
    if post_id and action:
        try:
            post = Post.objects.get(id=post_id)
            if action == 'like':
                current_ip = Ip.objects.create(ip=ip, post_id=post.id)
                post.ip_like.add(current_ip)
                post.save()
            else:
                current_ip = post.ip_like.get(post_id=post.id)
                post.ip_like.remove(current_ip)
                current_ip.delete()

            return JsonResponse({'status': 'ok'})
        except Post.DoesNotExist:
            pass

    return JsonResponse({'status': 'error'})
