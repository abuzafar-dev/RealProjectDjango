"""Fill the database with realistic demo content for presentations.

Safe to run many times: existing users, categories and posts (matched by
username / slug / title) are reused, never duplicated or overwritten.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from blog.models import Category, Comment, Post

DEMO_PASSWORD = 'Demo_parol_123'

CATEGORIES = [
    ('Python', 'python'),
    ('Django', 'django'),
    ('JavaScript', 'javascript'),
    ('Git', 'git'),
    ("Ma'lumotlar bazasi", 'database'),
    ('Karyera', 'karyera'),
]

AUTHORS = [
    ('dilnoza', 'Dilnoza', 'Karimova'),
    ('jasur', 'Jasur', 'Toshmatov'),
    ('madina', 'Madina', 'Rahimova'),
]

POSTS = [
    {
        'author': 'dilnoza', 'category': 'python', 'days_ago': 1, 'views': 214,
        'title': "Python'da list comprehension: bir qatorda toza kod",
        'text': """Ko'p boshlovchilar ro'yxat yaratish uchun har safar for sikli va append yozadi. Python bunga ancha qisqa yo'l beradi — list comprehension.

## Oddiy misol

Quyidagi ikki kod bir xil natija beradi:

```python
kvadratlar = []
for son in range(10):
    kvadratlar.append(son * son)

kvadratlar = [son * son for son in range(10)]
```

## Shart qo'shish

Faqat juft sonlarni olish uchun oxiriga `if` qo'shiladi:

```python
juftlar = [son for son in range(20) if son % 2 == 0]
```

## Qachon ishlatmaslik kerak

Agar ifoda uzun bo'lib, bir qatorga sig'masa yoki ichida bir nechta shart bo'lsa, oddiy for sikl o'qishga osonroq. Qoida oddiy: kod qisqa bo'lishi emas, tushunarli bo'lishi muhim.""",
    },
    {
        'author': 'jasur', 'category': 'django', 'days_ago': 2, 'views': 342,
        'title': "Django'da select_related: N+1 muammosini 1 qatorda hal qilish",
        'text': """Sahifangiz sekin ishlayaptimi? Ko'pincha sabab — N+1 so'rov muammosi. 20 ta post chiqarsangiz va har birining muallifini ko'rsatsangiz, Django 1 emas, 21 ta SQL so'rov yuboradi.

## Muammo

```python
posts = Post.objects.all()
for post in posts:
    print(post.author.username)  # har safar yangi so'rov!
```

## Yechim

`select_related` bog'langan jadvalni JOIN orqali bitta so'rovda olib keladi:

```python
posts = Post.objects.select_related('author', 'category')
```

ForeignKey va OneToOne uchun `select_related`, ManyToMany va teskari bog'lanishlar uchun esa `prefetch_related` ishlatiladi.

## Qanday tekshirish mumkin

django-debug-toolbar o'rnating yoki testda `assertNumQueries` dan foydalaning. Shu blogning bosh sahifasi ham aynan shu usul bilan bir nechta so'rovda ochiladi.""",
    },
    {
        'author': 'madina', 'category': 'git', 'days_ago': 3, 'views': 189,
        'title': 'Git: har kuni kerak bo\'ladigan 7 ta buyruq',
        'text': """Git'ning yuzlab buyrug'i bor, lekin kundalik ishning 90 foizi bir nechtasi bilan bajariladi.

```bash
git status              # nima o'zgardi?
git add fayl.py         # o'zgarishni tayyorlash
git commit -m "Izoh"    # saqlash
git pull                # serverdagi yangiliklarni olish
git push                # o'zingiznikini yuborish
git switch -c yangi-funksiya   # yangi branch
git log --oneline       # qisqa tarix
```

## Yaxshi commit xabari

