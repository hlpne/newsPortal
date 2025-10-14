from django.test import TestCase
from django.urls import reverse
from django.template import Context, Template
from .models import Author, Post
from django.contrib.auth.models import User


class CensorFilterTests(TestCase):
    def render(self, tpl, ctx):
        return Template(tpl).render(Context(ctx))

    def test_censor_replaces_lowercase_bad_word(self):
        out = self.render("{% load news_filters %}{{ text|censor }}", {"text": "Нехороший человек — редиска!"})
        self.assertEqual(out, "Нехороший человек — р******!")

    def test_censor_replaces_capitalized_bad_word(self):
        out = self.render("{% load news_filters %}{{ text|censor }}", {"text": "Редиска, говоришь?"})
        self.assertEqual(out, "Р******, говоришь?")

    def test_censor_ignores_mixed_case_inside(self):
        out = self.render("{% load news_filters %}{{ text|censor }}", {"text": "РеДисКа"})
        self.assertEqual(out, "РеДисКа")

    def test_censor_non_string_raises(self):
        with self.assertRaises(TypeError):
            self.render("{% load news_filters %}{{ value|censor }}", {"value": 123})


class NewsViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("u")
        self.author = self.user.author_profile
        self.p1 = Post.objects.create(author=self.author, post_type=Post.NEWS, title="A", text="aaa")
        self.p2 = Post.objects.create(author=self.author, post_type=Post.NEWS, title="B", text="bbb")
        self.p3 = Post.objects.create(author=self.author, post_type=Post.NEWS, title="C", text="ccc")
        self.p1.refresh_from_db(); self.p2.refresh_from_db(); self.p3.refresh_from_db()

    def test_list_sorted_desc(self):
        resp = self.client.get(reverse('news_list'))
        self.assertEqual(resp.status_code, 200)
        posts = list(resp.context['posts'])
        dates = [p.created_at for p in posts]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_detail_date_format(self):
        resp = self.client.get(reverse('news_detail', args=[self.p1.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.p1.created_at.strftime('%d.%m.%Y'), resp.content.decode('utf-8'))

