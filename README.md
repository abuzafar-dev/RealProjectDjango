# Daftar — o'zbek tilida dasturlash maqolalari (Django + Jinja2)

**Muammo:** o'zbek tilidagi dasturlash materiallari kam va Telegram kanallar, guruhlar, shaxsiy bloglarga sochilib ketgan. Ularni qidirib topish, mavzu bo'yicha saralash va muallifga savol berish qiyin.

**Yechim:** Daftar — dasturchilar o'zbek tilida bilim ulashadigan blog. Maqolalar kategoriyalarga ajratilgan, qidiriladi, kod misollari chiroyli ko'rinadi, izohlarda savol-javob qilinadi.

## Tez boshlash

```bash
make demo    # .venv, .env, migratsiya, demo maqolalar va server — bitta buyruq
make test    # Django check + migratsiya tekshiruvi + testlar
```

http://127.0.0.1:8000/ — sayt, http://127.0.0.1:8000/admin/ — admin panel.

Demo mualliflar (`make seed` yaratadi): `dilnoza`, `jasur`, `madina`, paroli `Demo_parol_123`.

| Buyruq | Nima qiladi |
|---|---|
| `make demo` | demo ma'lumot qo'shib serverni ishga tushiradi |
| `make run` | serverni ishga tushiradi |
| `make seed` | 6 kategoriya, 3 muallif, 9 maqola, 10 izoh qo'shadi (qayta ishga tushirish xavfsiz) |
| `make test` | CI'dagi tekshiruvlarning o'zi |

## Imkoniyatlar

- **Maqolalar ro'yxati:** qidiruv, kategoriya filtri, "Yangi / Mashhur" saralash, sahifalash (filtrlar sahifa almashganda saqlanadi)
- **Maqola sahifasi:** o'qish vaqti, ko'rishlar soni, kod bloklari, shu mavzudagi boshqa maqolalar
- **Matn formati:** bo'sh qator — xatboshi, `## ` — sarlavha, ```` ```python ```` — kod bloki, `` `kod` `` — qisqa kod. Matn avval to'liq HTML-escape qilinadi, shuning uchun XSS bo'lmaydi
- **Izohlar:** faqat kirganlar yozadi; izoh muallifi yoki maqola muallifi o'chira oladi
- **Muallif sahifasi:** maqolalar, jami ko'rishlar va izohlar statistikasi
- **Huquqlar:** postni faqat uning muallifi tahrirlay va o'chira oladi (boshqalarga 403)
- **Akkaunt:** ro'yxatdan o'tish, kirish, chiqish; xato xabarlari o'zbek tilida
- 404 va 500 sahifalari, admin panel

## Frontend

- CDN yo'q: o'z dizayn tizimi `static/css/app.css` da (ranglar, shrift o'lchamlari, oraliqlar, radiuslar tokenlar orqali)
- Qayta ishlatiladigan Jinja2 makrolari: `templates/components/ui.html` (`post_card`, `field`, `pagination`, `empty`, `icon`, `avatar`)
- Mobilga mos (375px dan), klaviatura bilan boshqarish (`:focus-visible`, "asosiy qismga o'tish" havolasi), matn kontrasti WCAG AA darajasida
- Bo'sh holatlar (qidiruv natija bermasa, post yo'q bo'lsa) foydalanuvchiga keyingi qadamni ko'rsatadi

## Jinja2 sozlamasi

- `config/settings.py` ichida `TEMPLATES` ga `Jinja2` backend qo'shilgan (admin panel uchun `DjangoTemplates` ham qoldirilgan)
- `config/jinja2.py`: `static()`, `url()`, `get_messages()`, `now()` globallari; `date`, `initials`, `display_name` filtrlari

## Tuzilishi

```
accounts/                   ro'yxatdan o'tish, login, logout (o'zbekcha xato xabarlari)
blog/models.py              Category, Post, Comment
blog/text.py                maqola matnini xavfsiz HTML'ga aylantirish, o'qish vaqti
blog/management/commands/   seed_demo — demo ma'lumotlar
templates/components/ui.html  qayta ishlatiladigan Jinja2 makrolari
static/css/app.css          dizayn tizimi
config/                     sozlamalar, Jinja2 environment
```

## Ustozga ko'rsatish (5 daqiqa)

1. `make demo` → http://127.0.0.1:8000/ ni oching. Muammo va yechim bosh sahifadagi birinchi blokda yozilgan.
2. Qidiruvga `django` yozing (3 ta natija), keyin o'ngdan **Django** kategoriyasini bosing (2 ta natija), so'ng **Mashhur** tabiga o'ting. Filtrlar birga ishlaydi, × belgisi har birini alohida olib tashlaydi.
3. "Django'da select_related" maqolasini oching: kod bloklari, o'qish vaqti, shu mavzudagi maqolalar va izohlar ko'rinadi.
4. `jasur` / `Demo_parol_123` bilan kiring. **Yozish** tugmasini bosing va formani bo'sh holda yuboring: xatolar o'zbekcha chiqadi. Keyin kod bloki bor post yozing.
5. Dilnozaning postini tahrirlashga urinib ko'ring (`/posts/1/edit/`): 403 qaytadi.
6. Izoh qoldiring va uni o'chiring. Muallif sahifasini oching (`/authors/jasur/`).
7. Telefon ko'rinishini ko'rsatish uchun brauzerda F12 → mobil rejimga o'ting.
8. `make test` — 31 ta test.

**Ustoz so'rashi mumkin:**
- *N+1 muammosi qanday hal qilingan?* `select_related('author', 'category')` va `annotate(Count('comments'))` ishlatilgan.
- *XSS'dan qanday himoyalangan?* `blog/text.py` avval matnni `escape` qiladi, keyin faqat o'zi yaratgan teglarni qo'shadi. Buni test ham tekshiradi.
- *Ko'rishlar soni nega `F('views') + 1` bilan oshiriladi?* Bir vaqtda kelgan so'rovlarda qiymat yo'qolmasligi uchun: hisob bazaning o'zida bajariladi.
- *Nega Jinja2?* U Django shablonlaridan tezroq, ichida Python ifodalari va makrolar ishlaydi. Admin panel esa DjangoTemplates'da qolgan.
