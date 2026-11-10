# Jelszó-entrópia és szótáralapú feltörés valószínűségi modellje

> **13. Feladat:** Elemezz egy anonimizált jelszó-adatbázist (vagy saját generált mintát). Számítsd ki a karakterek feltételes valószínűségét (Markov-lánc szemlélettel: mekkora eséllyel követi az `'a'`-t egy `'b'`).

---

## 1. Elméleti háttér és matematikai modell

A hagyományos (naiv) jelszóerősség-mérők azt feltételezik, hogy a felhasználó a jelszó minden egyes karakterét egymástól függetlenül, egyenletes valószínűséggel választja ki egy $N$ elemű ábécéből ($\Sigma$). A szabványos, 94 elemű nyomtatható ASCII karakterkészlet ($N = 94$) esetén egy $L$ hosszúságú jelszó brute-force entrópiája:

$$H_{\text{naiv}} = L \cdot \log_2(94) \approx L \cdot 6{,}5546 \text{ [bit]}$$

A gyakorlatban – még szigorú jelszóházirend (**6–18 karakter hossz, legalább 1 kisbetű, 1 nagybetű, 1 számjegy, valamint opcionális speciális karakter**) mellett is – a felhasználók természetes nyelvi szótöveket nagybetűsítenek, majd a jelszó végére évszámokat vagy gyakori számsorokat illesztenek (pl. `Abrakadabra123`, `Balaton2024!`). Emiatt az egymást követő karakterek nem függetlenek.

### Elsőrendű diszkrét idejű Markov-lánc
A jelszavak karakterláncát egy elsőrendű Markov-láncként modellezzük, amelynek állapottere a 94 elemű $\Sigma$ ábécé. A Markov-tulajdonság alapján a következő karakter eloszlása csak az aktuális karaktertől függ:

$$P(X_{t+1} = x_{t+1} \mid X_t = x_t, X_{t-1} = x_{t-1}, \dots, X_1 = x_1) = P(X_{t+1} = x_{t+1} \mid X_t = x_t)$$

Az átmeneti valószínűségi mátrix ($\mathbf{P} \in \mathbb{R}^{94 \times 94}$) elemeit a korpuszban megfigyelt karakterpárok (bigramok) relatív gyakoriságából becsüljük (opcionális $\alpha$ Laplace-simítással):

$$P_{i,j} = P(X_{t+1} = c_j \mid X_t = c_i) = \frac{N(c_i, c_j) + \alpha}{\sum_{k \in \Sigma} N(c_i, c_k) + \alpha \cdot \vert{}\Sigma\vert{}}$$

Speciálisan az `'a' -> 'b'` átmenetre ($\alpha = 0$ esetén):

$$P(X_{t+1} = \text{'b'} \mid X_t = \text{'a'}) = \frac{N(\text{"ab"})}{\sum_{c \in \Sigma} N(\text{"a"}c)}$$

### Korpusz- és jelszószintű entrópia
Egy $w = c_1 c_2 \dots c_L$ jelszó együttes valószínűsége és Markov-alapú öninformációja (találgatási entrópiája):

$$P(w) = P(c_1) \cdot \prod_{i=1}^{L-1} P(c_{i+1} \mid c_i), \qquad H_{\text{Markov}}(w) = -\log_2 P(w) = -\log_2 P(c_1) - \sum_{i=1}^{L-1} \log_2 P(c_{i+1} \mid c_i)$$

A teljes adatbázisra jellemző egy karakterre jutó átlagos bizonytalanságot az elsőrendű **Shannon-entrópia** ($H(X)$), valamint a karakterfüggőségeket is figyelembe vevő **Markov feltételes entrópia** ($H(X_{t+1} \mid X_t)$) adja meg:

$$H(X) = -\sum_{x \in \Sigma} P(x) \log_2 P(x), \qquad H(X_{t+1} \mid X_t) = -\sum_{x \in \Sigma} P(x) \sum_{y \in \Sigma} P(y \mid x) \log_2 P(y \mid x)$$

---

## 2. A projekt felépítése és technológiai stack

A megoldás a `numpy`, `scipy` és `matplotlib` tudományos könyvtárakra épül:

```text
Statistics-Password-Entropy-Markov/
├── .gitignore
├── README.md                              # Dokumentáció, elmélet és kritikus elemzés
├── jelszo_markov.py                       # NumPy/SciPy alapú szimuláció és Markov-modell
├── 1_a_kovetkezo_karakterek.png           # 1. ábra: P(X_{t+1} | X_t='a') eloszlás
├── 2_markov_heatmap.png                   # 2. ábra: 15x15 Markov-átmeneti hőtérkép
└── 3_parameterezett_entropia_meres.png    # 3. ábra: Paraméterezett entrópiamérés
```

* **Saját adatgenerálás és szabálykikényszerítés (`general_jelszo_minta`):**
  * **Ábécé ($N=94$):** 26 kisbetű (`a–z`), 26 nagybetű (`A–Z`), 10 számjegy (`0–9`) és 32 speciális karakter (`string.punctuation`).
  * **Garantált komplexitási szabály (`megfelel_a_szabalynak`):** Minden generált jelszó hossza **6 és 18 karakter közé esik**, és kötelezően tartalmaz **legalább 1 kisbetűt, 1 nagybetűt és 1 számjegyet**, míg a speciális karakterek használata opcionális (~50%-os előfordulással).
* **Vektorizált átmeneti mátrix és SciPy entrópia (`JelszoMarkovModell`):**
  * A $94 \times 94$-es átmeneti