# Değişiklik günlüğü

## 1.2.1 - 2026-08-26

- Yayın paketi dosya adı `Video-ve-Ses-Indirici-1.2.1.nvda-addon` olarak değiştirildi.
- Oynatma listesi davranışı değiştirilmeden korundu.
- WebM hariç otomatik ses seçimi gerçekten `ext!=webm` ile sınırlandı; bu seçimde ses çıkarma veya biçim dönüştürme işlemi kaldırıldı.
- Kapak görseli ön denetimi indirilecek kaynak ses kapsayıcısını kontrol edecek şekilde eşitlendi. Desteklenmeyen bir kapsayıcı algılanırsa kullanıcıya kapaksız devam etme seçeneği sunulur.
- Ön denetimde alınan bilgi asıl indirmede yeniden kullanılarak oynatma listesinin ağ üzerinden iki kez çözümlenmesi önlendi.
- İndirme veya güncelleme sürerken bütün ayar denetimleri kilitlenir.
- Kullanıcı adresleri yt-dlp seçeneklerinden güvenli biçimde ayrıldı.
- Otomatik ses seçiminde medya bilgisi uyumluluğu da kaynak kapsayıcısına göre denetlenir.
- Ağ/site hataları, uygun ses biçimi bulunamaması ve eksik oynatma listesi öğeleri ayrı uyarılarla gösterilir.
- Açık MP4 ve WebM seçimlerinde uyumsuz akışların birleştirilmeye çalışılması önlendi.
- Eklenti adı ve açıklamaları belgeler arasında tutarlı hâle getirildi.
- Eklenti lisansı ve üçüncü taraf bildirimleri oluşturulan pakete eklendi.

## 1.2.0 - 2026-08-26

- Oynatma listesi bağlantılarındaki tüm öğelerin indirilmesi sağlandı.
- Oynatma listesi öğelerine dosya adında sıra numarası eklendi.

## 1.1.1 - 2026-08-13

- Eklentinin yüklenmesini engelleyen bozuk Python kaynak yapısı düzeltildi.
- İndirme klasörü kalıcı olarak kaydedilip sonraki açılışlarda geri yükleniyor.
- Pencere ve menü adı `Video ve Ses İndirici` olarak sadeleştirildi.
- Aynı anda birden fazla pencere veya işlem başlatılması engellendi.
- Pencere kapanışı ve çalışan alt süreçlerin sonlandırılması kararlı hâle getirildi.
- Video ve ses biçimi komutları ile hata kontrolleri iyileştirildi.

## 1.1.0 - 2026-06-04

- Ses ve video indirme seçeneklerine orijinal en iyi kalite seçenekleri eklendi.
- Manifest son test edilen NVDA sürümü `2026.1.1` olacak şekilde güncellendi.
- Yayın paketi `ytdlpDownloader-1.1.0.nvda-addon` olarak yayımlandı.

## 1.0.1 - 2026-06-01

- Yayın paketi ve mağaza başvuru bilgileri `1.0.1` sürümü için güncellendi.
- Paketleme çıktısı ve SHA256 bütünlük bilgisi yenilendi.

## 1.0.0 - 2026-05-11

- İlk NVDA Add-on Store hazırlık sürümü.
- NVDA içinden video ve ses indirme penceresi eklendi.
- Paket içi yt-dlp, FFmpeg ve Deno desteği eklendi.
- yt-dlp güncellemesi otomatik açılış kontrolü yerine kullanıcı onaylı `yt-dlp güncelle` düğmesine taşındı.
- Kullanılmayan `ffprobe.exe` yayın paketinden çıkarılacak şekilde paketleme notları güncellendi.
- Yayın paketi temizleme ve SHA256 üretme betiği eklendi.
