# M4 - Kapsamlı test yazımı (kendi modunuzla)

**Süre:** 25 dk | **Bob özelliği:** M3'te yazdığınız **Custom Mode + Rules + Skill**'in değeri

> macOS/Linux'ta `python3`, Windows'ta `py` yazın.

## Durum

Release gate'in ikinci koşulu: `services/core` için **%85 satır kapsamı**. Şu an `tests/` altında yalnızca bir `/health` testi var.
Ekip lideri: "Test sayısı değil, **testlerin gerçekten koruduğu davranış** önemli."

- [`docs/ENGINEERING-HANDBOOK.md`](../docs/ENGINEERING-HANDBOOK.md) bölüm 4
- [`docs/FEE-POLICY.md`](../docs/FEE-POLICY.md): ücret tablosu ve sınır değerleri

> **Kapsam notu: M2 sonrası durum.** M4'te M2'de düzelttiğiniz kodla çalışırsınız. M2'de kapattığınız sorunlarla örtüşen hatalar zaten düzelmiş olabilir; bulacağınız hatalar M2'de kapanmamış olanlardır. Hepsini görmeniz gerekmez, davranışı koruyan testler yazmak asıl hedeftir.

## Teslim edilecekler

- En az **25 test**, ekip standardında (`TestClient`, `store.reset()`, iç fonksiyon import'u yok)
- `services/core` satır kapsamı en az **%85**
- Bulunan gizli hatalar **Agent** modunda düzeltildi ve testle kanıtlandı
- Testleriniz doğrulayıcının geçici bozduğu kodu yakalıyor (mutasyon kontrolü)
- `verify m4`: **12 kontrolün tamamı** PASS

## Adım 1 - Testleri yazdırın

**M3'te yazdığınız moda** geçin. Önce testin değil **davranışın** listesini çıkarın: her endpoint için bir mutlu yol, bir negatif durum, bir sınır değeri.
Mod ve skill'i siz kurduğunuz için standardı tekrar anlatmanız gerekmemeli; gerekiyorsa M3'e dönüp skill'i düzeltin.

Kapsamı ölçmek için. macOS/Linux:

```bash
.venv/bin/python -m pytest --cov=services/core --cov-branch
```

Windows (PowerShell):

```powershell
.venv\Scripts\python -m pytest --cov=services/core --cov-branch
```

## Adım 2 - Bulunan hataları kapatın

İyi bir sınır değeri veya negatif test gizli hataları ortaya çıkarır. Mod üretim koduna yazamaz:

1. Hatayı QA modunun **raporlamasını** sağlayın (test beklentisini düşürmek yerine).
2. **Agent** moduna geçip kodu düzelttirin.
3. QA moduna dönüp düzeltmeyi testle kanıtlayın.

Test geçmediğinde önce testin mi, kodun mu yanlış olduğuna el kitabına bakarak karar verin.

## Adım 3 - Doğrulama

Sonucu doğrulamak için aşağıdaki komutu kullanabilirsiniz:

```bash
python3 verify/run.py m4
```

Mutasyon kontrolü FAIL verirse çıktı hangi davranışı test etmediğinizi söyler.

## Keşif noktaları

- Moddan üretim koduna dokunmasını isteyin. Ne oluyor? Bu bir kısıtlama mı, güvenlik ağı mı?
- Bob hatayla karşılaşınca testi mi gevşetiyor, hatayı mı raporluyor? Skill'inizde bunu söylediniz mi?
- Bonus: `pytest --cov` çıktısını Bob'a yorumlatın; en riskli kapsanmayan davranış hangisi?

## İpucu

- **İpucu 1:** Test geçmiyor diye kodu değil, önce beklentiyi sorgulayın. Hata gerçekse modunuz üretim koduna yazamaz: raporlatın.
- **İpucu 2:** Şu denemelerle arayın: negatif bakiyeyle hesap oluşturma, aynı `id` ile ikinci hesap, aynı hesaptan aynı hesaba transfer, transfer sonrası log satırında ne yazıyor? Ücret sınırı için `999.99`, `1000.00`, `1000.01` tutarlarını test edin.
- **Eğitmenden yardım:** İpucu 2 yetmediyse eğitmeni çağırın.
