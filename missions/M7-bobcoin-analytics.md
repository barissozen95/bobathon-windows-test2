# M7 - Bobcoin, Bob Admin ve Bobalytics: harcamayı görün

**Süre:** 15 dk | **Bob özelliği:** **Bobcoin** tüketimi, **Bob Admin** portalı, **Bobalytics**, `--max-cost`

> macOS/Linux'ta `python3`, Windows'ta `py` yazın.

## Durum

Ekip lideri Bob'u tüm ekibe açmak istiyor ama CFO soruyor: "Bu iş bize kaça mal oluyor, nereden izleyeceğiz?"
Bu görev kod değil, **ölçüm ve karar** görevi.

## Teslim edilecekler

- `reports/bob-run.json`: `bob run --format json` çıktısı, geçerli JSON
- Aynı iş farklı sınırla bir kez daha çalıştırıldı ve karşılaştırıldı
- `reports/bobcoin-notes.md` (en az ~200 karakter): "Bobcoin" ifadesi, **gerçek rakamlar**, rakamların kaynağı (portal / Bobalytics / `stats`) ve bir `--max-cost` / `--max-turns` önerisi
- `verify m7` PASS

## Adım 1 - Sınırlı bir iş çalıştırın ve ölçün

Küçük bir işi (ör. `services/core`'daki bir modülü açıklatmak) Bob Shell ile **maliyet ve tur sınırı koyarak**, çıktıyı JSON alarak çalıştırın. macOS/Linux:

```bash
bob run --format json --max-cost <bobcoin> --max-turns <n> "<küçük bir iş>" > reports/bob-run.json
```

Windows (PowerShell; `>` dosyayı UTF-16 yazabilir, bu yüzden `Out-File` kullanın):

```powershell
bob run --format json --max-cost <bobcoin> --max-turns <n> "<küçük bir iş>" | Out-File -Encoding utf8 reports/bob-run.json
```

Çıktıdaki `stats` bölümüne bakın: kaç tur sürdü, ne kadar tüketildi? **Anlık rakamları buradan alabilirsiniz.** Sonra aynı işi sınırı değiştirerek bir kez daha çalıştırın.

> **`--max-cost` çalışan bir turu durdurmayabilir.** Sınır tur sınırlarında değerlendirilir; devam eden bir tur bütçeyi aşabilir. `--max-turns` ile birlikte kullanın.

## Adım 2 - Portaldan ve Bobalytics'ten okuyun, karar yazın

- **Bob Admin** (`https://bob.ibm.com/admin`): kalan bakiyeniz ve kullanım detayınız.
- **Bobalytics** (yetkiniz varsa): **Metrics** sekmesi (Adoption, Bob factor, Bobcoin spend) ve **Insights**.
- Yetkiniz yoksa eğitmen ekranını paylaşır.

> **Bobalytics gecikmelidir ve UTC gösterir.** Veriler her 60 dakikada bir yenilenir; az önce yaptığınız çalıştırma henüz görünmeyebilir. Anlık sayılar için `bob-run.json` içindeki `stats` bölümünü kullanın ve notunuzda kaynağı belirtin.

Gördüklerinizi `reports/bobcoin-notes.md` dosyasına yazın: gördüğünüz **rakamlar**, nereden okuduğunuz ve bu iş için hangi `--max-cost` / `--max-turns` değerini önerdiğiniz. Rakamı gördüğünüz yerden yazın, tahmin etmeyin.

> **Ekran görüntülerini anonimleştirin.** Portal veya Bobalytics görüntüsü paylaşacaksanız ad, e-posta ve kimlikleri önce gizleyin.

## Adım 3 - Doğrulama

Sonucu doğrulamak için aşağıdaki komutu kullanabilirsiniz:

```bash
python3 verify/run.py m7
```

JSON dosyası boşsa `--format json` kullandığınızı ve çıktıyı dosyaya yönlendirdiğinizi kontrol edin.

## Keşif noktaları

- Bobcoin neye göre tükeniyor? Uzun bir sohbetle yeni açılmış bir sohbet arasında fark var mı?
- MCP sunucuları ve büyük bağlam harcamayı nasıl etkiler?
- Bobalytics'te **Bob factor** neyi ölçüyor? Bu metrik sizi neden ikna ederdi ya da etmezdi?
- Admin olarak bir kullanıcıya harcama limiti koymak ile her çalıştırmaya `--max-cost` koymak aynı şey mi?

## İpucu

- **İpucu 1:** Bu görev ölçüm. Rakamı gördüğünüz yerden yazın. İki farklı sınırla çalıştırırsanız karşılaştırma yapabilirsiniz.
- **İpucu 2:** Seçenekler için `bob run --help`. `reports/` klasörü hazır. Uzun sohbetler her mesajda tüm bağlamı yeniden gönderdiği için daha pahalıdır; görev değişince yeni sohbet açmak maliyeti düşürür.
- **Eğitmenden yardım:** İpucu 2 yetmediyse eğitmeni çağırın.
