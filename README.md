# Jelszó-entrópia és szótáralapú feltörés valószínűségi modellje

> **13. Feladat:** Elemezz egy anonimizált jelszó-adatbázist (vagy saját generált mintát)[cite: 1]. Számítsd ki a karakterek feltételes valószínűségét (Markov-lánc szemlélettel: mekkora eséllyel követi az `'a'`-t egy `'b'`)[cite: 1].

---

## 1. Elméleti háttér és célkitűzés

A klasszikus (naiv) jelszóerősség-becslés azt feltételezi, hogy a jelszó minden egyes karakterét egymástól függetlenül, egyenletes eloszlással választják ki egy $N$ elemű ábécéből ($\Sigma$). Ekkor egy $L$ hosszúságú jelszó brute-force entrópiája:

$$H_{\text{naiv}} = L \cdot \log_2(N) \text{ [bit]}$$

A valóságban a felhasználók gyakori szótári szavakat, billentyűzet-mintázatokat (`qwerty`) és kiszámítható számvégződéseket (`123`, évszámok) használnak. Emiatt az egymást követő karakterek nem függetlenek: egy adott karakter megjelenése erősen függ az őt közvetlenül megelőző karaktertől[cite: 1].

### Elsőrendű Markov-lánc modell
A jelszavak karakterláncát egy elsőrendű, diszkrét idejű Markov-láncként modellezzük[cite: 1], ahol a következő karakter feltételes valószínűsége csak az aktuális karaktertől függ:

$$P(X_{t+1} = x_{t+1} \mid X_t = x_t, X_{t-1} = x_{t-1}, \dots, X_1 = x_1) = P(X_{t+1} = x_{t+1} \mid X_t = x_t)$$

Az átmeneti valószínűségeket a jelszó-adatbázisban megfigyelt karakterpárok (bigramok) empirikus gyakoriságából becsüljük[cite: 1]. Annak a feltételes valószínűsége, hogy az `'a'` karaktert közvetlenül egy `'b'` karakter követi[cite: 1]:

$$P(X_{t+1} = \text{'b'} \mid X_t = \text{'a'}) = \frac{N(\text{"ab"})}{\sum_{c \in \Sigma} N(\text{"a"}c)}$$

ahol $N(\text{"ab"})$ az `"ab"` karakterpár előfordulásainak száma, a nevező pedig az `'a'` karakter összes nem-szóvégi előfordulása az adatbázisban.

### Jelszó-valószínűség és Markov-entrópia
Egy $w = c_1 c_2 \dots c_L$ jelszó együttes előfordulási valószínűsége a Markov-lánc szerint:

$$P(w) = P(c_1) \cdot \prod_{i=1}^{L-1} P(c_{i+1} \mid c_i)$$

Az egy karakterre jutó átlagos bizonytalanságot a korpusz szintjén az elsőrendű **Shannon-entrópia** ($H(X)$), illetve a karakterfüggőségeket is figyelembe vevő **feltételes entrópia** ($H(X_{t+1} \mid X_t)$) méri:

$$H(X) = -\sum_{x \in \Sigma} P(x) \log_2 P(x)$$

$$H(X_{t+1} \mid X_t) = -\sum_{x \in \Sigma} P(x) \sum_{y \in \Sigma} P(y \mid x) \log_2 P(y \mid x)$$

---

## 2. A projekt felépítése

```text
jelszo-entropia-markov/
├── .gitignore
├── README.md                  # Projektdokumentáció és eredmények
└── jelszo_markov_entropia.py  # Adatgeneráló, Markov-modell és kiértékelő szkript
```

### Főbb komponensek (`jelszo_markov_entropia.py`)
* **`general_jelszo_minta(elemszam, seed)`**: Reprodukálható (`seed=42`), 5000 elemű szintetikus jelszó-adatbázist állít elő[cite: 1]:
  * **70%** szótári alapú jelszó + gyakori utótagok (pl. `abrakadabra123`, `balaton2024`, `admin!`),
  * **20%** két rövid szótöredék összefűzése,
  * **10%** valódi véletlenszerű kisbetűs-számos karakterlánc.
  * *Az ábécé mérete ($N = 37$):* Az adatbázisban 26 angol kisbetű (`a`–`z`), 10 számjegy (`0`–`9`) és 1 speciális karakter (`!`) fordul elő.
