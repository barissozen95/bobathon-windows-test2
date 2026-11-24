# Bobcoin notları - M7

**Tarih:** 24.11.2026, çalıştırmalar 09:05-09:08 UTC
**Araç:** Bob Shell 2.1.0, `bob run --format json --mode ask --disable-mcp`
**CFO sayfası:** `reports/bob-limits/cfo-bobcoin-raporu.html`

## Rakamların kaynağı

Bütün rakamlar her çalıştırmanın JSON çıktısındaki `stats` bölümünden alındı: `stats.session_costs` (Bobcoin), `stats.tool_calls`, `stats.duration_ms`. Ham çıktılar `reports/bob-limits/run-*.json`, özet `reports/bob-limits/summary.json` dosyasında. Teslim edilen çalıştırma `reports/bob-run.json` (`balanced` senaryosu).

Bu rakamlar **Bob Admin portalından veya Bobalytics'ten okunmadı.** Bobalytics 60 dakika gecikmeli çalışıyor ve UTC gösteriyor, bu yüzden bu çalıştırmalar orada henüz görünmeyebilir. Kalan bakiye ve faturalanan tutar için Bob Admin portalı (`https://bob.ibm.com/admin`) esas alınmalı. Portal rakamları buraya ayrıca eklenmeli.

## Ölçülen tüketim

### Küçük iş: `services/core/fees.py` modülünü açıklatma

| Senaryo | --max-cost | --max-turns | Sonuç | Bobcoin | Araç çağrısı | Süre |
|---|---|---|---|---|---|---|
| tight | 0.05 | 2 | tamamlandı | 0.0424 | 1 | 9.4 sn |
| lowturn | 2 | 2 | tamamlandı | 0.0422 | 1 | 7.5 sn |
| lowcost | 0.10 | 10 | tamamlandı | 0.0424 | 1 | 9.0 sn |
| balanced | 0.50 | 6 | tamamlandı | 0.0425 | 1 | 9.8 sn |
| loose | 2 | 15 | tamamlandı | 0.0425 | 1 | 9.1 sn |

Maliyet beş senaryoda da 0.0422 ile 0.0425 Bobcoin arasında kaldı. Hiçbir sınır devreye girmedi.

### Büyük iş: `services/core` altındaki tüm modüller + `tests/` kapsam tablosu

| Senaryo | --max-cost | --max-turns | Sonuç | Bobcoin | Araç çağrısı | Süre |
|---|---|---|---|---|---|---|
| heavy-turncap | 5 | 2 | 2 turda kesildi, cevap 49 karakter | 0.0415 | 4 | 4.6 sn |
| heavy-costcap | 0.05 | 20 | tavanda kesildi, cevap yarım | 0.0664 | 7 | 7.3 sn |
| heavy-loose | 5 | 30 | tamamlandı | 0.3361 | 20 | 39.4 sn |

## Gözlemler

1. **`--max-cost` kesin bir tavan değil.** 0.05 tavanlı işte gerçek harcama 0.066 Bobcoin oldu (%33 aşım). Bob şu mesajı yazdı: `The task reached the cost limit of 0.050 (spent: 0.066).` Tavan tur bitince kontrol ediliyor.
2. **Sınıra takılan iş başarılı görünüyor.** Kesilen iki çalıştırmada da çıkış kodu 0 ve `status: "success"` döndü. Kesildiğini yalnızca JSON'daki ayrı `"type":"error"` satırı gösteriyor. CI veya raporlama bu satırı kontrol etmeli.
3. **Çok dar sınır boşa harcama demek.** Büyük işte 2 tur sınırı 0.042 Bobcoin harcatıp kullanılamaz bir cevap üretti.
4. Büyük iş küçük işin yaklaşık 8 katı tutuyor (0.336 / 0.042).

## Bütçe önerisi

| İş tipi | Öneri | Gerekçe |
|---|---|---|
| Küçük iş (tek modül açıklama, kısa soru) | `--max-cost 0.10 --max-turns 5` | Ölçülen 0.042'nin 2.4 katı pay; %33 aşımla en fazla ~0.13 Bobcoin |
| Büyük iş (çok dosyalı analiz) | `--max-cost 0.50 --max-turns 30` | Ölçülen 0.336'nın 1.5 katı pay; %33 aşımla en fazla ~0.67 Bobcoin |

`--max-cost` her zaman `--max-turns` ile birlikte verilmeli. Bütçe planında tavanın 1.33 katı esas alınmalı.

## Sınırlar

Örneklem küçük: 8 çalıştırma, 2 iş tipi. Büyük iş rakamı tek bir tamamlanmış çalıştırmaya dayanıyor ve birkaç tekrarla doğrulanmalı. Bobcoin'in TL karşılığı bu notlara dahil değil; sözleşme oranı Bob Admin'den alınmalı.
