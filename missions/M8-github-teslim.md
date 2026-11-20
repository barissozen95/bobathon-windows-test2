# M8 - GitHub'a teslim: dal, commit, push, PR

**Süre:** 15 dk | **Bob özelliği:** Bob ile **Git iş akışı** (commit mesajı, push, Pull Request)

> macOS/Linux'ta `python3`, Windows'ta `py` yazın.

## Durum

İş bitti. Şimdi ekibin kuralıyla teslim zamanı: [`docs/ENGINEERING-HANDBOOK.md`](../docs/ENGINEERING-HANDBOOK.md) bölüm 6.
Template'ten oluşturduğunuz **kendi GitHub reponuz** (M0) hedef.

## Teslim edilecekler

- Dal adı `feature/<kısa-ad>` veya `fix/<kısa-ad>`, `main`'den açıldı (M0'da açtıysanız hazır)
- Çalışma dizini temiz
- `main`'den sonra en az **3 anlamlı commit** (İngilizce, ne yaptığını anlatan tek cümle, en az 12 karakter)
- Dal `origin`'e push edildi
- Açık bir PR: başlık en az 10, açıklama en az 80 karakter, şablon dolu, en az bir kutu işaretli (`- [x]`)
- PR üzerindeki CI yeşil (testler + kapsam %85 + Semgrep)
- `verify m8` PASS (`gh` yoksa SKIP ve PR sayfası eğitmene gösterildi)

## Adım 1 - Çalışma dizinini temizleyin

Commit edilmemiş dosya kalmamalı:

```bash
git status --short
```

> **Sık takılanlar:**
> - `.vscode/` klasörü depoda yok sayılır; yine de listede görünürse commit etmeyin.
> - `limits-service-plan.md`: M1'de Plan modunda Bob'un oluşturduğu plan dosyası. Ya commit edin ya silin.
> - `reports/bob-run.json` yok sayılır; commit etmenize gerek yok.

## Adım 2 - Dal ve commit'ler

Bob'a dalı açtırın (M0'da açtıysanız mevcut dalı kullanın) ve işinizi **görev başına bir commit** olacak şekilde kaydettirin. Kuralları siz yazmayın: Bob'a el kitabı bölüm 6'yı okutup uymasını söyleyin. Örnek mesaj: `Add limits service from PRD`. `update`, `fix`, `wip` gibi tek kelimelik mesajlar kabul edilmez.

Elle yapmak isterseniz:

```bash
git switch -c feature/<kısa-ad>
```

```bash
git add -A
```

```bash
git commit -m "<ne yaptığınızı anlatan tek cümle>"
```

## Adım 3 - Push ve Pull Request

Bob'a dalı `origin`'e push ettirin ve **Pull Request** açtırın. Başlık ve açıklamayı Bob, değişikliklere bakarak yazsın; [`.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md) doldurulsun, işaretleyebildiğiniz kutuları işaretleyin.

```bash
git push -u origin HEAD
```

**GitHub MCP bağlantısı hata verirse** `gh` ile devam edin:

```bash
gh pr create --title "<başlık>" --body "<PR şablonuna göre açıklama>"
```

- İlk PR'da Bob GitHub yetkilendirmesi isteyebilir. `gh` kuruluysa onay penceresi olmadan açabilir.
- `gh` kurulu değilse PR ve CI kontrolleri **SKIP** görünür; PR sayfasını eğitmene gösterin.
- CI kırmızıysa log çıktısını Bob'a gösterin. Sık nedenler: kapsam %85'in altında, Semgrep bulgusu.

## Adım 4 - Doğrulama

Sonucu doğrulamak için aşağıdaki komutu kullanabilirsiniz:

```bash
python3 verify/run.py m8
```

`gh` kuruluysa CI durumunu izlemek için:

```bash
gh pr checks --watch
```

## Keşif noktaları

- Bob `git push` ve `gh pr create` öncesi sizden onay istedi mi? Hangi komutlara "bu görev için onayla" demek mantıklı?
- Commit'leri tek tek mi, hepsini birden mi kaydettirdiniz? Hangisi PR incelemesini kolaylaştırır?
- Push edilen dosyalar arasında olmaması gereken bir şey var mı? (`.bobignore` ve gizli bilgiler)

## İpucu

- **İpucu 1:** Teslim işin bir parçasıdır. Commit'leri tek parça yapmayın.
- **İpucu 2:** `origin` yoksa M0'da template'ten kendi reponuzu oluşturup klonlamamışsınız demektir. Çalışma dizini kirliyse `git status --short` neyin kaldığını gösterir. "main'den sonra 3 commit" sayılmıyorsa commit'leri `main`'e değil dalınıza attığınızdan emin olun. CI hiç başlamıyorsa repo sayfasında Actions'ın etkin olduğuna bakın.
- **Eğitmenden yardım:** İpucu 2 yetmediyse eğitmeni çağırın.
