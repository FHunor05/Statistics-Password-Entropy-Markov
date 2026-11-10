import math
import random
import string
from collections import defaultdict, Counter
from typing import List, Dict, Tuple

import numpy as np
from scipy.stats import entropy as scipy_entropy
import matplotlib.pyplot as plt


# Szabványos, 94 elemű jelszó-ábécé definiálása
KISBETUK = string.ascii_lowercase       # 26 db: a-z
NAGYBETUK = string.ascii_uppercase      # 26 db: A-Z
SZAMOK = string.digits                  # 10 db: 0-9
SPECIALIS = string.punctuation          # 32 db: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
TELJES_ABECE = KISBETUK + NAGYBETUK + SZAMOK + SPECIALIS  # Összesen: 94 karakter


def megfelel_a_szabalynak(jelszo: str) -> bool:
    """
    Ellenőrzi a jelszószabályt: 6-18 karakter, min. 1 kisbetű, 1 nagybetű, 1 szám.
    A speciális karakter opcionális.
    """
    if not (6 <= len(jelszo) <= 18):
        return False
    van_kisbetu = any(c in KISBETUK for c in jelszo)
    van_nagybetu = any(c in NAGYBETUK for c in jelszo)
    van_szam = any(c in SZAMOK for c in jelszo)
    return van_kisbetu and van_nagybetu and van_szam


def szabalyossag_kikenyszeritese(jelszo: str) -> str:
    """Garantálja a 6-18 karakteres hosszt, min. 1 kisbetűt, 1 nagybetűt és 1 számot."""
    while len(jelszo) < 6:
        jelszo += random.choice(SZAMOK)
    if len(jelszo) > 18:
        jelszo = jelszo[:18]

    karakter_lista = list(jelszo)

    if not any(c in KISBETUK for c in karakter_lista):
        karakter_lista[-3] = random.choice(KISBETUK)

    if not any(c in NAGYBETUK for c in karakter_lista):
        kisbetuk_szama = sum(1 for c in karakter_lista if c in KISBETUK)
        if karakter_lista[0] in KISBETUK and kisbetuk_szama > 1:
            karakter_lista[0] = karakter_lista[0].upper()
        else:
            karakter_lista[-2] = random.choice(NAGYBETUK)

    if not any(c in SZAMOK for c in karakter_lista):
        karakter_lista[-1] = random.choice(SZAMOK)

    if not any(c in KISBETUK for c in karakter_lista):
        karakter_lista[-3] = random.choice(KISBETUK)
    if not any(c in NAGYBETUK for c in karakter_lista):
        karakter_lista[-2] = random.choice(NAGYBETUK)
    if not any(c in SZAMOK for c in karakter_lista):
        karakter_lista[-1] = random.choice(SZAMOK)

    return "".join(karakter_lista)


def general_jelszo_minta(
    elemszam: int = 5000,
    szotari_arany: float = 0.70,
    osszetett_arany: float = 0.20,
    seed: int = 42
) -> List[str]:
    """
    Paraméterezhető jelszó-adatbázis generátor.
    A szotari_arany és osszetett_arany paraméterekkel mérhető, hogyan hat
    az emberi kiszámíthatóság aránya a Markov-entrópiára.
    """
    random.seed(seed)

    szotar_alapok = [
        "abrakadabra", "ablak", "almafa", "admin", "titok", "jelszo",
        "passwort", "password", "baba", "balaton", "budapest", "macska",
        "kutya", "kabelek", "szabadsag", "barat", "csaba", "tabor",
        "qwerty", "asdfgh", "zxcvbn", "dragon", "football", "lovag"
    ]
    utotagok = ["1", "12", "123", "1234", "2024", "2025", "99", "00", "1ab"]

    minta = []

    # 1. Mind a 94 karakter garantált elhelyezése az adatbázisban
    karakter_index = 0
    while karakter_index < len(TELJES_ABECE) and len(minta) < elemszam:
        kotelezo_szelet = TELJES_ABECE[karakter_index:karakter_index + 4]
        karakter_index += 4
        extra_hossz = random.randint(2, 8)
        extra = "".join(random.choice(TELJES_ABECE) for _ in range(extra_hossz))
        nyers_jelszo = (
            kotelezo_szelet + extra
            + random.choice(KISBETUK) + random.choice(NAGYBETUK) + random.choice(SZAMOK)
        )
        minta.append(szabalyossag_kikenyszeritese(nyers_jelszo))

    # 2. Fennmaradó jelszavak generálása a megadott arányok szerint
    while len(minta) < elemszam:
        valasztas = random.random()

        if valasztas < szotari_arany:
            alap = random.choice(szotar_alapok)
            if random.random() < 0.6:
                alap = alap.capitalize()
            utotag = random.choice(utotagok)
            spec = random.choice(SPECIALIS) if random.random() < 0.5 else ""
            nyers_jelszo = alap + utotag + spec

        elif valasztas < (szotari_arany + osszetett_arany):
            szo1 = random.choice(szotar_alapok)[:4].capitalize()
            szo2 = random.choice(szotar_alapok)[:4]
            spec = random.choice(SPECIALIS) if random.random() < 0.5 else ""
            szam = random.choice(utotagok)
            nyers_jelszo = f"{szo1}{spec}{szo2}{szam}"

        else:
            hossz = random.randint(6, 18)
            keszlet = TELJES_ABECE if random.random() < 0.5 else (KISBETUK + NAGYBETUK + SZAMOK)
            nyers_jelszo = "".join(random.choice(keszlet) for _ in range(hossz))

        minta.append(szabalyossag_kikenyszeritese(nyers_jelszo))

    return minta


