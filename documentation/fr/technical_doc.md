# Documentation technique

## Architecture

Le depot reprend la structure d'une integration complete d'algorithme externe :

- `__init__.py` enregistre la factory dans `VThermAPI`
- `factory.py` expose l'identifiant utilise par VT pour instancier le handler
- `handler.py` implemente le cycle de vie attendu par `InterfacePropAlgorithmHandler`
- `hysteresis/controller.py` contient la loi de regulation isolee
- `config_flow.py` fournit les entrees globales et par thermostat

## Contrat d'interface

Le handler implemente les methodes suivantes de `vtherm_api.interfaces.InterfacePropAlgorithmHandler` :

- `init_algorithm`
- `async_added_to_hass`
- `async_startup`
- `remove`
- `control_heating`
- `on_state_changed`
- `on_scheduler_ready`
- `should_publish_intermediate`

Chaque methode est conservee dans le scaffold meme quand le cas hysteresis ne demande pas de logique complexe, afin de montrer ou se place chaque point d'extension.

## Interaction avec le scheduler

Le controleur ne commute pas le materiel directement. Il calcule un `on_percent` et transmet cette consigne au cycle scheduler VT :

- `max_on_percent` est envoye quand la chauffe est active (defaut `1.0`)
- `min_on_percent` est envoye quand le controleur est inactif (defaut `0.0`)

Les deux valeurs sont configurables par thermostat, permettant par exemple de plafonner la puissance de chauffe a 80 % ou de maintenir une vanne legerement ouverte en veille.
