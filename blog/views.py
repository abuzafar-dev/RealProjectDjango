from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from blog.forms import CommentForm, PostForm
from blog.models import Category, Post


class PostListView(ListView):
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        posts = Post.objects.select_related('author', 'category').annotate(comment_count=Count('comments')).order_by('-created_at')
        query = self.request.GET.get('q')
        if query:
            posts = posts.filter(Q(title__icontains=query) | Q(text__icontains=query))
        category = self.request.GET.get('category')
        if category:
            posts = posts.filter(category__slug=category)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related('author', 'category'), pk=pk)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Izoh qo'shildi")
            return redirect(post)
    else:
        Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
    comments = post.comments.select_related('author')
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'form': form})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post qo'shildi")
        return super().form_valid(form)


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class PostUpdateView(AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Post yangilandi')
        return super().form_valid(form)


class PostDeleteView(AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        messages.success(self.request, "Post o'chirildi")
        return super().form_valid(form)


@login_required
def my_posts(request):
    posts = request.user.posts.select_related('category').annotate(comment_count=Count('comments')).order_by('-created_at')
    return render(request, 'blog/my_posts.html', {'posts': posts})