class JelszoMarkovModell:
    """
    Elsőrendű Markov-lánc modell NumPy átmeneti mátrixszal és
    SciPy alapú entrópia-számítással.
    """
    def __init__(self, simitas_alpha: float = 0.0):
        self.alpha = simitas_alpha
        self.atmenet_szamlalo: Dict[str, Counter] = defaultdict(Counter)
        self.kezdo_szamlalo: Counter = Counter()
        self.karakter_szamlalo: Counter = Counter()
        self.osszes_karakter: int = 0
        self.abeceszam: int = 0
        self.tanitott: bool = False

        # NumPy mátrixhoz tartozó indexelés
        self.karakter_lista: List[str] = list(TELJES_ABECE)
        self.kar_index: Dict[str, int] = {k: i for i, k in enumerate(self.karakter_lista)}
        self.atmeneti_matrix_np: np.ndarray = np.zeros((len(TELJES_ABECE), len(TELJES_ABECE)))

    def tanitas(self, jelszavak: List[str]) -> None:
        """Felépíti a gyakorisági szótárakat és a 94x94-es NumPy átmeneti mátrixot."""
        nyers_matrix = np.zeros((len(TELJES_ABECE), len(TELJES_ABECE)), dtype=np.float64)

        for jelszo in jelszavak:
            if not jelszo:
                continue
            self.kezdo_szamlalo[jelszo[0]] += 1

            for i, kar in enumerate(jelszo):
                self.karakter_szamlalo[kar] += 1
                self.osszes_karakter += 1

                if i < len(jelszo) - 1:
                    kov_kar = jelszo[i + 1]
                    self.atmenet_szamlalo[kar][kov_kar] += 1
                    if kar in self.kar_index and kov_kar in self.kar_index:
                        nyers_matrix[self.kar_index[kar], self.kar_index[kov_kar]] += 1.0

        self.abeceszam = len(self.karakter_szamlalo)

        # Soronkénti normálás NumPy-jal (feltételes valószínűségi mátrix P_ij)
        if self.alpha > 0:
            nyers_matrix += self.alpha
        sor_osszegek = nyers_matrix.sum(axis=1, keepdims=True)
        self.atmeneti_matrix_np = np.divide(
            nyers_matrix, sor_osszegek, out=np.zeros_like(nyers_matrix), where=sor_osszegek != 0
        )
        self.tanitott = True

    def felteteles_valoszinuseg(self, aktualis_kar: str, kovetkezo_kar: str) -> float:
        """Lekérdezi a P(X_{t+1} = kovetkezo_kar | X_t = aktualis_kar) értéket a NumPy mátrixból."""
        if not self.tanitott:
            raise RuntimeError("A modellt először tanítani kell!")
        if aktualis_kar in self.kar_index and kovetkezo_kar in self.kar_index:
            return float(self.atmeneti_matrix_np[self.kar_index[aktualis_kar], self.kar_index[kovetkezo_kar]])
        return 0.0

    def top_kovetkezo_karakterek(self, aktualis_kar: str, top_n: int = 5) -> List[Tuple[str, float, int]]:
        eredmenyek = []
        for kov_kar, db in self.atmenet_szamlalo[aktualis_kar].most_common(top_n):
            p = self.felteteles_valoszinuseg(aktualis_kar, kov_kar)
            eredmenyek.append((kov_kar, p, db))
        return eredmenyek

    def jelszo_valoszinusege_es_entropiaja(self, jelszo: str) -> Tuple[float, float, float]:
        if not jelszo:
            return 0.0, 0.0, 0.0

        osszes_jelszo = sum(self.kezdo_szamlalo.values())
        p_kezdo = (self.kezdo_szamlalo[jelszo[0]] + 1e-6) / (osszes_jelszo + 1e-6 * self.abeceszam)
        log2_p = math.log2(p_kezdo)

        for i in range(len(jelszo) - 1):
            p_atmenet = self.felteteles_valoszinuseg(jelszo[i], jelszo[i + 1])
            if p_atmenet == 0.0:
                p_atmenet = 1e-6
            log2_p += math.log2(p_atmenet)

        markov_valoszinuseg = 2 ** log2_p
        markov_entropia_bit = -log2_p
        naiv_entropia_bit = len(jelszo) * math.log2(max(self.abeceszam, 2))

        return markov_valoszinuseg, markov_entropia_bit, naiv_entropia_bit

    def korpusz_entropia_rata(self) -> Tuple[float, float]:
        """
        Kiszámítja az elsőrendű Shannon-entrópiát H(X) és a Markov feltételes
        entrópiát H(X_{t+1} | X_t) a scipy.stats.entropy függvény segítségével (base=2).
        """
        gyakorisagok = np.array(list(self.karakter_szamlalo.values()), dtype=np.float64)
        p_x_eloszlas = gyakorisagok / np.sum(gyakorisagok)
        h_shannon = float(scipy_entropy(p_x_eloszlas, base=2))

        h_markov = 0.0
        osszes_atmenet = sum(sum(c.values()) for c in self.atmenet_szamlalo.values())

        for aktualis_kar, kovetkezo_dict in self.atmenet_szamlalo.items():
            kimeno_db = sum(kovetkezo_dict.values())
            if kimeno_db == 0:
                continue
            p_x = kimeno_db / osszes_atmenet
            sor_valoszinusegek = np.array(list(kovetkezo_dict.values()), dtype=np.float64) / kimeno_db
            h_y_adott_x = float(scipy_entropy(sor_valoszinusegek, base=2))
            h_markov += p_x * h_y_adott_x

        return h_shannon, h_markov


