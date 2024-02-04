# Zadanie domowe #5
### GoIT moduł 2 web
---
## Część obowiązkowa

[Publiczne API Narodowy Bank Polski](http://api.nbp.pl/#kursyParams) pozwala uzyskać informacje o kursach wymiany gotówki Narodowy Bank Polski w wybranym dniu. 
Archiwum przechowuje dane z ostatnich 4 lat.

Napisz narzędzie konsolowe, które zwraca kursy wymiany EUR i USD Narodowy Bank Polski z ostatnich kilku dni. 
Ustaw ograniczenie, aby narzędzie mogło wyświetlać tylko kursy wymiany z ostatnich 10 dni. Użyj klienta Aiohttp, aby wysłać żądanie do API. 
Postępuj zgodnie z zasadami SOLID podczas pisania zadania. Poprawnie obsługuj błędy zapytań sieciowych.

Program umożliwia podanie argumentów w lini poleceń, określających liczbę dni a także dodatkowe waluty (domyslnie wyświetlane sa kursy dla usd i eur z ostatniego dnia)

Przykłady pracy (dostosowane do rozwiązania)
```
python3 cli_exchange_rate.py
```
```
python3 cli_exchange_rate.py 4
```
```
python3 cli_exchange_rate.py 2 chf 
```
```
python3 cli_exchange_rate.py
```
```
python3 cli_exchange_rate.py chf gbp
```
Przykładowy wynik programu:

```json
[
  {
    '03.11.2022': {
      'EUR': {
        'sale': 39.4,
        'purchase': 38.4
      },
      'USD': {
        'sale': 39.9,
        'purchase': 39.4
      }
    }
  },
  {
    '02.11.2022': {
      'EUR': {
        'sale': 39.4,
        'purchase': 38.4
      },
      'USD': {
        'sale': 39.9,
        'purchase': 39.4
      }
    }
  }
]
```
---
## Część dodatkowa
* Dodaj możliwość wyboru dodatkowych walut w odpowiedziach aplikacji poprzez przekazane parametry narzędzia konsoli;
* Weź czat websocket z materiału wykładowego i dodaj możliwość wprowadzenia polecenia exchange, które pokazuje użytkownikom aktualny kurs wymiany w formacie tekstowym. Wybierz format wyświetlania według własnego uznania;
* Rozszerz dodane polecenie exchange, aby umożliwić użytkownikom przeglądanie kursu wymiany na czacie z ostatnich kilku dni. Przykład exchange 2.
* Użyj pakietów aiofile i aiopath, aby dodać logowanie do pliku, gdy komenda exchange została wykonana na czacie.

