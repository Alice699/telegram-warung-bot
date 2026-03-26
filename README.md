# 🤖 Telegram Warung Bot

Bot Telegram untuk sistem pemesanan warung/UMKM lokal - ekstensi dari [warung-digital](https://github.com/Alice699/warung-digital).

## Fitur

### Pelanggan
- `/start` - Mulai & lihat menu
- `/menu` - Lihat daftar menu berdasarkan kategori
- `/pesan` - Buat pesanan baru (percakapan interaktif)
- `/pesananku` - Riwayat 5 pesanan terakhir
- `/status <id>` - Cek status pesanan realtime

### Admin / Owner
- `/admin` - Panel admin
- `/pesanan_masuk` - Lihat pesanan pending
- Update status pesanan langsung dari Telegram (pending → preparing → ready → done)

## Cara Menjalankan

### 1. Clone & Install
```bash
git clone https://github.com/Alice699/telegram-warung-bot.git
cd telegram-warung-bot

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Setup `.env`
```bash
cp .env.example .env
# Edit .env dan isi BOT_TOKEN dan ADMIN_IDS
```

**Cara dapat BOT_TOKEN:**
1. Buka Telegram, cari `@BotFather`
2. Ketik `/newbot` dan ikuti instruksinya
3. Copy token yang diberikan ke `.env`

**Cara dapat ADMIN_IDS:**
1. Cari `@userinfobot` di Telegram
2. Kirim pesan `/start`
3. Copy ID kamu ke `.env`

### 3. Jalankan
```bash
python main.py
```

## 📁 Struktur Project

```
telegram-warung-bot/
├── main.py              ← Entry point & registrasi handler
├── config.py            ← Konfigurasi dari .env
├── database.py          ← SQLite setup & query
├── handlers/
│   ├── start.py         ← /start & /help
│   ├── menu.py          ← Lihat menu & kategori
│   ├── order.py         ← Alur pemesanan (ConversationHandler)
│   ├── status.py        ← Cek status pesanan
│   └── admin.py         ← Panel admin & update status
├── .env.example
├── requirements.txt
└── .gitignore
```

## Alur Pemesanan

```
/pesan
  → Ketik nama
  → Ketik nomor meja
  → Pilih menu (inline keyboard)
  → Ketik jumlah
  → Tambah lagi / Selesai
  → Konfirmasi
  → ✅ Pesanan masuk!
```

## 🛠️ Tech Stack

- **Python 3.11**
- **python-telegram-bot v21** - Framework bot
- **SQLite** - Database lokal
- **python-dotenv** - Konfigurasi environment

## Terkait

- [warung-digital](https://github.com/Alice699/warung-digital) - REST API versi web

## 👤 Author

**Robbian Saputra Gumay** - [@Alice699](https://github.com/Alice699)

---
> Dibuat dengan ❤️ dari Palembang, South Sumatera 🇮🇩
