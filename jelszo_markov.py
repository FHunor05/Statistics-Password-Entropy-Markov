import math
import random
import string
from collections import defaultdict, Counter
from typing import List, Dict, Tuple


# Szabványos, 94 elemű jelszó-ábécé definiálása
KISBETUK = string.ascii_lowercase       # 26 db: a-z
NAGYBETUK = string.ascii_uppercase      # 26 db: A-Z
SZAMOK = string.digits                  # 10 db: 0-9
SPECIALIS = string.punctuation          # 32 db: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
TELJES_ABECE = KISBETUK + NAGYBETUK + SZAMOK + SPECIALIS  # Összesen: 94 karakter


def megfelel_a_szabalynak(jelszo: str) -> bool:
    """
    Ellenőrzi, hogy a jelszó megfelel-e az ajánlott jelszószabálynak:
    - Hossz: 6 és 18 karakter között (6 <= hossz <= 18)
    - Legalább 1 kisbetűs karakter (a-z)
    - Legalább 1 nagybetűs karakter (A-Z)
    - Legalább 1 számjegy (0-9)
    - Speciális karakter: opcionális
    """
    if not (6 <= len(jelszo) <= 18):
        return False
    van_kisbetu = any(c in KISBETUK for c in jelszo)
    van_nagybetu = any(c in NAGYBETUK for c in jelszo)
    van_szam = any(c in SZAMOK for c in jelszo)
    return van_kisbetu and van_nagybetu and van_szam


def szabalyossag_kikenyszeritese(jelszo: str) -> str:
    """
    Átalakítja a jelszójelöltet úgy, hogy garantáltan teljesítse a
    6-18 karakteres hosszt, valamint a min. 1 kisbetű, 1 nagybetű és 1 szám szabályt.
    """
    # 1. Hossz beállítása (6 és 18 karakter közé)
    while len(jelszo) < 6:
        jelszo += random.choice(SZAMOK)
    if len(jelszo) > 18:
        jelszo = jelszo[:18]

    karakter_lista = list(jelszo)

    # 2. Kötelező karaktertípusok (kisbetű, nagybetű, szám) ellenőrzése és pótlása
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

    # Biztonsági ellenőrzés: a három különböző végső pozíció (-3, -2, -1)
    # garantálja, hogy egyik pótlás se írja felül a másikat
    if not any(c in KISBETUK for c in karakter_lista):
        karakter_lista[-3] = random.choice(KISBETUK)
    if not any(c in NAGYBETUK for c in karakter_lista):
        karakter_lista[-2] = random.choice(NAGYBETUK)
    if not any(c in SZAMOK for c in karakter_lista):
        karakter_lista[-1] = random.choice(SZAMOK)

    return "".join(karakter_lista)


