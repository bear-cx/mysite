from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from .models import Blog, BlogType
from django.db.models import Count
from django.conf import settings


def get_blog_list_common_date(request,blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    page_num = request.GET.get('page', 1) #获取url的页面参数（GET请求）
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number #获取当前页码
    # 获取当前页码前后各2页的页码范围
    page_range = list(range(max(current_page_num -2, 1),current_page_num)) + \
                 list(range(current_page_num, min(current_page_num +2, paginator.num_pages) + 1))

    # 加上省略页码标记
    if page_range[0] -1 >=2:
        page_range.insert(0,'...')
    if paginator.num_pages - page_range[-1] >=2:
        page_range.append('...')

    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0,1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    #获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    content = {}
    content['blogs'] = page_of_blogs.object_list
    content['page_of_blogs'] = page_of_blogs
    content['page_range'] = page_range
    content['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    content['blog_dates'] = blog_dates_dict
    return content


def blog_list(request):
    blogs_all_list = Blog.objects.all()
    content = get_blog_list_common_date(request,blogs_all_list)
    return render_to_response('blog/blog_list.html', content)



def blogs_with_type(request,blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    content = get_blog_list_common_date(request,blogs_all_list)
    content['blog_type'] = blog_type
    return render_to_response('blog/blogs_with_type.html', content)

def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year =year, created_time__month=month)
    content = get_blog_list_common_date(request,blogs_all_list)
    content['blogs_with_date'] = '%s年%s月' %(year,month)
    return render_to_response('blog/blogs_with_date.html', content)

def blog_detail(request,blog_pk):
    content = {}
    blog = get_object_or_404(Blog, pk=blog_pk)
    content['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    content['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    content['blog'] = blog
    return render_to_response('blog/blog_detail.html', content)