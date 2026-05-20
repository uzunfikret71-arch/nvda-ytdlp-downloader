# Üçüncü taraf bileşenler

Bu eklenti, kullanıcı kurulumu kolay olsun diye bazı komut satırı araçlarını paket içinde taşır.

## yt-dlp

- Dosya: `.addon/bin/yt-dlp.exe`
- Proje: https://github.com/yt-dlp/yt-dlp
- Paketlenen sürüm: `2026.03.17`
- Lisans: The Unlicense
- Not: Güncelleme otomatik çalışmaz. Kullanıcı `yt-dlp güncelle` düğmesini seçip onay verirse `yt-dlp.exe -U` çalıştırılır.

## FFmpeg

- Dosya: `.addon/bin/ffmpeg.exe`
- Proje: https://ffmpeg.org/
- Paketlenen yapı: `N-124279-g0f6ba39122-20260430`
- Lisans: Paketlenen Windows yapısı GPL etkin derlenmiştir. Ayrıntılar kaynak dağıtımdaki `ffmpeg/ffmpeg-N-124279-g0f6ba39122-win64-gpl/LICENSE.txt` dosyasındadır.

## Deno

- Dosya: `.addon/bin/deno.exe`
- Proje: https://deno.com/
- Paketlenen sürüm: `2.7.14`
- Lisans: MIT
- Not: Bazı yt-dlp çıkarıcıları JavaScript çalıştırma desteği için Deno kullanabilir. Bu nedenle paket bağımlılığı olarak tutulur.
