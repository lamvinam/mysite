from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
from ..models import Post

register = template.Library()


@register.simple_tag
def total_posts_tag():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def latest_posts_tag(limit=5):
    latest_posts = Post.published.order_by('-publish')[:limit]
    return {'latest_posts': latest_posts}

# Mele version of most_commented_posts_tag.
# Copy & add Mele html code for simple tag to base.html when use this.
# @register.simple_tag
# def most_commented_posts_tag(limit=5):
#     return Post.published.annotate(
#                total_comments=Count('comments')
#            ).order_by('-total_comments')[:limit]


# My version of most_commented_posts_tag
@register.inclusion_tag('blog/post/most_commented_posts.html')
def most_commented_posts_tag(limit=5):
    most_commented_posts = Post.published.annotate(
               total_comments=Count('comments')
           ).exclude(total_comments=0).order_by('-total_comments')[:limit]
    return {'most_commented_posts': most_commented_posts}

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
