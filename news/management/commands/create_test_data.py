from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from news.models import Author, Category, Post, Comment


class Command(BaseCommand):
    help = 'Создает тестовые данные для новостного портала'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Количество пользователей/авторов (по умолчанию 5)',
        )
        parser.add_argument(
            '--categories',
            type=int,
            default=8,
            help='Количество категорий (по умолчанию 8)',
        )
        parser.add_argument(
            '--posts',
            type=int,
            default=30,
            help='Количество постов (по умолчанию 30)',
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_categories = options['categories']
        num_posts = options['posts']

        self.stdout.write(self.style.SUCCESS('Начинаем создание тестовых данных...'))

        # Создание пользователей и авторов
        self.stdout.write('Создание пользователей и авторов...')
        users = []
        authors = []
        for i in range(1, num_users + 1):
            username = f'testuser{i}'
            email = f'testuser{i}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Test{i}',
                    'last_name': 'User',
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            
            author, created = Author.objects.get_or_create(
                user=user,
                defaults={'rating': random.randint(0, 100)}
            )
            users.append(user)
            authors.append(author)
            if created:
                self.stdout.write(f'  ✓ Создан пользователь: {username}')

        # Создание категорий
        self.stdout.write('Создание категорий...')
        category_names = [
            'Политика', 'Экономика', 'Технологии', 'Спорт',
            'Культура', 'Наука', 'Здоровье', 'Путешествия',
            'Образование', 'Развлечения', 'Бизнес', 'Медиа'
        ]
        
        categories = []
        for i, name in enumerate(category_names[:num_categories]):
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  ✓ Создана категория: {name}')

        # Создание постов (новостей и статей)
        self.stdout.write('Создание постов...')
        news_titles = [
            'Новые законы вступили в силу',
            'Встреча глав государств',
            'Реформа образования',
            'Новые технологии в медицине',
            'Спортивные достижения',
            'Культурные события',
            'Экономические показатели',
            'Научные открытия',
            'Здоровый образ жизни',
            'Туристические направления',
        ]
        
        article_titles = [
            'Как правильно инвестировать',
            'Анализ текущей ситуации',
            'Руководство по использованию',
            'Тенденции развития',
            'Практические советы',
            'Глубокий анализ проблемы',
            'Методы решения задач',
            'Опыт и рекомендации',
            'Теоретические основы',
            'Практические примеры',
        ]

        post_texts = [
            'Это интересная новость о важных событиях в мире. Она содержит много полезной информации для читателей.',
            'Данная статья рассказывает о последних изменениях и тенденциях в различных сферах жизни.',
            'Автор рассматривает актуальные проблемы и предлагает различные подходы к их решению.',
            'Материал основан на глубоком анализе фактов и данных, представленных экспертами.',
            'Статья охватывает широкий спектр вопросов, связанных с современными вызовами и возможностями.',
        ]

        posts_created = 0
        for i in range(num_posts):
            # Чередуем новости и статьи
            post_type = Post.NEWS if i % 2 == 0 else Post.ARTICLE
            if post_type == Post.NEWS:
                title_base = random.choice(news_titles)
            else:
                title_base = random.choice(article_titles)
            
            title = f'{title_base} #{i+1}'
            text = random.choice(post_texts) * (random.randint(2, 5))
            author = random.choice(authors)
            
            # Создаем пост с случайной датой в последние 30 дней
            days_ago = random.randint(0, 30)
            created_at = timezone.now() - timedelta(days=days_ago)
            
            post = Post.objects.create(
                author=author,
                post_type=post_type,
                title=title,
                text=text,
                rating=random.randint(-10, 50),
                created_at=created_at
            )
            
            # Добавляем случайные категории (1-3 категории на пост)
            num_cats = random.randint(1, min(3, len(categories)))
            selected_categories = random.sample(categories, num_cats)
            post.categories.set(selected_categories)
            
            posts_created += 1
            if posts_created % 10 == 0:
                self.stdout.write(f'  ✓ Создано постов: {posts_created}')

        # Создание комментариев
        self.stdout.write('Создание комментариев...')
        comment_texts = [
            'Очень интересная статья!',
            'Спасибо за информацию.',
            'Не согласен с некоторыми моментами.',
            'Отличный материал, рекомендую к прочтению.',
            'Есть что обсудить по этой теме.',
            'Много полезной информации.',
            'Требуется дополнительное изучение вопроса.',
        ]
        
        comments_created = 0
        for post in Post.objects.all()[:posts_created]:
            # Создаем 1-5 комментариев для каждого поста
            num_comments = random.randint(1, 5)
            for _ in range(num_comments):
                user = random.choice(users)
                days_ago = random.randint(0, 30)
                created_at = timezone.now() - timedelta(days=days_ago)
                
                Comment.objects.create(
                    post=post,
                    user=user,
                    text=random.choice(comment_texts),
                    rating=random.randint(-5, 10),
                    created_at=created_at
                )
                comments_created += 1
        
        self.stdout.write(f'  ✓ Создано комментариев: {comments_created}')

        # Создание подписок
        self.stdout.write('Создание подписок на категории...')
        subscriptions = 0
        for user in users:
            # Каждый пользователь подписывается на 2-4 случайные категории
            num_subs = random.randint(2, min(4, len(categories)))
            selected_cats = random.sample(categories, num_subs)
            for category in selected_cats:
                category.subscribers.add(user)
                subscriptions += 1
        
        self.stdout.write(f'  ✓ Создано подписок: {subscriptions}')

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Тестовые данные успешно созданы!\n'
            f'  - Пользователей: {len(users)}\n'
            f'  - Авторов: {len(authors)}\n'
            f'  - Категорий: {len(categories)}\n'
            f'  - Постов: {posts_created}\n'
            f'  - Комментариев: {comments_created}\n'
            f'  - Подписок: {subscriptions}\n'
            f'\nДля входа используйте:\n'
            f'  Username: testuser1 (и testuser2, testuser3 и т.д.)\n'
            f'  Password: testpass123'
        ))

