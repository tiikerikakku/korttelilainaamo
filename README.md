# korttelilainaamo

Verkkosovellus, jossa käyttäjät voivat tarjota esineitään lainaan omalla postinumeroalueellaan.

### status 7.4.2024

Sovelluksen perusominaisuuksia on lisäilty ja ns. runko on olemassa ja odottaa nyt jatkokehitystä. Kaikkia ominaisuuksia ei ole toteutettu vielä, ja olemassaoleviin ominaisuuksiin pitää tehdä viilauksia, esim. validointia (nyt toteutettu vain selaimen puolella) ja erilaisten mahdollisten virheiden käsittelyä. Alla olevaan listaan on merkitty missä vaiheessa toiminnot ovat.

Tavoiteena on, että parin viikon päästä kaikki toiminnot ovat käytettävissä ja (kunnolla) tominnassa. Sitten viilausta...

## toiminnot 11.4.2024

* rekisteröityminen (mm. oman postinumeron ilmoittaminen) **TOTEUTETTU**
* esineen lisääminen **TOTEUTETTU**
* listaus oman postinumeroalueen vapaana olevista esineistä **TOTEUTETTU**
* lainauspyyntö & hyväksyntä/hylkäys **TOTEUTETTU**
* lainan palauttaminen **TOTEUTETTU**
* arvioinnit (lainaaja & lainaava) **OSIN TOTEUTETTU**, pitää vielä näyttää tieto käyttäjille
* omien tietojen ja esineiden tietojen muokkaaminen
* esineen poistaminen?
* käyttäjän poistaminen?

Muita toimintoja tarpeen ja mahdollisuuksien mukaan...

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
