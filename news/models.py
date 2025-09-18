from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="author_profile")
    rating = models.IntegerField(default=0)

    def update_rating(self) -> None:
        posts_rating_sum = self.post_set.aggregate(total=models.Sum("rating")).get("total") or 0
        comments_rating_sum = self.user.comment_set.aggregate(total=models.Sum("rating")).get("total") or 0
        posts_comments_rating_sum = Comment.objects.filter(post__author=self).aggregate(total=models.Sum("rating")).get("total") or 0
        self.rating = posts_rating_sum * 3 + comments_rating_sum + posts_comments_rating_sum
        self.save(update_fields=["rating"])

    def __str__(self) -> str:
        return f"Author({self.user.username})"


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    ARTICLE = "AR"
    NEWS = "NW"
    POST_TYPES = [
        (ARTICLE, "статья"),
        (NEWS, "новость"),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through="PostCategory", related_name="posts")
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self) -> None:
        self.rating = models.F("rating") + 1
        self.save(update_fields=["rating"])
        self.refresh_from_db(fields=["rating"])  # resolve F-expression

    def dislike(self) -> None:
        self.rating = models.F("rating") - 1
        self.save(update_fields=["rating"])
        self.refresh_from_db(fields=["rating"])  # resolve F-expression

    def preview(self) -> str:
        return f"{self.text[:124]}..."

    def __str__(self) -> str:
        return f"{self.get_post_type_display()}: {self.title}"


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.post_id}:{self.category_id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self) -> None:
        self.rating = models.F("rating") + 1
        self.save(update_fields=["rating"])
        self.refresh_from_db(fields=["rating"])  # resolve F-expression

    def dislike(self) -> None:
        self.rating = models.F("rating") - 1
        self.save(update_fields=["rating"])
        self.refresh_from_db(fields=["rating"])  # resolve F-expression

    def __str__(self) -> str:
        return f"Comment by {self.user.username} on {self.post_id}"


# Create your models here.