* **`JelszoMarkovModell` osztály**:
  * `tanitas(jelszavak)`: $O(M)$ időkomplexitással (ahol $M$ az összes karakter száma) felépíti a kezdőkarakterek eloszlását, az egyedi karakterek gyakoriságát és a `defaultdict(Counter)` alapú ritka átmeneti mátrixot.
  * `felteteles_valoszinuseg(aktualis_kar, kovetkezo_kar)`: Kiszámítja a $P(X_{t+1} \mid X_t)$ átmeneti valószínűséget (opcionális Laplace-simítással)[cite: 1].
  * `jelszo_valoszinusege_es_entropiaja(jelszo)`: Logaritmikus térben ($\log_2$) számítja ki egy konkrét jelszó Markov-valószínűségét és entrópiáját a lebegőpontos alulcsordulás (*underflow*) elkerülése végett.
  * `korpusz_entropia_rata()`: Kiszámítja az adatbázisra jellemző $H(X)$ és $H(X_{t+1} \mid X_t)$ értékeket.

---

## 3. Futtatási útmutató

A szkript kizárólag a Python beépített könyvtárait (`math`, `random`, `collections`, `typing`) használja, így külső csomag telepítése nem szükséges.

**Követelmények:** Python 3.8+

```bash
# Tároló klónozása
git clone [https://github.com/FELHASZNALONEVED/jelszo-entropia-markov.git](https://github.com/FELHASZNALONEVED/jelszo-entropia-markov.git)
cd jelszo-entropia-markov

# Szkript futtatása
python jelszo_markov_entropia.py
```

---

## 4. Futási eredmények és kiértékelés

### 4.1. Konzolkimenet

```text
=================================================================
 13. FELADAT: JELSZÓ-ENTRÓPIA ÉS MARKOV-LÁNC ALAPÚ MODELL
=================================================================

[1] ADATBÁZIS STATISZTIKÁK
  - Elemzett jelszavak száma : 5000 db
  - Összes elemzett karakter : 40886 db
  - Egyedi karakterek száma  : 37 db

[2] FELTÉTELES VALÓSZÍNŰSÉG VIZSGÁLATA ('a' -> 'b')
  - Az 'a' karakter után álló karakterek száma összesen : 6705 db
  - Ebből közvetlenül 'b' karakter következik           : 1538 db
  - P(X_{t+1} = 'b' | X_t = 'a') = 0.2294 (22.94%)

[3] LEGGYAKORIBB FOLYTATÁSOK AZ 'a' KARAKTER UTÁN (TOP 5)
  - 'a' -> 'b' : P = 0.2294 (22.94%) | (1538 előfordulás)
  - 'a' -> 'l' : P = 0.1308 (13.08%) | (877 előfordulás)
  - 'a' -> 'd' : P = 0.1235 (12.35%) | (828 előfordulás)
  - 'a' -> 'k' : P = 0.1059 (10.59%) | (710 előfordulás)
  - 'a' -> 't' : P = 0.0880 ( 8.80%) | (590 előfordulás)

[4] KARAKTERENKÉNTI ENTRÓPIA ÖSSZEHASONLÍTÁSA
  - Egyenletes eloszlás (log2(37))      : 5.21 bit/karakter
  - Független karakterek (Shannon H(X)) : 4.46 bit/karakter
  - Markov-lánc feltételes H(X_{t+1}|X_t) : 1.73 bit/karakter
  -> A karakterek közti függőség 61.2%-kal csökkenti a bizonytalanságot!
```

### 4.2. Eredmények elemzése

1. **Az `'a' -> 'b'` átmenet valószínűsége[cite: 1]:**
   A mintában az `'a'` betűt 6705 esetben követi további karakter, ebből 1538 esetben a `'b'` betű (olyan gyakori szótövek miatt, mint az *abrakadabra*, *ablak*, *baba*, *szabadsag*, *csaba*). A kapott feltételes valószínűség **$P(\text{'b'} \mid \text{'a'}) = 22{,}94\%$**, ami több mint nyolcszorosa az egyenletes eloszlásból adódó $1/37 \approx 2{,}70\%$-os értéknek[cite: 1].
2. **Entrópiacsökkenés a Markov-függőség miatt:**
   Míg egyenletes eloszlás mellett 5,21 bit, a karakterek egyedi gyakoriságát ismerve pedig 4,46 bit egy karakter entrópiája, addig az előző karakter ismeretében a bizonytalanság **1,73 bit/karakterre** esik vissza (61,2%-os csökkenés).
3. **Egyedi jelszavak összehasonlítása (Naiv vs. Markov-entrópia):**

| Vizsgált jelszó | Hossz | Naiv entrópia (Brute-force) | Markov-entrópia (Szótári/Markov) | $\log_{10} P(\text{jelszó})$ | Következtetés |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `abrakadabra123` | 14 | 72,93 bit | **15,73 bit** | -4,73 | Hosszú, de gyakori átmenetekből áll, így szótári támadással gyorsan feltörhető. |
| `balaton2024` | 11 | 57