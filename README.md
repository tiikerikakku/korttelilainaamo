# korttelilainaamo

Verkkosovellus, jossa käyttäjät voivat tarjota esineitään lainaan omalla postinumeroalueellaan.

### status 5.5.2024

Sovellus on nyt niin valmis kuin se tällä aikataululla voi olla. Alla näkyy toiminnot, jotka ovat käytettävissä.

Viimeisten viikkojen (tai päivien) aikana koodiin on lisätty csrf-tarkistusta ja muita turvallisuuskomponentteja. Nyt sovelluksen pitäisi toivon mukaan olla aika turvallinen.

Parannettavaa löytyy varmasti, mutta ainakin sain suurilta osin toteutettua kaikki toiminnot suunnitellusti.

Kauheasti aikaa meni myös pythonin *tyyli*sääntörikosten korjaamiseen. Toivottavasti en rikkonut mitään sovelluksen osaa tätä tehdessäni...

## toiminnot 5.5.2024

* rekisteröityminen (mm. oman postinumeron ilmoittaminen) **TOTEUTETTU**
* esineen lisääminen **TOTEUTETTU**
* listaus oman postinumeroalueen vapaana olevista esineistä **TOTEUTETTU**
* lainauspyyntö & hyväksyntä/hylkäys **TOTEUTETTU**
* lainan palauttaminen **TOTEUTETTU**
* arvioinnit (lainaaja & lainaava) **TOTEUTETTU**
* omien tietojen ja esineiden tietojen muokkaaminen **TOTEUTETTU**
* esineen poistaminen **TOTEUTETTU**
* yrityskorttelin luominen (lisää tietoa käyttäjän asetussivulla) **TOTEUTETTU**
* yrityskorttelin poistaminen **TOTEUTETTU**

## systeemin käynnistäminen omalla laitteella

Ensimmäinen askel olisi kloonaaminen gitistä. Tai sitten voit vaan ladata koodin zip-tiedostona githubista. Sitten valmistelua:

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install flask Flask-SQLAlchemy psycopg2-binary python-dotenv
```

Seuraavaksi luo tietokanta ja taulut `schema.sql` mukaan. Ja `.env`-tiedosto, minne tulee tarvittavat asetukset, esim. seuraavalla tavalla:

```env
SECRET=indeedverysecret
DATABASE=postgresql:///kl
```

Tässä siis `kl` on tietokannan nimi. Ja tuo `SECRET` ei tosiaan saisi olla arvattavissa (tuotannossa).

Jos kaikki meni oikein, niin koko rojun saa pystyyn seuraavalla komennolla:

```bash
flask run --debug
```

Voilà ! Komentokehotteesta löydät nyt sovelluksen verkko-osoitteen. Onnea testailuun!!
