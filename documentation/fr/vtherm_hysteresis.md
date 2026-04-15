# Hysteresis

## Objectif

Cette integration expose un controleur de chauffage a hysteresis simple a Versatile Thermostat via l'API d'algorithmes externes.

Elle est volontairement simple et sert de reference pour les developpeurs qui veulent brancher un autre algorithme dans VT.

## Parametres

### Ecart de remise en chauffe

Quand la temperature de la piece descend sous `target - hysteresis_on`, le controleur demande la chauffe.

### Ecart de coupure chauffage

Quand la temperature de la piece depasse `target + hysteresis_off`, le controleur demande l'arret.

## Modes de configuration

Le config flow supporte deux portees :

- des valeurs globales appliquees quand aucune entree specifique au thermostat n'existe
- des reglages specifiques a une entite VT

## Persistance

L'etat du relais est conserve dans le stockage Home Assistant pour reprendre avec un etat coherent apres redemarrage.
