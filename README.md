# RealProjectDjango — Blog

Django'da yozilgan to'liq blog sayti: ro'yxatdan o'tish, kirish, post yozish, izoh qoldirish, qidiruv va kategoriyalar.

## Quick start

```bash
make run     # creates .venv and .env, installs deps, starts the app
make test    # checks + tests
```

## Imkoniyatlar

- Ro'yxatdan o'tish, kirish, chiqish (`accounts` app)
- Postlar ro'yxati: qidiruv, kategoriya bo'yicha filtr, sahifalash (pagination)
- Post sahifasi: ko'rishlar soni, izohlar
- Post qo'shish faqat kirgan foydalanuvchilar uchun
- Postni faqat uning muallifi tahrirlay va o'chira oladi
- "Mening postlarim" sahifasi
- Admin panel: kategoriyalar, postlar va izohlar
- Bootstrap 5 dizayn

## Ishga tushirish

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

http://127.0.0.1:8000/ — sayt, http://127.0.0.1:8000/admin/ — admin panel (kategoriyalarni shu yerdan qo'shing).

## Tuzilishi

```
accounts/   ro'yxatdan o'tish, login, logout
blog/       Category, Post, Comment modellari va sahifalar
templates/  base.html, accounts/, blog/
config/     sozlamalar
```

## Testlar

```bash
python manage.py test
```
