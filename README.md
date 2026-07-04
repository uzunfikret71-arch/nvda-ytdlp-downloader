# yt-dlp video ve ses indirici

NVDA içinden yt-dlp ve FFmpeg kullanarak video veya ses indirmeyi sağlayan bir NVDA eklentisi.

## Özellikler

- NVDA Araçlar menüsünden veya `NVDA+Shift+Y` kısayoluyla indirme penceresini açar.
- Video indirmeleri için `mp4`, `mkv` ve `webm` çıktı seçenekleri sunar.
- Ses indirmeleri için `mp3`, `m4a`, `flac` ve `wav` çıktı seçenekleri sunar.
- Ses dosyalarına medya bilgisi ve kapak görseli ekleme seçenekleri sağlar.
- Yayın paketi içinde `yt-dlp.exe`, `ffmpeg.exe` ve `deno.exe` bulunur.

## yt-dlp güncellemesi

yt-dlp sık güncellenen bir araç olduğu için bazı sitelerde indirme desteğinin korunması amacıyla eklenti içinden güncelleme yapılabilir.

Güncelleme otomatik çalışmaz. Kullanıcı indirme penceresindeki `yt-dlp güncelle` düğmesini seçtiğinde eklenti internet bağlantısı ve paket içindeki `yt-dlp.exe` dosyasının güncellenebileceği hakkında onay ister. Kullanıcı onay verirse `yt-dlp.exe -U` çalıştırılır. Güncelleme başarısız olursa durum günlük alanında gösterilir ve indirme özelliği kullanılabilir kalır.

## Kurulum

1. `ytdlpDownloader-1.1.0.nvda-addon` dosyasını son GitHub yayınından indirin.
2. İndirilen `.nvda-addon` dosyasını NVDA ile açın.
3. NVDA'nın eklenti kurulum uyarılarını onaylayın.
4. NVDA yeniden başlatıldıktan sonra Araçlar menüsünden `yt-dlp ile video veya ses indir...` öğesini kullanın.

## Paketleme

Yayın paketini yeniden üretmek ve SHA256 değerini almak için:

```powershell
.\scripts\package.ps1
```

Betik `.addon` içeriğini temiz bir geçici klasöre kopyalar, `__pycache__` klasörlerini ve kullanılmayan `ffprobe.exe` dosyasını dışarıda bırakır, `dist/ytdlpDownloader-1.1.0.nvda-addon` paketini üretir ve SHA256 değerini yazar.

Yayın paketi üretmeden önce `.addon\bin` klasöründe şu dosyaların bulunduğundan emin olun:

- `yt-dlp.exe`
- `ffmpeg.exe`
- `deno.exe`

## Yayın durumu

Kaynak repo URL'si:

https://github.com/uzunfikret71-arch/nvda-ytdlp-downloader

Son yayın:

https://github.com/uzunfikret71-arch/nvda-ytdlp-downloader/releases/tag/v1.1.0

## Lisans

Bu eklenti `GPL-2.0-or-later` lisansı ile dağıtılır. Üçüncü taraf bileşenler için `THIRD_PARTY_NOTICES.md` dosyasına bakın.
