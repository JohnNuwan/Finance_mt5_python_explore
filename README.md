

# Serveur Recherche Finance Analyse Data

---
**Language**  : *Python3*

**PlatForme** : *MetaTrader5*

**Broker** : 

- [*FTMO*](https://trader.ftmo.com)
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


FastAPi
> Pour La Creation De L'api


---

# Serveur

creation d'un simple serveur pour echange données en temp reel 

donner boursiere , plus retour strategie 
prise de position automatique 
management des position 
recommandation de position 
correlation des different actife

## Création d'une api 

recuperé en temp-reel les donné sous deux forme OHCL 

### Server Route:

- Get /OHLC/{name}/{timeframe}/{num_bars}

| Open | High | Low | Close | Volume | Spread |
| ---- | ---- |---- | ----  |---- | ---- | 
| 1.232 | 1.260 | 1.110 | 1.250 | 150 | 9 |

- Get /stochc/{name}/{timeframe}/{num_bars}

	- ajout valeur Stochastique et Signal %K %D Strategy Stochastique

- Get /sup_res/{name}/{timeframe}/{num_bars}

	* Calcule Support Resistance de L'asset , avec Strategy Stochastique et RSI en plus au retourn d'inforamtion

- Get /ichimoku/{name}/{timeframe}/{num_bars}

	* Calcule De l'indicateur Ichimoku, Avec Retour Strategy

- Get /position_total

	* retourne Le Nombres Globales de Positons en court

- Get/positions_en_court

	* Retourne Les Positions en cours sous format Json 


Definition port : *localhost*
Definition host : **8090**


---

