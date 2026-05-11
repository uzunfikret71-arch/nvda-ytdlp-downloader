# NVDA Add-on Store başvuru notları

Bu dosya mağaza başvurusu doldurulurken kullanılacak değerleri özetler.

- Name: `ytdlpDownloader`
- Display name: `yt-dlp video ve ses indirici`
- Version: `1.0.0`
- Author: `Fikret Uzun`
- Minimum NVDA version: `2025.3.3`
- Last tested NVDA version: `2025.3.3`
- Source URL: `https://github.com/uzunfikret71-arch/nvda-ytdlp-downloader`
- Download URL: `https://github.com/uzunfikret71-arch/nvda-ytdlp-downloader/releases/download/v1.0.0/ytdlpDownloader-1.0.0.nvda-addon`
- SHA256: `0063A3D361A84360DBBF8902CC3298AE009F095071D944EF0DD5A55B7A5AD0C9`

## Açıklama

NVDA içinden yt-dlp ve FFmpeg kullanarak video veya ses indirmeyi sağlar. Ses indirmelerinde medya bilgisi ve kapak görseli ekleme seçenekleri sunar.

## Güvenlik ve bütünlük notu

Eklenti paket içinde `yt-dlp.exe`, `ffmpeg.exe`, `ffprobe.exe` ve `deno.exe` taşır. İndirme penceresi ilk açıldığında paket içindeki `yt-dlp.exe -U` komutu otomatik olarak çalışır. Bu güncelleme kontrolü başarısız olursa indirme özelliği kullanılabilir kalır ve hata günlük alanında gösterilir.

NVDA Add-on Store SHA256 bütünlüğü yayımlanan `.nvda-addon` dosyası için geçerlidir. `yt-dlp.exe` çalışma zamanında kendini güncelleyebildiği için bu davranış başvuruda açıkça belirtilmelidir.

## Yayın öncesi tamamlanacaklar

- GitHub repo ve release bağlantıları yayınlandıktan sonra tarayıcıdan doğrulanacak.
- `yt-dlp.exe --version` bu ortamda PyInstaller çıkarma izni hatasıyla başarısız oluyor: `Failed to extract ... __mypyc.cp310-win_amd64.pyd`. Bu düzeltilmeden veya temiz bir kullanıcı ortamında doğrulanmadan mağaza yayını yapılmamalıdır.