def abrak_es_meresek_generalasa(alap_modell: JelszoMarkovModell) -> None:
    """
    Saját paraméterezett mérések futtatása és 3 db publikációs minőségű
    Matplotlib ábra mentése a PDF dokumentációhoz.
    """
    plt.rcParams["figure.dpi"] = 150

    # --- 1. ÁBRA: Az 'a' karaktert követő Top 10 karakter feltételes valószínűsége ---
    top10_a = alap_modell.top_kovetkezo_karakterek('a', top_n=10)
    karakterek = [elem[0] for elem in top10_a]
    valoszinusegek = [elem[1] * 100 for elem in top10_a]
    egyenletes_szint = (1.0 / alap_modell.abeceszam) * 100

    fig, ax = plt.subplots(figsize=(8, 4.5))
    oszlopok = ax.bar(karakterek, valoszinusegek, color="#2b5c8f", edgecolor="black", alpha=0.85)
    oszlopok[0].set_color("#d95f02")  # 'b' karakter kiemelése
    ax.axhline(egyenletes_szint, color="red", linestyle="--", linewidth=1.5,
               label=f"Egyenletes eloszlás (1/94 = {egyenletes_szint:.2f}%)")

    ax.set_title("Az 'a' karaktert követő Top 10 karakter feltételes valószínűsége P(X_{t+1} | X_t='a')", fontsize=11, fontweight="bold")
    ax.set_xlabel("Következő karakter (X_{t+1})", fontsize=10)
    ax.set_ylabel("Feltételes valószínűség (%)", fontsize=10)
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.6)

    for oszlop, ertek in zip(oszlopok, valoszinusegek):
        ax.text(oszlop.get_x() + oszlop.get_width() / 2, oszlop.get_height() + 0.4,
                f"{ertek:.1f}%", ha="center", va="bottom", fontsize=8, fontweight="bold")

    plt.tight_layout()
    plt.savefig("1_a_kovetkezo_karakterek.png")
    plt.close()

    # --- 2. ÁBRA: Markov-átmeneti mátrix hőtérkép (Top 15 leggyakoribb karakterre) ---
    top15_kar = [k for k, _ in alap_modell.karakter_szamlalo.most_common(15)]
    top15_idx = [alap_modell.kar_index[k] for k in top15_kar]
    resz_matrix = alap_modell.atmeneti_matrix_np[np.ix_(top15_idx, top15_idx)]

    fig, ax = plt.subplots(figsize=(8, 6.5))
    im = ax.imshow(resz_matrix, cmap="YlGnBu", interpolation="nearest")
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Feltételes valószínűség P(oszlop | sor)", fontsize=9)

    ax.set_xticks(np.arange(len(top15_kar)))
    ax.set_yticks(np.arange(len(top15_kar)))
    ax.set_xticklabels(top15_kar, fontsize=9, fontweight="bold")
    ax.set_yticklabels(top15_kar, fontsize=9, fontweight="bold")
    ax.set_xlabel("Következő karakter (X_{t+1})", fontsize=10)
    ax.set_ylabel("Aktuális karakter (X_t)", fontsize=10)
    ax.set_title("Elsőrendű Markov-átmeneti mátrix hőtérképe (Top 15 karakter)", fontsize=11, fontweight="bold")

    for i in range(len(top15_kar)):
        for j in range(len(top15_kar)):
            ertek = resz_matrix[i, j]
            if ertek >= 0.05:
                szin = "white" if ertek > 0.25 else "black"
                ax.text(j, i, f"{ertek:.2f}", ha="center", va="center", color=szin, fontsize=7)

    plt.tight_layout()
    plt.savefig("2_markov_heatmap.png")
    plt.close()

    # --- 3. ÁBRA: Paraméterezett méréssorozat (Szótári arány vs. Entrópia) ---
    szotari_aranyok = np.linspace(0.0, 0.95, 11)
    naiv_entropiak = []
    shannon_entropiak = []
    markov_entropiak = []

    for arany in szotari_aranyok:
        maradek = 1.0 - arany
        minta_meres = general_jelszo_minta(
            elemszam=3000, szotari_arany=float(arany), osszetett_arany=float(maradek * 0.3), seed=42
        )
        m_modell = JelszoMarkovModell()
        m_modell.tanitas(minta_meres)
        h_s, h_m = m_modell.korpusz_entropia_rata()

        naiv_entropiak.append(math.log2(m_modell.abeceszam))
        shannon_entropiak.append(h_s)
        markov_entropiak.append(h_m)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    x_szazalek = szotari_aranyok * 100
    ax.plot(x_szazalek, naiv_entropiak, "k--", linewidth=1.8, label="Naiv entrópia: log2(94) = 6.55 bit")
    ax.plot(x_szazalek, shannon_entropiak, "b-o", linewidth=2, label="Elsőrendű Shannon-entrópia H(X)")
    ax.plot(x_szazalek, markov_entropiak, "r-s", linewidth=2.2, label="Markov feltételes entrópia H(X_{t+1} | X_t)")

    ax.fill_between(x_szazalek, markov_entropiak, shannon_entropiak, color="red", alpha=0.12,
                    label="Karakterfüggőségből eredő entrópiaveszteség")

    ax.set_title("Paramétervizsgálat: A szótári jelszavak arányának hatása az entrópiára", fontsize=11, fontweight="bold")
    ax.set_xlabel("Szótári alapú jelszavak aránya az adatbázisban (%)", fontsize=10)
    ax.set_ylabel("Karakterenkénti entrópia (bit / karakter)", fontsize=10)
    ax.set_ylim(1.0, 7.2)
    ax.grid(True, linestyle=":", alpha=0.7)
    ax.legend(loc="lower left", fontsize=8.5)

    plt.tight_layout()
    plt.savefig("3_parameterezett_entropia_meres.png")
    plt.close()