Commit xabari nima uchun o'zgartirganingizni aytishi kerak. "fix" yoki "update" emas, balki `Login sahifasida bo'sh parol xatosini tuzatish` kabi.

## Bitta maslahat

Har bir yangi ish uchun alohida branch oching. main branch doim ishlaydigan holatda tursin — ustozingiz yoki jamoangiz shunga tayanadi.""",
    },
    {
        'author': 'jasur', 'category': 'javascript', 'days_ago': 5, 'views': 156,
        'title': 'JavaScript: let, const va var farqi oddiy tilda',
        'text': """Zamonaviy JavaScript'da o'zgaruvchi e'lon qilishning uchta usuli bor. Qaysi birini qachon ishlatish kerak?

## const — standart tanlov

Qiymati qayta tayinlanmaydigan o'zgaruvchilar uchun. Kodning ko'p qismi shu bilan yoziladi.

```javascript
const narx = 25000;
const foydalanuvchi = { ism: 'Ali' };
foydalanuvchi.ism = 'Vali'; // obyekt ichini o'zgartirish mumkin
```

## let — qiymat o'zgarsa

```javascript
let hisob = 0;
hisob += 1;
```

## var — ishlatmang

`var` blok doirasini tan olmaydi va kutilmagan xatolarga olib keladi. Eski kodlarda uchraydi, yangi kodda unga ehtiyoj yo'q.

Qoida: avval `const` yozing, qiymat o'zgarishi kerak bo'lsa — `let` ga almashtiring.""",
    },
    {
        'author': 'dilnoza', 'category': 'database', 'days_ago': 7, 'views': 267,
        'title': "SQL'ni 15 daqiqada tushunish: SELECT, WHERE, JOIN",
        'text': """Har qanday backend dasturchi SQL'ni bilishi kerak, hatto ORM ishlatsa ham. Mana eng muhim uchta tushuncha.

## SELECT va WHERE

```sql
SELECT title, views
FROM blog_post
WHERE views > 100
ORDER BY views DESC;
```

## JOIN — jadvallarni bog'lash

Post va uning muallifini bir vaqtda olish:

```sql
SELECT p.title, u.username
FROM blog_post p
JOIN auth_user u ON u.id = p.author_id;
```

## Django'da ko'rish

Django qanday SQL yozayotganini bilish uchun `print(queryset.query)` dan foydalaning. Bu ORM va SQL o'rtasidagi bog'liqlikni tushunishning eng tez yo'li.""",
    },
    {
        'author': 'madina', 'category': 'karyera', 'days_ago': 9, 'views': 398,
        'title': 'Birinchi ish uchun portfolio: nima qo\'yish kerak?',
        'text': """Junior dasturchi sifatida ish qidirayotganda tajriba o'rnini portfolio bosadi. Lekin 20 ta yarim tayyor loyiha emas, 2-3 ta tugallangan loyiha kerak.

## Yaxshi loyiha belgilari

Real muammoni hal qiladi. README'da nima uchun yozilgani va qanday ishga tushirilishi aniq yozilgan. Testlari bor. Kodi toza va bir xil uslubda.

## Ko'rsatish oson bo'lsin

Ish beruvchi loyihangizni 2 daqiqada ishga tushira olishi kerak. `make run` kabi bitta buyruq va namunaviy ma'lumotlar katta farq qiladi.

## GitHub profilingiz

Pin qilingan loyihalar, tushunarli commit tarixi va har bir repoda qisqa tavsif. Bu sizning ish uslubingiz haqida rezyumedan ko'ra ko'proq gapiradi.""",
    },
    {
        'author': 'jasur', 'category': 'python', 'days_ago': 12, 'views': 121,
        'title': 'Virtual muhit (venv) nima va nega u shart?',
        'text': """Har bir Python loyihaning o'z kutubxonalari va versiyalari bor. Ular bir-biriga xalaqit bermasligi uchun virtual muhit ishlatiladi.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## requirements.txt

Loyiha qaysi kutubxonalarga bog'liqligini shu faylga yozib qo'ying. Shunda boshqa odam bir buyruq bilan aynan sizdagi muhitni tiklaydi.

## .venv'ni git'ga qo'shmang

Virtual muhit papkasi `.gitignore` ga yozilishi kerak. Git'da faqat kod va `requirements.txt` saqlanadi.""",
    },
    {
        'author': 'dilnoza', 'category': 'django', 'days_ago': 15, 'views': 233,
        'title': "Django formalari: validatsiyani to'g'ri joyda qilish",
        'text': """Foydalanuvchi kiritgan ma'lumotga hech qachon ishonmang. Django formalari tekshiruvni bir joyda va tartibli qilish imkonini beradi.

## clean_<field> usuli

```python
class PostForm(forms.ModelForm):
    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 5:
            raise forms.ValidationError("Sarlavha juda qisqa")
        return title
