import math
import random
from collections import defaultdict, Counter
from typing import List, Dict, Tuple


def general_jelszo_minta(elemszam: int = 2000, seed: int = 42) -> List[str]:
    """
    Saját, valósághű jelszó-adatbázis generálása gyakori szótári tövekkel,
    magyar/nemzetközi részletekkel, számsorokkal és véletlen karakterekkel.
    """
    random.seed(seed)
    
    szotar_alapok = [
        "abrakadabra", "ablak", "almafa", "admin", "titok", "jelszo",
        "passwort", "password", "baba", "balaton", "budapest", "macska",
        "kutya", "kabelek", "szabadsag", "barat", "csaba", "tabor",
        "qwerty", "asdfgh", "zxcvbn", "dragon", "football", "lovag"
    ]
    utotagok = ["", "1", "12", "123", "1234", "2024", "2025", "99", "00", "!", "ab"]
    
    minta = []
    for _ in range(elemszam):
        valasztas = random.random()
        if valasztas < 0.70:
            # 70%: Szótári alapú jelszó + gyakori utótag
            alap = random.choice(szotar_alapok)
            utotag = random.choice(utotagok)
            jelszo = alap + utotag
        elif valasztas < 0.90:
            # 20%: Két rövid szótöredék összefűzése
            jelszo = random.choice(szotar_alapok)[:4] + random.choice(szotar_alapok)[:4]
        else:
            # 10%: Teljesen véletlenszerű kisbetűs-számos jelszó
            karakterek = "abcdefghijklmnopqrstuvwxyz0123456789"
            hossz = random.randint(6, 10)
            jelszo = "".join(random.choice(karakterek) for _ in range(hossz))
            
        minta.append(jelszo)
        
    return minta


class JelszoMarkovModell:
    """
    Elsőrendű Markov-lánc modell jelszavak karakterátmeneteinek és
    entrópiájának vizsgálatára.
    """
    def __init__(self, simitas_alpha: float = 0.0):
        # simitas_alpha > 0 esetén Laplace-simítást alkalmazunk a 0 valószínűségek elkerülésére
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
            
            # Kezdőkarakter rögzítése
            self.kezdo_szamlalo[jelszo[0]] += 1
            
            # Karakterek és átmenetek rögzítése
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

        # Empirikus (vagy Laplace-simított) valószínűség
        szamlalo = kovetkezo_darab + self.alpha
        nevezo = osszes_kimeno + (self.alpha * self.abeceszam)
        return szamlalo / nevezo

    def top_kovetkezo_karakterek(self, aktualis_kar: str, top_n: int = 5) -> List[Tuple[str, float, int]]:
        """
        Visszaadja az adott karaktert leggyakrabban követő karaktereket,
        valószínűségükkel és előfordulási számukkal.
        """
        eredmenyek = []
        for kov_kar, db in self.atmenet_szamlalo[aktualis_kar].most_common(top_n):
            p = self.felteteles_valoszinuseg(aktualis_kar, kov_kar)
            eredmenyek.append((kov_kar, p, db))
        return eredmenyek

    def jelszo_valoszinusege_es_entropiaja(self, jelszo: str) -> Tuple[float, float, float]:
        """
        Kiszámítja egy konkrét jelszó:
        1. Markov-lánc szerinti együttes valószínűségét: P(w) = P(c_1) * prod P(c_{i+1} | c_i)
        2. Markov-alapú öninformációját / találgatási entrópiáját (bitben): -log2(P(w))
        3. Naiv (független, egyenletes eloszlást feltételező) brute-force entrópiáját (bitben): L * log2(N)
        """
        if not jelszo:
            return 0.0, 0.0, 0.0

        # Kezdőkarakter valószínűsége (minimális simítással ismeretlen karakter esetére)
        osszes_jelszo = sum(self.kezdo_szamlalo.values())
        p_kezdo = (self.kezdo_szamlalo[jelszo[0]] + 1e-6) / (osszes_jelszo + 1e-6 * self.abeceszam)
        
        log2_p = math.log2(p_kezdo)

        for i in range(len(jelszo) - 1):
            p_atmenet = self.felteteles_valoszinuseg(jelszo[i], jelszo[i + 1])
            # Ha az átmenet nem fordult elő a mintában, kis küszöbértéket használunk
            if p_atmenet == 0.0:
                p_atmenet = 1e-6
            log2_p += math.log2(p_atmenet)

        markov_valoszinuseg = 2 ** log2_p
        markov_entropia_bit = -log2_p
        
        # Naiv entrópia: H_naiv = L * log2(|Ábécé|)
        naiv_entropia_bit = len(jelszo) * math.log2(max(self.abeceszam, 2))

        return markov_valoszinuseg, markov_entropia_bit, naiv_entropia_bit

    def korpusz_entropia_rata(self) -> Tuple[float, float]:
        """
        Kiszámítja az adatbázisra jellemző:
        - Elsőrendű Shannon-entrópiát (független karaktereloszlás): H(X)
        - Markov-lánc stacionárius feltételes entrópiáját: H(X_{t+1} | X_t)
        """
        # 1. Karakterek peremeloszlásának Shannon-entrópiája: H(X) = - sum P(x) * log2 P(x)
        h_shannon = 0.0
        for kar, db in self.karakter_szamlalo.items():
            p_x = db / self.osszes_karakter
            h_shannon -= p_x * math.log2(p_x)

        # 2. Feltételes entrópia: H(Y|X) = - sum_x P(x) sum_y P(y|x) log2 P(y|x)
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
    print("=" * 65)
    print(" 13. FELADAT: JELSZÓ-ENTRÓPIA ÉS MARKOV-LÁNC ALAPÚ MODELL")
    print("=" * 65)

    # 1. Adatbázis előállítása és modell tanítása
    jelszavak = general_jelszo_minta(elemszam=5000)
    modell = JelszoMarkovModell(simitas_alpha=0.0)
    modell.tanitas(jelszavak)

    print(f"\n[1] ADATBÁZIS STATISZTIKÁK")
    print(f"  - Elemzett jelszavak száma : {len(jelszavak)} db")
    print(f"  - Összes elemzett karakter : {modell.osszes_karakter} db")
    print(f"  - Egyedi karakterek száma  : {modell.abeceszam} db")

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

    # 4. Konkrét jelszavak feltörési nehézségének (entrópiájának) összevetése
    teszt_jelszavak = ["abrakadabra123", "balaton2024", "qwerty12", "x9q7z2k8m4"]
    print(f"\n[5] JELSZAVAK VALÓDI (MARKOV) VS. NAIV (BRUTE-FORCE) ENTRÓPIÁJA")
    print(f"  {'Jelszó':<18} | {'Naiv entrópia':<15} | {'Markov entrópia':<17} | {'Log10 P(jelszó)'}")
    print("  " + "-" * 70)
    for pw in teszt_jelszavak:
        p_w, h_m, h_n = modell.jelszo_valoszinusege_es_entropiaja(pw)
        log10_p = math.log10(p_w) if p_w > 0 else float('-inf')
        print(f"  {pw:<18} | {h_n:>9.2f} bit  | {h_m:>11.2f} bit  | {log10_p:>10.2f}")


if __name__ == "__main__":
    main()