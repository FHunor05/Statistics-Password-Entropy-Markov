# Jelszó-entrópia és szótáralapú feltörés valószínűségi modellje

> **13. Feladat:** Elemezz egy anonimizált jelszó-adatbázist (vagy saját generált mintát)[cite: 1]. Számítsd ki a karakterek feltételes valószínűségét (Markov-lánc szemlélettel: mekkora eséllyel követi az `'a'`-t egy `'b'`)[cite: 1].

---

## 1. Elméleti háttér és célkitűzés

A klasszikus (naiv) jelszóerősség-becslés azt feltételezi, hogy a jelszó minden egyes karakterét egymástól függetlenül, egyenletes eloszlással választják ki egy $N$ elemű ábécéből ($\Sigma$). Szabványos, nyomtatható ASCII karakterkészlet esetén ($N = 94$) egy $L$ hosszúságú jelszó brute-force entrópiája:

$$H_{\text{naiv}} = L \cdot \log_2(94) \approx L \cdot 6{,}55 \text{ [bit]}$$

A gyakorlatban még az ajánlott jelszószabályok (**6–18 karakter hossz, legalább 1 kisbetű, 1 nagybetű, 1 számjegy, valamint opcionális speciális karakter**) mellett is megfigyelhető, hogy a felhasználók gyakori szótári szavakat nagybetűsítenek, és a végükre illesztenek számokat (pl. `Abrakadabra123`, `Balaton2024!`). Emiatt az egymást követő karakterek nem függetlenek: egy adott karakter megjelenése erősen függ az őt megelőző karaktertől[cite: 1].

### Elsőrendű Markov-lánc modell
A jelszavak karakterláncát egy elsőrendű, diszkrét idejű Markov-láncként modellezzük[cite: 1], ahol a következő karakter feltételes valószínűsége csak az aktuális karaktertől függ:

$$P(X_{t+1} = x_{t+1} \mid X_t = x_t, X_{t-1} = x_{t-1}, \dots, X_1 = x_1) = P(X_{t+1} = x_{t+1} \mid X_t = x_t)$$

Annak a feltételes valószínűsége, hogy az `'a'` karaktert közvetlenül egy `'b'` karakter követi[cite: 1]:

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
Statistics-Password-Entropy-Markov/
├── .gitignore
├── README.md          # Projektdokumentáció és eredmények
└── jelszo_markov.py   # Adatgeneráló, szabályellenőrző és Markov-modell szkript
```

### Főbb komponensek (`jelszo_markov.py`)
* **Teljes, 94 elemű karakterkészlet (`TELJES_ABECE`):**
  * **26 angol kisbetű** (`a`–`z`)
  * **26 angol nagybetű** (`A`–`Z`)
  * **10 számjegy** (`0`–`9`)
  * **32 speciális karakter** (`!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~`)
* **Garantált jelszószabályok (`megfelel_a_szabalynak` és `szabalyossag_kikenyszeritese`):**
  * Az adatbázis minden egyes elemére (5000/5000 db, 100%) garantált, hogy a hossza **6 és 18 karakter közé esik**, és tartalmaz **legalább 1 kisbetűt**, **legalább 1 nagybetűt**, valamint **legalább 1 számjegyet**.
  * A **speciális karakterek használata opcionális** (a jelszavak kb. felében fordulnak elő), ugyanakkor az adatbázis egésze mind a 32 speciális karaktert lefedi.
* **`JelszoMarkovModell` osztály:**
  * `tanitas(jelszavak)`: $O(M)$ időkomplexitással felépíti a kezdőkarakterek eloszlását, az egyedi karakterek gyakoriságát és a ritka (sparse) átmeneti mátrixot.
  * `felteteles_valoszinuseg(aktualis_kar, kovetkezo_kar)`: Kiszámítja a $P(X_{t+1} \mid X_t)$ átmeneti valószínűséget[cite: 1].
  * `jelszo_valoszinusege_es_entropiaja(jelszo)`: Logaritmikus térben ($\log_2$) számítja ki egy konkrét jelszó Markov-valószínűségét és entrópiáját.
  * `korpusz_entropia_rata()`: Kiszámítja az adatbázisra jellemző $H(X)$ és $H(X_{t+1} \mid X_t)$ értékeket.

---

## 3. Futtatási útmutató

A szkript kizárólag a Python beépített könyvtárait (`math`, `random`, `string`, `collections`, `typing`) használja.

**Követelmények:** Python 3.8+

```bash
# Tároló klónozása
git clone [https://github.com/FHunor05/Statistics-Password-Entropy-Markov.git](https://github.com/FHunor05/Statistics-Password-Entropy-Markov.git)
cd Statistics-Password-Entropy-Markov

# Szkript futtatása
python jelszo_markov.py
```

---

## 4. Eredmények elemzése és következtetések

1. **Jelszószabályok és a 94 karakteres ábécé lefedettsége:**
   Az 5000 generált jelszó 100%-a teljesíti a 6–18 karakteres hosszkorlátot, valamint a kötelező kisbetűs, nagybetűs és számjegyes követelményt. A speciális karakterek opcionálisak, de a teljes mintában mind a 94 nyomtatható ASCII karakter előfordul.
2. **Az `'a' -> 'b'` átmenet valószínűsége[cite: 1]:**
   Ha a 94 karakter egyenletes eloszlást követne, annak az esélye, hogy az `'a'` betűt egy `'b'` követi, mindössze $1/94 \approx 1{,}06\%$ lenne. A szótári tövek (*abrakadabra*, *ablak*, *baba*, *szabadsag*, *csaba*) miatt azonban a tényleges feltételes valószínűség **$P(\text{'b'} \mid \text{'a'}) > 20\%$**, vagyis nagyságrenddel magasabb a véletlen szintnél[cite: 1].
3. **Naiv vs. Markov-entrópia összehasonlítása:**
   * A szabályoknak formálisan megfelelő, de szótári alapú jelszavak (mint az `Abrakadabra123` vagy a `Balaton2024!`) magas naiv brute-force entrópiával (~85–90 bit) rendelkeznek, ám a kiszámítható karakterátmenetek miatt a Markov-entrópiájuk töredékére (~18–22 bitre) esik vissza.
   * Ezzel szemben a valóban véletlenszerű karakterláncok (`X9#q7$Z2!k8&M4`) a Markov-alapú, szótári támadásokkal szemben is megőrzik magas entrópiájukat.