```

## View'da tekshirish

```python
form = PostForm(request.POST or None)
if form.is_valid():
    form.save()
```

Xato bo'lsa, forma o'sha sahifaga xato xabarlari bilan qaytadi. Shu blogdagi "Yangi post" formasi ham aynan shunday ishlaydi.""",
    },
    {
        'author': 'madina', 'category': 'javascript', 'days_ago': 20, 'views': 98,
        'title': 'fetch() bilan API\'dan ma\'lumot olish',
        'text': """Brauzerda serverdan ma'lumot olishning zamonaviy usuli — `fetch`. U Promise qaytaradi, shuning uchun `async/await` bilan juda qulay.

```javascript
async function postlarniOl() {
    const javob = await fetch('/api/posts/');
    if (!javob.ok) {
        throw new Error(`Xatolik: ${javob.status}`);
    }
    return await javob.json();
}
```

## Xatolarni unutmang

`fetch` faqat tarmoq uzilganda xato beradi. 404 yoki 500 javobni `javob.ok` orqali o'zingiz tekshirishingiz kerak — bu boshlovchilar eng ko'p o'tkazib yuboradigan joy.""",
    },
]

COMMENTS = [
    (1, 'madina', "Juda tushunarli! Men ham doim append yozardim."),
    (1, 'jasur', 'Generator ifodasi haqida ham yozsangiz, ular xotirani tejaydi.'),
    (2, 'dilnoza', "assertNumQueries haqidagi maslahat uchun rahmat, darhol testga qo'shdim."),
    (2, 'madina', 'prefetch_related misolini ham ko\'rsatsangiz bo\'lardi.'),
    (2, 'jasur', "Albatta, keyingi maqolada alohida yozaman."),
    (3, 'jasur', "git switch'ni bilmagan ekanman, checkout ishlatib yurardim."),
    (5, 'jasur', 'JOIN turlarini (LEFT, INNER) ham qo\'shsangiz zo\'r bo\'lardi.'),
    (6, 'dilnoza', "Ayniqsa 'bitta buyruq bilan ishga tushirish' qismi muhim."),
    (6, 'jasur', "Testlar haqidagi fikrga to'liq qo'shilaman."),
    (8, 'madina', 'clean() va clean_<field> farqini ham yozing iltimos.'),
]


class Command(BaseCommand):
    help = "Demo uchun kategoriya, muallif, maqola va izohlar qo'shadi (qayta ishga tushirish xavfsiz)."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        now = timezone.now()

        categories = {}
        for name, slug in CATEGORIES:
            categories[slug], _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})

        authors, new_users = {}, 0
        for username, first, last in AUTHORS:
            user, created = User.objects.get_or_create(
                username=username, defaults={'first_name': first, 'last_name': last},
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
                new_users += 1
            authors[username] = user

        posts, new_posts = [], 0
        for data in POSTS:
            post, created = Post.objects.get_or_create(
                title=data['title'],
                defaults={
                    'author': authors[data['author']],
                    'category': categories[data['category']],
                    'text': data['text'],
                    'views': data['views'],
                },
            )
            if created:
                Post.objects.filter(pk=post.pk).update(created_at=now - timedelta(days=data['days_ago'], hours=3))
                new_posts += 1
            posts.append((post, created))

        new_comments = 0
        for position, (index, username, text) in enumerate(COMMENTS):
            post, created = posts[index - 1]
            if created:
                comment = Comment.objects.create(post=post, author=authors[username], text=text)
                published = Post.objects.values_list('created_at', flat=True).get(pk=post.pk)
                Comment.objects.filter(pk=comment.pk).update(
                    created_at=published + timedelta(hours=2 + position * 3, minutes=17 * position % 60),
                )
                new_comments += 1

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {new_users} muallif, {new_posts} maqola, {new_comments} izoh qo'shildi."
        ))
        if new_users:
            self.stdout.write(f"Demo mualliflar paroli: {DEMO_PASSWORD} ({', '.join(a[0] for a in AUTHORS)})")
