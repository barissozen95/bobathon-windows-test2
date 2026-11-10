# FEE-POLICY - Transfer Ücreti Politikası

**Sahip:** Ürün / Finans Operasyonları | **Sürüm:** 1.2 | **Geçerlilik:** 01.01.2025

## Kurallar

| Transfer tutarı (TRY) | Ücret oranı |
|---|---|
| `0.01` ≤ tutar **<** `1000.00` | %0,50 |
| tutar **≥** `1000.00` | %0,25 |

1. Eşik değer (`1000.00`) **dahildir** ve düşük oran uygulanır.
2. Ücret kuruş hassasiyetinde (2 ondalık) hesaplanır.
3. Yuvarlama **ROUND_HALF_UP**'dır (0,015 → 0,02). Banker's rounding ve ikili kayan nokta (float) hesaplama **kullanılmaz**.
4. Para tutarları kod içinde `Decimal` ile tutulur (bkz. ENGINEERING-HANDBOOK).

## Örnekler

| Tutar | Oran | Ücret |
|---|---|---|
| 3.00 | %0,50 | 0.02 |
| 10.10 | %0,50 | 0.05 |
| 100.00 | %0,50 | 0.50 |
| 999.99 | %0,50 | 5.00 |
| 1000.00 | %0,25 | 2.50 |
| 1234.56 | %0,25 | 3.09 |