def general_jelszo_minta(elemszam: int = 5000, seed: int = 42) -> List[str]:
    """
    Saját, valósághű jelszó-adatbázis generálása, amely:
    - Garantálja a 6-18 karakteres hosszt, min. 1 kisbetűt, 1 nagybetűt és 1 számot.
    - A speciális karaktereket opcionálisan kezeli, de garantálja mind a 94
      szabványos karakter előfordulását az adatbázisban.
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

    # 1. LÉPÉS: Garantáljuk, hogy a 94 karakter mindegyike (beleértve a 32
    # speciális karaktert is) bekerüljön az adatbázisba szabályos jelszavakban.
    karakter_index = 0
    while karakter_index < len(TELJES_ABECE):
        kotelezo_szelet = TELJES_ABECE[karakter_index:karakter_index + 4]
        karakter_index += 4
        extra_hossz = random.randint(2, 8)
        extra = "".join(random.choice(TELJES_ABECE) for _ in range(extra_hossz))
        nyers_jelszo = (
            kotelezo_szelet
            + extra
            + random.choice(KISBETUK)
            + random.choice(NAGYBETUK)
            + random.choice(SZAMOK)
        )
        minta.append(szabalyossag_kikenyszeritese(nyers_jelszo))

    # 2. LÉPÉS: A fennmaradó jelszavak generálása (opcionális speciális karakterekkel)
    while len(minta) < elemszam:
        valasztas = random.random()

        if valasztas < 0.70:
            # 70%: Szótári alapú jelszó + számutótag + opcionális speciális karakter (50% eséllyel)
            alap = random.choice(szotar_alapok)
            if random.random() < 0.6:
                alap = alap.capitalize()
            utotag = random.choice(utotagok)
            spec = random.choice(SPECIALIS) if random.random() < 0.5 else ""
            nyers_jelszo = alap + utotag + spec

        elif valasztas < 0.90:
            # 20%: Két szótöredék + szám + opcionális speciális karakter (50% eséllyel)
            szo1 = random.choice(szotar_alapok)[:4].capitalize()
            szo2 = random.choice(szotar_alapok)[:4]
            spec = random.choice(SPECIALIS) if random.random() < 0.5 else ""
            szam = random.choice(utotagok)
            nyers_jelszo = f"{szo1}{spec}{szo2}{szam}"

        else:
            # 10%: Véletlenszerű jelszó (fele speciális karakterrel, fele csak alfanumerikus)
            hossz = random.randint(6, 18)
            if random.random() < 0.5:
                keszlet = TELJES_ABECE
            else:
                keszlet = KISBETUK + NAGYBETUK + SZAMOK
            nyers_jelszo = "".join(random.choice(keszlet) for _ in range(hossz))

        szabalyos_jelszo = szabalyossag_kikenyszeritese(nyers_jelszo)
        minta.append(szabalyos_jelszo)

    return minta


class JelszoMarkovModell:
    """
    Elsőrendű Markov-lánc modell jelszavak karakterátmeneteinek és
    entrópiájának vizsgálatára.
    """
    def __init__(self, simitas_alpha: float = 0.0):
        self.alpha = simitas_alpha
        self.atmenet_szamlalo: Dict[str, Counter] = defaultdict(Counter)
        self.kezdo_szamlalo: Counter = Counter()
        self.karakter_szamlalo: Counter = Counter()
        self.osszes_karakter: int = 0
        self.abeceszam: int = 0
        self.tanitott: bool = False

    def tanitas(self, jelszavak: List[str]) -> None:
        """
        A jelszó-adatbázis elemzése: karaktergyakoriságok és
        bigram (c_i -> c_{i+1}) átmenetek megszámlálása.
        """
        for jelszo in jelszavak:
            if not jelszo:
                continue

            self.kezdo_szamlalo[jelszo[0]] += 1

            for i, kar in enumerate(jelszo):
                self.karakter_szamlalo[kar] += 1
                self.osszes_karakter += 1

                if i < len(jelszo) - 1:
                    kovetkezo_kar = jelszo[i + 1]
                    self.atmenet_szamlalo[kar][kovetkezo_kar] += 1

        self.abeceszam = len(self.karakter_szamlalo)
        self.tanitott = True

    def felteteles_valoszinuseg(self, aktualis_kar: str, kovetkezo_kar: str) -> float:
        """
        Kiszámítja a P(X_{t+1} = kovetkezo_kar | X_t = aktualis_kar)
        feltételes valószínűséget.
        """
        if not self.tanitott:
            raise RuntimeError("A modellt először tanítani kell a .tanitas() metódussal!")

        kovetkezo_darab = self.atmenet_szamlalo[aktualis_kar][kovetkezo_kar]
        osszes_kimeno = sum(self.atmenet_szamlalo[aktualis_kar].values())

        if osszes_kimeno == 0:
            return 0.0

        szamlalo = kovetkezo_darab + self.alpha
        nevezo = osszes_kimeno + (self.alpha * self.abeceszam)
        return szamlalo / nevezo

    def top_kovetkezo_karakterek(self, aktualis_kar: str, top_n: int = 5) -> List[Tuple[str, float, int]]:
        """
        Visszaadja az adott karaktert leggyakrabban követő karaktereket.
        """
        eredmenyek = []
        for kov_kar, db in self.atmenet_szamlalo[aktualis_kar].most_common(top_n):
            p = self.felteteles_valoszinuseg(aktualis_kar, kov_kar)
            eredmenyek.append((kov_kar, p, db))
        return eredmenyek

    def jelszo_valoszinusege_es_entropiaja(self, jelszo: str) -> Tuple[float, float, float]:
        """
        Kiszámítja egy konkrét jelszó:
        1. Markov-lánc szerinti együttes valószínűségét: P(w)
        2. Markov-alapú entrópiáját (bitben): -log2(P(w))
        3. Naiv brute-force entrópiáját (bitben): L * log2(N)
        """
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
        Kiszámítja az adatbázisra jellemző:
        - Elsőrendű Shannon-entrópiát: H(X)
        - Markov-lánc feltételes entrópiáját: H(X_{t+1} | X_t)
        """
        h_shannon = 0.0
        for kar, db in self.karakter_szamlalo.items():
            p_x = db / self.osszes_karakter
            h_shannon -= p_x * math.log2(p_x)

        h_markov = 0.0
        osszes_atmenet = sum(sum(c.values()) for c in self.atmenet_szamlalo.values())

        for aktualis_kar, kovetkezo_dict in self.atmenet_szamlalo.items():
            kimeno_db = sum(kovetkezo_dict.values())
            if kimeno_db == 0:
                continue
            p_x = kimeno_db / osszes_atmenet

            h_y_adott_x = 0.0
            for kov_kar, db in kovetkezo_dict.items():
                p_y_adott_x = db / kimeno_db
                h_y_adott_x -= p_y_adott_x * math.log2(p_y_adott_x)

            h_markov += p_x * h_y_adott_x

        return h_shannon, h_markov


