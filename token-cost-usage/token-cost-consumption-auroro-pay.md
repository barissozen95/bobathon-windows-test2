# Task 0: First Day (İlk Gün)

macOS'ta M0 kurulumunu baştan sona nasıl tamamladığımın kısa özeti. Kurulum sırasında Claude Code'a sorduğum sorular ve bu session'ın token/maliyet kullanımı da aşağıda.

- **Platform:** macOS (Apple Silicon, Homebrew kurulu)
- **Tarih:** 2026-11-24
- **Session ID:** `1f4e0172-1203-4265-bb5a-8b84d9d36a8a`

## 1. Kurulum adımları (macOS)

### 1.1 İlk deneme: Python sürüm hatası

```bash
python3 setup.py --scanners
```

```
HATA: Python 3.11 veya üzeri gerekli, bulunan: 3.9.
```

macOS ile gelen `python3` 3.9 sürümünde. Proje 3.11 veya üzerini istiyor; kodda `str | None` gibi yeni sözdizimi kullanılıyor.

### 1.2 Yeni Python kurulumu

```bash
brew install python@3.12
/opt/homebrew/bin/python3.12 --version
```

### 1.3 Kurulumu yeni Python ile çalıştırma

```bash
/opt/homebrew/bin/python3.12 setup.py --scanners
```

Alternatif olarak `PYTHON=/opt/homebrew/bin/python3.12 ./setup.sh --scanners` de kullanılabilir.

Bu adım iki sanal ortam oluşturur:
- `.venv`: proje bağımlılıkları (fastapi, uvicorn, pydantic, pytest...)
- `.venv-tools`: Semgrep (M5 için)

> İpucu: Daha önce 3.9 ile oluşturulmuş bir `.venv` varsa önce silin (`rm -rf .venv .venv-tools`), sonra kurulumu tekrar çalıştırın.

### 1.4 Doğrulama

```bash
python3 verify/run.py m0
```

```
=== M0 Kurulum ===
7 passed in 7.11s
[PASS] Python 3.11 veya uzeri
[PASS] Bagimliliklar kurulu (fastapi, pytest, httpx, yaml)
[PASS] Aurora Core uygulamasi ayaga kalkiyor (/health)
[PASS] Gorev dosyalari yerinde (docs, fixtures, deploy)
[PASS] Git kurulu ve klasor bir git deposu
[PASS] semgrep kurulu (M5 icin)
[PASS] Bob Shell (bob komutu) kurulu (M2 icin)

M0 Kurulum: PASS  7/7 kontrol  [7.3s]
```

Bu çıktı eğitmene gönderilir.

## 2. Claude Code'a sorulan sorular

| # | Soru | Kısa cevap |
|---|---|---|
| 1 | `setup.py` "Python 3.11 gerekli" hatası veriyor, nasıl çözerim? | `brew install python@3.12`, ardından kurulumu `/opt/homebrew/bin/python3.12` ile çalıştır. |
| 2 | Bu uygulama hakkında bilgi verir misin? | Bob'u öğretmek için hazırlanmış 4 saatlik bir atölye. Senaryo: Aurora Bank'ta FastAPI ile yazılmış bir bankacılık servisi. M0–M8 arası 9 görev var, her biri bir Bob özelliğini gösteriyor. |
| 3 | `services/core` içinde kaç endpoint, kaç satır kod var? | 7 endpoint (hepsi `main.py` içinde). 201 satır; boş satır ve yorumlar hariç ~148. |
| 4 | Repoda toplam kaç satır kod var? | Toplam 5.917 satır; kod ~3.000. Python 2.302 satır, bunun 1.497'si `verify/` testleri. |
| 5 | Bu session'da kaç token, ne kadar süre, hangi model kullanıldı? | Aşağıdaki "Kullanım" bölümü. |
| 6 | Maliyeti de ekleyip bir dosyada tut. | Bu dosya. |

### Endpoint'ler (`services/core/main.py`)

| Metot | Yol |
|---|---|
| GET | `/health` |
| POST | `/accounts` |
| GET | `/accounts/{account_id}` |
| POST | `/transfers` |
| GET | `/transfers/{transfer_id}` |
| GET | `/reports/transfers` |
| POST | `/reports/archive` |

## 3. Kullanım: token ve maliyet

Kaynak: `~/.claude/projects/-Users-barissozen-bobathon-auroro-pay2/1f4e0172-1203-4265-bb5a-8b84d9d36a8a.jsonl`

### Süre

| | Saat (yerel, UTC+3) |
|---|---|
| Başlangıç | 09:38:23 |
| Son kayıt | 09:54:11 |
| **Toplam** | **~15 dk 48 sn** |

### Model

| Model | API çağrısı |
|---|---|
| Claude Opus 5.5 (`claude-opus-5-5`) | 14 |

### Token kullanımı ve maliyet

Fiyatlar: Opus 5.5, Anthropic API listesi, 1M token başına.

| Tür | Token | Birim fiyat | Maliyet |
|---|---:|---:|---:|
| Input (önbelleksiz) | 38 | $4.00 | $0.0002 |
| Output | 6.369 | $20.00 | $0.1274 |
| Cache yazma (1 saat TTL) | 27.456 | $8.00 | $0.2196 |
| Cache okuma | 663.709 | $0.20 | $0.1327 |
| **Toplam** | **697.572** | | **~$0.48** |

### Notlar

- Token'ların yaklaşık %95'i cache okuma. Konuşma her mesajda modele yeniden gönderiliyor, ancak önbellekten okunduğu için input fiyatının yalnızca 1/20'si ödeniyor.
- En büyük maliyet kalemi cache yazma (%46). Claude Code 1 saatlik önbellek kullanıyor ve bu önbelleğin yazma fiyatı normal input fiyatının 2 katı.
- Maliyet API liste fiyatıyla hesaplanmış tahmini bir değerdir. Claude Pro/Max aboneliği ile kullanılıyorsa ayrıca ücret ödenmez; kullanım abonelik limitinden düşer.
- Rakamlar 6. soruya kadar olan kısmı kapsar. Canlı değer için Claude Code içinde `/cost` yazın.
