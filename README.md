# yt-dlp video ve ses indirici

NVDA içinden yt-dlp ve FFmpeg kullanarak video veya ses indirmeyi sağlayan bir NVDA eklentisi.

## Özellikler

- NVDA Araçlar menüsünden veya `NVDA+Shift+Y` kısayoluyla indirme penceresini açar.
- Video indirmeleri için `mp4`, `mkv` ve `webm` çıktı seçenekleri sunar.
- Ses indirmeleri için `mp3`, `m4a`, `opus`, `flac` ve `wav` çıktı seçenekleri sunar.
- Ses dosyalarına medya bilgisi ve kapak görseli ekleme seçenekleri sağlar.
- Paket içinde `yt-dlp.exe`, `ffmpeg.exe`, `ffprobe.exe` ve `deno.exe` bulunur.

## Otomatik yt-dlp güncellemesi

İndirme penceresi ilk açıldığında eklenti paket içindeki `yt-dlp.exe -U` komutuyla güncelleme kontrolü yapar. Kontrol başarısız olursa durum günlük alanında gösterilir ve indirme özelliği kullanılabilir kalır.

Bu davranış, NVDA Add-on Store başvurusunda açıkça belirtilmelidir çünkü mağaza paketi SHA256 bütünlüğüyle doğrulanırken `yt-dlp.exe` çalışma zamanında kendini güncelleyebilir.

## Kurulum

1. `dist/ytdlpDownloader-1.0.0.nvda-addon` dosyasını NVDA ile açın.
2. NVDA'nın eklenti kurulum uyarılarını onaylayın.
3. NVDA yeniden başlatıldıktan sonra Araçlar menüsünden `yt-dlp ile video veya ses indir...` öğesini kullanın.

## Paketleme

Yayın paketini yeniden üretmek ve SHA256 değerini almak için:

```powershell
.\scripts\package.ps1
```

Betik `.addon` içeriğini temiz bir geçici klasöre kopyalar, `__pycache__` klasörlerini dışarıda bırakır, `dist/ytdlpDownloader-1.0.0.nvda-addon` paketini üretir ve SHA256 değerini yazar.

## Yayın durumu

Kaynak repo URL'si:

https://github.com/uzunfikret71-arch/nvda-ytdlp-downloader

## Lisans

Bu eklenti `GPL-3.0-or-later` lisansı ile dağıtılır. Üçüncü taraf bileşenler için `THIRD_PARTY_NOTICES.md` dosyasına bakın.
