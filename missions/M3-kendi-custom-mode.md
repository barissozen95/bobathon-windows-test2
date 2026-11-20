# M3 - Kendi custom mode'unuzu yazın (Mode + Rules + Skill)

**Süre:** 20 dk | **Bob özelliği:** **Custom Mode**, **Rules**, **Skills**

> macOS/Linux'ta `python3`, Windows'ta `py` yazın.

## Durum

M2'yi bitirdiniz ama code review'da ekip lideri aynı yorumu üçüncü kez yazdı: "Bob yine el kitabını çiğnedi."
Bob her yeni sohbette **sıfırdan başlıyor**. Ekibin tek kaynağı [`docs/ENGINEERING-HANDBOOK.md`](../docs/ENGINEERING-HANDBOOK.md).

Hedef, **tek bir persona** kurmak: yalnızca test yazan ve çalıştıran bir **QA Engineer**. Bu mod kendi kurallarını ve kendi skill'ini yanında taşır.

## Teslim edilecekler

- `.bob/custom_modes.yaml` içinde yeni bir mod: `read` + `execute` + yalnızca `tests/` için kısıtlı `edit`
- `.bob/rules/` (veya `.bob/rules-<slug>/`) altında el kitabını özetleyen kural dosyası: para, hata zarfı, loglama, güvenlik
- `.bob/skills/<ad>/SKILL.md` altında test yazma prosedürü
- `verify m3`: **11 kontrolün tamamı** PASS
- Modu seçip `services/core/main.py`'yi düzenletmeyi denediniz: **engellendi**
- Yeni sohbette el kitabını **anmadan** bir şey sordunuz, Bob kuralı kendisi uyguladı

## Üç parça, üç ayrı rol

| Parça | Ne zaman devreye girer | Ne tanımlar | Nerede yaşar |
|---|---|---|---|
| **Mode** | Siz seçince | Kimlik ve yetki | `.bob/custom_modes.yaml` |
| **Rules** | Her zaman | Uyulacak standart | `.bob/rules/` (tüm modlar) veya `.bob/rules-<mod-slug>/` |
| **Skill** | İlgili istekte Bob kendisi | Tekrar kullanılabilir prosedür | `.bob/skills/<ad>/SKILL.md` |

## Adım 1 - Modu yazın

Personayı **siz** yazın. Bob sohbetinde `/create-mode` ile bir iskelet oluşturtabilirsiniz; sonuç şu şemaya uymalıdır:

```yaml
customModes:
  - slug: ornek-mod
    name: Örnek Mod
    roleDefinition: Odaklı bir persona tanımı (en az 80 karakter)...
    whenToUse: Bu mod ne zaman seçilmeli
    customInstructions: |-
      Ek talimatlar
    groups:
      - read
      - - edit
        - fileRegex: ^tests/.*\.py$
          description: Yalnızca tests/ altındaki test dosyaları
      - execute
```

> **Sessiz tuzaklar:** Yanlış yazılmış klasör adı veya geçersiz yetki grubu **hata vermez**, parça yok sayılır. YAML'da kıvrık tırnak, uzun tire ve emoji gibi ASCII dışı karakter kullanmayın.
> **Bob'un ürettiği `fileRegex` satırını elle kontrol edin:** yalnızca `tests/` altını eşlemeli; `services/core/main.py` eşleşmemeli.

## Adım 2 - Kurallar ve skill

- **Rules:** el kitabındaki para, hata, loglama ve güvenlik standartları, `.md` dosyası olarak.
- **Skill:** test yazma adımları tek bir prosedür; Bob ilgili isteği görünce kendisi devreye almalı.

```markdown
---
name: klasor-adiyla-ayni
description: Use when ...  (Bob'un ne zaman devreye alacağını anlatan tetikleyici, en az 40 karakter)
---
# Skill gövdesi: adım adım prosedür
```

## Adım 3 - Pencereyi yenileyin ve deneyin

Dosyaları kaydettikten sonra komut paletinden (`Ctrl/Cmd + Shift + P`) şunu çalıştırın:

```text
Developer: Reload Window
```

Sonra modu seçip üretim koduna yazdırmayı deneyin. Reddedilmeli.

## Adım 4 - Doğrulama

Sonucu doğrulamak için aşağıdaki komutu kullanabilirsiniz:

```bash
python3 verify/run.py m3
```

## Keşif noktaları

- Bob Settings'teki **Modes** sekmesi veya `bob --mode <slug>` ile Shell'de modu seçin. Hangi alanlar zorunlu?
- "Dosya düzenleyebilir" ile "yalnızca şu dosyaları düzenleyebilir" aynı şey değil. Mod ayarında bunu nasıl ifade edersiniz?
- Proje düzeyi ile kullanıcı düzeyi: hangi dosya repoya girer, ekip arkadaşınız görür mü?

## İpucu

- **İpucu 1:** Üç parçanın işi farklı: Mode = kimlik ve yetki, Rules = her zaman uyulacak standart, Skill = ilgili işte devreye giren prosedür. `verify` çıktısı hangisinin bozuk olduğunu söyler.
- **İpucu 2:** Geçerli yetki grupları: `read`, `edit`, `execute`, `mcp`, `skill`, `todo`, `subagent`, `mode`. Skill klasör adı küçük harf ve tiredir, frontmatter'daki `name` ile aynı olmalı. Kurallar `Decimal` (ve `float` yasağı), hata zarfı, PII loglama yasağı, gizli bilgi ve parametreli SQL'i kapsamalı. Skill gövdesi `TestClient`, `store.reset()`, mutlu yol, negatif durum ve sınır değerini anlatmalı.
- **Eğitmenden yardım:** İpucu 2 yetmediyse eğitmeni çağırın.
