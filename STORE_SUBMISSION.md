# NVDA Add-on Store başvuru notları

Bu dosya mağaza başvurusu doldurulurken kullanılacak değerleri özetler.

- Name: `ytdlpDownloader`
- Display name: `Video ve Ses İndirici`
- Version: `1.2.1`
- Author: `Fikret Uzun`
- Minimum NVDA version: `2025.3.3`
- Last tested NVDA version: `2026.1.1`
- Source URL: `https://github.com/uzunfikret71-arch/nvda-ytdlp-downloader`
- Download URL: `https://github.com/uzunfikret71-arch/nvda-ytdlp-downloader/releases/download/v1.2.1/ytdlpDownloader-1.2.1.nvda-addon`
- Yerel yayın adayı SHA256: `74219F991027F0A4CAA1A6E7543BD326168B68CF5BCCCC882AE3096D3EE17B09`
- License: `GPL v2 or later`
- License URL: `https://www.gnu.org/licenses/gpl-2.0.html`

## Açıklama

NVDA içinden tek videoları ve oynatma listelerini video veya ses olarak indirmeyi sağlar. Ses indirmelerinde medya bilgisi ve desteklenen biçimlerde kapak görseli ekleme seçenekleri sunar.

## Güvenlik ve bütünlük notu

Eklenti paket içinde `yt-dlp.exe`, `ffmpeg.exe` ve `deno.exe` taşır. `deno.exe`, bazı yt-dlp çıkarıcılarının JavaScript çalıştırma desteği için gerekebileceğinden bağımlılık olarak tutulur. `ffprobe.exe` kullanılmadığı için yayın paketine dahil edilmez.

Eklenti açılışta otomatik güncelleme veya ağ isteği başlatmaz. Kullanıcı indirme penceresindeki `yt-dlp güncelle` düğmesini seçtiğinde, eklenti internet bağlantısı kullanılacağını ve paket içindeki `yt-dlp.exe` dosyasının güncellenebileceğini açıkça bildirip onay ister. Kullanıcı onay verirse `yt-dlp.exe -U` çalıştırılır. Güncelleme başarısız olursa indirme özelliği kullanılabilir kalır ve hata günlük alanında gösterilir.

NVDA Add-on Store SHA256 bütünlüğü yayımlanan `.nvda-addon` dosyası için geçerlidir. Kullanıcı onaylı `yt-dlp` güncellemesi çalışma zamanında paket içindeki `yt-dlp.exe` dosyasını değiştirebilir; bu davranış başvuruda açıkça belirtilmelidir.

## 1.2.1 yayın hazırlığı

- `1.2.1` yayın paketi üretildi ve paket içindeki manifest sürümü doğrulandı.
- GitHub indirme adresi eklendi; yayımlanan dosyanın SHA256 değeri yerel paketle karşılaştırılacak.
- `yt-dlp.exe --version`, `ffmpeg.exe -version` ve `deno.exe --version` çalıştırılarak paketlenen sürümler doğrulandı.
