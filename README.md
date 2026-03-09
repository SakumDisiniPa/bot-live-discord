# 🎵 Discord Music Bot with Lavalink

Bot Discord yang bisa streaming musik dari YouTube, Spotify, dan berbagai sumber lain menggunakan Lavalink server.

## Fitur

✅ Play musik dari YouTube, Spotify, SoundCloud, dll  
✅ Queue management  
✅ Pause/Resume/Skip musik  
✅ Stop dan disconnect  
✅ Join/Leave voice channel  
✅ Show current queue dan lagu sekarang  
✅ High-quality audio streaming dengan Lavalink

## Prasyarat

- Python 3.8+
- Java 11+ (untuk menjalankan Lavalink server)
- Virtual Environment (optional tapi recommended)

## Setup Lavalink Server

### 1. Download Lavalink

```bash
# Download Lavalink
mkdir lavalink
cd lavalink
wget https://github.com/lavalink-devs/Lavalink/releases/download/4.1.7/Lavalink.jar
```

### 2. Buat application.yml

Buat file `application.yml` di folder lavalink:

```yaml
server:
  port: 2333
  address: localhost

lavalink:
  server:
    password: "youshallnotpass"
    sources:
      youtube: true
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      mixer: true
      http: true
      local: false
    filters:
      volume: true
      equalizer: true
      karaoke: true
      timescale: true
      tremolo: true
      vibrato: true
      distortion: true
      rotation: true
      channelmix: true
      lowpass: true
    buffering:
      duration: 400
      thresholdUser: 10
      thresholdDefault: 1

logging:
  file:
    path: ./logs/

metrics:
  prometheus:
    enabled: false
```

### 3. Run Lavalink

```bash
java -jar Lavalink.jar
```

💡 Keep Lavalink running di terminal yang terpisah!

## Setup Bot Discord

### 1. Install Dependencies

```bash
# Navigate ke folder bot
cd bot-live-discord

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Create Discord Bot

1. Buka https://discord.com/developers/applications
2. Click "New Application"
3. Go to "Bot" → "Add Bot"
4. Copy token
5. Edit `bot.py` - ganti `YOUR_DISCORD_BOT_TOKEN_HERE` dengan token Anda
6. Go to "OAuth2" → "URL Generator"
   - Select scopes: `bot`
   - Select permissions: `Send Messages`, `Connect`, `Speak`, `Use Voice Activity`
7. Copy generated URL dan invite bot ke server

### 3. Update Token

Edit `bot.py` dan ganti baris terakhir:
```python
TOKEN = 'YOUR_DISCORD_BOT_TOKEN_HERE'
```

dengan token Anda.

### 4. Run Bot

```bash
python bot.py
```

## Commands

| Command | Deskripsi |
|---------|-----------|
| `s!p <query>` | Play musik dari YouTube/Spotify/SoundCloud dll |
| `s!pause` | Pause musik |
| `s!resume` | Resume musik |
| `s!skip` | Skip ke lagu selanjutnya |
| `s!stop` | Stop dan disconnect |
| `s!join` | Join voice channel Anda |
| `s!leave` | Leave voice channel |
| `s!queue` | Show current queue |
| `s!now` | Show lagu yang sedang diputar |
| `s!help` | Show all commands |

## Cara Pakai

1. Join ke voice channel
2. Ketik salah satu:
   - `s!p https://www.youtube.com/watch?v=...` (YouTube)
   - `s!p song name` (Search di YouTube)
   - `s!p spotify:track:...` (Spotify URI)
3. Bot akan otomatis join dan putar musik
4. Gunakan `s!pause`, `s!resume`, `s!skip`, `s!stop` untuk kontrol

## Troubleshooting

**"Bot tidak bisa connect ke Lavalink"**
- Pastikan Lavalink server running dengan `java -jar Lavalink.jar`
- Check di terminal Lavalink untuk error messages
- Default Lavalink address: `localhost:2333`

**"Audio tidak keluar"**
- Pastikan bot punya permission "Connect" dan "Speak" di server
- Cek Lavalink logs untuk error

**"Lavalink tidak bisa download YouTube"**
- Pastikan internet connection OK
- YouTube blocknya bisa mempengaruhi, coba dengan sumber lain (Spotify, SoundCloud)

**"Module 'wavelink' not found"**
```bash
pip install -r requirements.txt --upgrade
```

## Tips & Customization

- Bisa customize prefix dari `s!` ke yang lain (line 8 di bot.py)
- Bisa tambah fitur polling vote untuk skip, volume control, dll
- Bisa set Lavalink password yang berbeda di `application.yml` dan `bot.py`

## Resources

- [Wavelink Documentation](https://wavelink.dev/)
- [Lavalink Documentation](https://lavalink.dev/)
- [Discord.py Documentation](https://docs.pycord.dev/)

## License

MIT License