def main():
    print("=" * 72)
    print(" 13. FELADAT: JELSZÓ-ENTRÓPIA ÉS MARKOV-LÁNC ALAPÚ MODELL")
    print("=" * 72)

    # 1. Adatbázis előállítása, szabályok ellenőrzése és modell tanítása
    jelszavak = general_jelszo_minta(elemszam=5000, seed=42)
    modell = JelszoMarkovModell(simitas_alpha=0.0)
    modell.tanitas(jelszavak)

    szabalyos_db = sum(1 for pw in jelszavak if megfelel_a_szabalynak(pw))
    spec_db = sum(1 for pw in jelszavak if any(c in SPECIALIS for c in pw))
    hosszak = [len(pw) for pw in jelszavak]

    print(f"\n[1] ADATBÁZIS ÉS JELSZÓSZABÁLY STATISZTIKÁK")
    print(f"  - Elemzett jelszavak száma          : {len(jelszavak)} db")
    print(f"  - Jelszóhossz tartomány (min - max) : {min(hosszak)} - {max(hosszak)} karakter")
    print(f"  - Szabálynak megfelelő jelszavak    : {szabalyos_db}/{len(jelszavak)} db (100.0%)")
    print(f"    (6-18 karakter, min. 1 kisbetű, min. 1 nagybetű, min. 1 szám)")
    print(f"  - Speciális karaktert is tartalmaz  : {spec_db}/{len(jelszavak)} db ({spec_db / len(jelszavak) * 100:.1f}% - opcionális)")
    print(f"  - Összes elemzett karakter          : {modell.osszes_karakter} db")
    print(f"  - Egyedi karakterek száma (Ábécé)   : {modell.abeceszam} db")
    print(f"    (26 kisbetű + 26 nagybetű + 10 szám + 32 speciális karakter)")

    # 2. Konkrét kérdés megválaszolása: P('b' | 'a')
    p_ab = modell.felteteles_valoszinuseg('a', 'b')
    a_osszes = sum(modell.atmenet_szamlalo['a'].values())
    ab_db = modell.atmenet_szamlalo['a']['b']

    print(f"\n[2] FELTÉTELES VALÓSZÍNŰSÉG VIZSGÁLATA ('a' -> 'b')")
    print(f"  - Az 'a' karakter után álló karakterek száma összesen : {a_osszes} db")
    print(f"  - Ebből közvetlenül 'b' karakter következik           : {ab_db} db")
    print(f"  - P(X_{{t+1}} = 'b' | X_t = 'a') = {p_ab:.4f} ({p_ab * 100:.2f}%)")

    print(f"\n[3] LEGGYAKORIBB FOLYTATÁSOK AZ 'a' KARAKTER UTÁN (TOP 5)")
    for kov_kar, valsz, db in modell.top_kovetkezo_karakterek('a', top_n=5):
        print(f"  - 'a' -> '{kov_kar}' : P = {valsz:.4f} ({valsz * 100:5.2f}%) | ({db} előfordulás)")

    # 3. Korpusz szintű entrópia összehasonlítás
    h_shannon, h_markov = modell.korpusz_entropia_rata()
    print(f"\n[4] KARAKTERENKÉNTI ENTRÓPIA ÖSSZEHASONLÍTÁSA")
    print(f"  - Egyenletes eloszlás (log2({modell.abeceszam}))      : {math.log2(modell.abeceszam):.2f} bit/karakter")
    print(f"  - Független karakterek (Shannon H(X)) : {h_shannon:.2f} bit/karakter")
    print(f"  - Markov-lánc feltételes H(X_{{t+1}}|X_t) : {h_markov:.2f} bit/karakter")
    print(f"  -> A karakterek közti függőség {((h_shannon - h_markov) / h_shannon) * 100:.1f}%-kal csökkenti a bizonytalanságot!")

    # 4. Szabályos jelszavak feltörési nehézségének összevetése (speciális karakterrel és anélkül)
    teszt_jelszavak = ["Abrakadabra123", "Balaton2024!", "Qwerty12", "X9#q7$Z2!k8&M4"]
    print(f"\n[5] SZABÁLYOS JELSZAVAK VALÓDI (MARKOV) VS. NAIV (BRUTE-FORCE) ENTRÓPIÁJA")
    print(f"  {'Jelszó':<18} | {'Hossz':<5} | {'Naiv entrópia':<15} | {'Markov entrópia':<17} | {'Log10 P(jelszó)'}")
    print("  " + "-" * 78)
    for pw in teszt_jelszavak:
        p_w, h_m, h_n = modell.jelszo_valoszinusege_es_entropiaja(pw)
        log10_p = math.log10(p_w) if p_w > 0 else float('-inf')
        print(f"  {pw:<18} | {len(pw):^5} | {h_n:>9.2f} bit  | {h_m:>11.2f} bit  | {log10_p:>10.2f}")


if __name__ == "__main__":
    main()