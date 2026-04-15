# Hysteresis

## Objectif

Cette integration expose un controleur de chauffage a hysteresis simple a Versatile Thermostat via l'API d'algorithmes externes.

Elle est volontairement simple et sert de reference pour les developpeurs qui veulent brancher un autre algorithme dans VT.

## Parametres

### Ecart de remise en chauffe

Quand la temperature de la piece descend sous `target - hysteresis_on`, le controleur demande la chauffe.

### Ecart de coupure chauffage

Quand la temperature de la piece depasse `target + hysteresis_off`, le controleur demande l'arret.

### Puissance maximale en chauffe (`max_on_percent`)

La fraction de cycle envoyee au scheduler quand la chauffe est active. La valeur `1.0` correspond a 100 % (defaut). Reduire cette valeur pour les radiateurs a forte inertie thermique afin d'eviter le depassement de consigne, ou pour limiter l'ouverture d'une vanne en mode chauffe.

Plage : `0.0` – `1.0`. Defaut : `1.0`.

### Puissance minimale en refroidissement (`min_on_percent`)

La fraction de cycle envoyee au scheduler quand le controleur est inactif (pas de chauffe). La valeur `0.0` correspond a completement ferme (defaut). Definir une valeur non nulle permet de maintenir une vanne partiellement ouverte en mode refroidissement ou en veille.

Plage : `0.0` – `1.0`. Defaut : `0.0`.

## Modes de configuration

Le config flow supporte deux portees :

- des valeurs globales appliquees quand aucune entree specifique au thermostat n'existe
- des reglages specifiques a une entite VT

## Persistance

L'etat du relais est conserve dans le stockage Home Assistant pour reprendre avec un etat coherent apres redemarrage.
