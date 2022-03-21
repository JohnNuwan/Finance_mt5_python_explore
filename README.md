

# Serveur Recherche Finance Analyse Data

---
**Language**  : *Python3*

**PlatForme** : *MetaTrader5*

**Broker** : 

- [*FTMO*](https://www.example.com)
- [*Admiral Market*](https://admiralmarkets.com/start-trading/admiral-invest-stocks-and-etfs?raf=53471867)
- [*VantageFX*](https://www.vantagemarkets.com/forex-trading/forex-trading-account/?affid=58014)

---

### Lib Utiliser:

Pandas

> pour L'analyse des donner en DataFrame

numpy

> Pour Les Calculs 

Ta

> Indicateur Technique

requests

> Requete des Strategies Au serveur

art

> Pour Affichage Dynamique

seaborn

> Pour visualisation de certaine Donnée

uvicorn

> Pour Facilité les traitement avec Fastapi

rich

> Pour retour promp 


schedule
> Pour Planifier des Actions Dans le Temps
---

# Serveur

creation d'un simple serveur pour echange mes donner en temp reel 

donner boursiere , plus retour strategie 
prise de position automatique 
management des position 
recommandation de position 
correlation des different actife

## Création d'une api 

recuperé en temp-reel les donné sous deux forme OHCL et Tick
pouvoir Traité et servire les donner au client 

# Server Route:

- Get /OHLC/{name}/{timeframe}/{num_bars}

- Get /stochc/{name}/{timeframe}/{num_bars}

- Get /sup_res/{name}/{timeframe}/{num_bars}

- Get /ichimoku/{name}/{timeframe}/{num_bars}

- Get /position_total

- Get/positions_en_court


Definition port : *localhost*
Definition host : **8090**


---