def main():
    print("=" * 72)
    print(" 13. FELADAT: JELSZÓ-ENTRÓPIA ÉS MARKOV-LÁNC ALAPÚ MODELL (NumPy/SciPy)")
    print("=" * 72)

    jelszavak = general_jelszo_minta(elemszam=5000, szotari_arany=0.70, osszetett_arany=0.20, seed=42)
    modell = JelszoMarkovModell(simitas_alpha=0.0)
    modell.tanitas(jelszavak)

    szabalyos_db = sum(1 for pw in jelszavak if megfelel_a_szabalynak(pw))
    spec_db = sum(1 for pw in jelszavak if any(c in SPECIALIS for c in pw))
    hosszak = [len(pw) for pw in jelszavak]

    print(f"\n[1] ADATBÁZIS ÉS JELSZÓSZABÁLY STATISZTIKÁK")
    print(f"  - Elemzett jelszavak száma          : {len(jelszavak)} db")
    print(f"  - Jelszóhossz tartomány (min - max) : {min(hosszak)} - {max(hosszak)} karakter")
    print(f"  - Szabálynak megfelelő jelszavak    : {szabalyos_db}/{len(jelszavak)} db (100.0%)")
    print(f"  - Speciális karaktert is tartalmaz  : {spec_db}/{len(jelszavak)} db ({spec_db / len(jelszavak) * 100:.1f}%)")
    print(f"  - Egyedi karakterek száma (Ábécé)   : {modell.abeceszam} db (94x94 NumPy mátrix)")

    p_ab = modell.felteteles_valoszinuseg('a', 'b')
    a_osszes = sum(modell.atmenet_szamlalo['a'].values())
    ab_db = modell.atmenet_szamlalo['a']['b']

    print(f"\n[2] FELTÉTELES VALÓSZÍNŰSÉG VIZSGÁLATA ('a' -> 'b')")
    print(f"  - Az 'a' karakter után álló karakterek száma összesen : {a_osszes} db")
    print(f"  - Ebből közvetlenül 'b' karakter következik           : {ab_db} db")
    print(f"  - P(X_{{t+1}} = 'b' | X_t = 'a') = {p_ab:.4f} ({p_ab * 100:.2f}%)")

    h_shannon, h_markov = modell.korpusz_entropia_rata()
    print(f"\n[3] KARAKTERENKÉNTI ENTRÓPIA ÖSSZEHASONLÍTÁSA (SciPy)")
    print(f"  - Egyenletes eloszlás (log2({modell.abeceszam}))      : {math.log2(modell.abeceszam):.2f} bit/karakter")
    print(f"  - Független karakterek (Shannon H(X)) : {h_shannon:.2f} bit/karakter")
    print(f"  - Markov-lánc feltételes H(X_{{t+1}}|X_t) : {h_markov:.2f} bit/karakter")
    print(f"  -> Entrópiacsökkenés: {((h_shannon - h_markov) / h_shannon) * 100:.1f}%")

    teszt_jelszavak = ["Abrakadabra123", "Balaton2024!", "Qwerty12", "X9#q7$Z2!k8&M4"]
    print(f"\n[4] SZABÁLYOS JELSZAVAK VALÓDI (MARKOV) VS. NAIV (BRUTE-FORCE) ENTRÓPIÁJA")
    print(f"  {'Jelszó':<18} | {'Hossz':<5} | {'Naiv entrópia':<15} | {'Markov entrópia':<17} | {'Log10 P(jelszó)'}")
    print("  " + "-" * 78)
    for pw in teszt_jelszavak:
        p_w, h_m, h_n = modell.jelszo_valoszinusege_es_entropiaja(pw)
        log10_p = math.log10(p_w) if p_w > 0 else float('-inf')
        print(f"  {pw:<18} | {len(pw):^5} | {h_n:>9.2f} bit  | {h_m:>11.2f} bit  | {log10_p:>10.2f}")

    print(f"\n[5] PARAMÉTEREZETT MÉRÉSEK ÉS MATPLOTLIB ÁBRÁK GENERÁLÁSA...")
    abrak_es_meresek_generalasa(modell)
    print("  -> Elkészült: 1_a_kovetkezo_karakterek.png")
    print("  -> Elkészült: 2_markov_heatmap.png")
    print("  -> Elkészült: 3_parameterezett_entropia_meres.png")


if __name__ == "__main__":
    main()