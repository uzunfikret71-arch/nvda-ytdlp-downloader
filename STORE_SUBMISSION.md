# NVDA Add-on Store başvuru notları

Bu dosya mağaza başvurusu doldurulurken kullanılacak değerleri özetler.

- Name: `ytdlpDownloader`
- Display name: `Video ve ses indirici`
- Version: `1.1.1`
- Author: `Fikret Uzun`
- Minimum NVDA version: `2025.3.3`
- Last tested NVDA version: `2026.1.1`
- Source URL: `https://github.com/uzunfikret71-arch/nvda-ytdlp-downloader`
- Download URL: `https://github.com/uzunfikret71-arch/nvda-ytdlp-downloader/releases/download/v1.1.1/ytdlpDownloader-1.1.1.nvda-addon`
- SHA256: `45498C44074A469CAFA8EE7416061C6EDF7E91B40B8411C160C40DD0F23F3690`
- License: `GPL v2 or later`
- License URL: `https://www.gnu.org/licenses/gpl-2.0.html`

## Açıklama

NVDA içinden yt-dlp ve FFmpeg kullanarak video veya ses indirmeyi sağlar. Ses indirmelerinde medya bilgisi ve kapak görseli ekleme seçenekleri sunar.

## Güvenlik ve bütünlük notu

Eklenti paket içinde `yt-dlp.exe`, `ffmpeg.exe` ve `deno.exe` taşır. `deno.exe`, bazı yt-dlp çıkarıcılarının JavaScript çalıştırma desteği için gerekebileceğinden bağımlılık olarak tutulur. `ffprobe.exe` kullanılmadığı için yayın paketine dahil edilmez.

Eklenti açılışta otomatik güncelleme veya ağ isteği başlatmaz. Kullanıcı indirme penceresindeki `yt-dlp güncelle` düğmesini seçtiğinde, eklenti internet bağlantısı kullanılacağını ve paket içindeki `yt-dlp.exe` dosyasının güncellenebileceğini açıkça bildirip onay ister. Kullanıcı onay verirse `yt-dlp.exe -U` çalıştırılır. Güncelleme başarısız olursa indirme özelliği kullanılabilir kalır ve hata günlük alanında gösterilir.

NVDA Add-on Store SHA256 bütünlüğü yayımlanan `.nvda-addon` dosyası için geçerlidir. Kullanıcı onaylı `yt-dlp` güncellemesi çalışma zamanında paket içindeki `yt-dlp.exe` dosyasını değiştirebilir; bu davranış başvuruda açıkça belirtilmelidir.

## Yayın öncesi tamamlanacaklar

- Yayın paketi yeniden üretildi.
- Yeni SHA256 değeri bu dosyaya ve mağaza başvurusuna eklendi.
- GitHub repo ve release bağlantıları doğrulandı.
- `yt-dlp.exe --version`, `ffmpeg.exe -version` ve `deno.exe --version` temiz bir kullanıcı ortamında doğrulanacak.
