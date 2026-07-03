# App Vinted Recherche

> Source de vérité du projet : état, architecture, backlog. Mis à jour à chaque session de travail.

## Objectif

Outil perso pour construire des recherches Vinted avancées (catégories, sous-catégories, marques, statut, taille, prix, tri), les sauvegarder, et ouvrir directement l'URL Vinted correspondante. Évite de re-cocher les mêmes filtres à chaque fois.

## Architecture

- **`vinted-search.html`** : app single-page (HTML/CSS/JS, pas de build, s'ouvre directement dans le navigateur).
  - Deux onglets : **Mes recherches** (vue maître-détail des recherches sauvegardées) et **Création** (constructeur de filtres).
  - Gestion de catégories (avec sous-catégories et catalog IDs Vinted) et de marques (avec étiquettes, filtres, remplacement en masse) via des modales dédiées.
  - Génère l'URL `https://www.vinted.fr/catalog?...` à partir des filtres sélectionnés (`catalog[]`, `brand_ids[]`, `price_from`, `price_to`, `order`, etc.).
  - **Stockage** : `localStorage` en local, synchronisé vers une table Supabase (`vinted_search_settings`) pour persister entre appareils. Fallback silencieux sur localStorage si Supabase est injoignable.
  - **Export/Import** : bouton pour sauvegarder/recharger toutes les données (recherches, catégories, marques, étiquettes) en JSON.

- **`vinted_proxy.py`** : petit serveur HTTP local (port 8765) à lancer en parallèle (`python3 vinted_proxy.py`). Sert de proxy pour interroger l'API marques de Vinted (`/api/v2/brands`) sans être bloqué par le CORS du navigateur, utilisé par le bouton « 🔍 Chercher ID » dans la gestion des marques.

- **`commande python.rtf`** : pense-bête avec la commande pour lancer le proxy.

## État actuel

Fonctionnel. Historique des commits :
1. Version initiale avec sync Supabase
2. Ajout de la vue « Mes recherches » (maître-détail)
3. Ajout du proxy local de recherche de marques
4. Sélection des catégories parentes (option « (toutes) »)

Pas de déploiement en ligne : usage 100% local (fichier HTML ouvert directement + proxy Python lancé à la main).

## Historique des sessions

- **2026-07-03** : ajout de la sélection des catégories parentes. Quand une catégorie a des sous-catégories ET son propre ID catalogue, le sous-menu affiche en premier une option « … (toutes) » cochable, qui envoie l'ID du parent (ex : « Chaussures (toutes) » → `catalog[]=16`). Avant, seul le choix d'une sous-catégorie était possible. Touche `getCatIds()` (renvoie l'ID du parent même s'il a des enfants), `buildCategories()` (rend l'option « (toutes) » quand le parent a un ID) et `toggleCat()` (pastille parente marquée active si le parent OU un enfant est coché). Aucun impact sur les données. Vérifié en conditions réelles (catégories chargées depuis Supabase).
- **2026-07-01** : incident de perte de données (les recherches sauvegardées `vintedSearches` se sont retrouvées vides en local et sur Supabase ; marques, catégories et étiquettes intactes). Cause : synchro aveugle, le vide pouvait écraser le plein dans les deux sens. Correctif appliqué et testé en conditions réelles contre la base Supabase : `sbLoad()` ne remplace plus une valeur locale non vide par une valeur Supabase vide ; `sbSave()` demande confirmation avant d'écraser une valeur Supabase non vide par du vide. Les recherches perdues n'ont pas pu être récupérées (pas de Time Machine, pas d'export JSON existant).

## Bugs connus / backlog

- **Chemin du proxy incorrect à deux endroits** :
  - Dans `vinted-search.html`, la fonction `copyProxyCommand()` (~ligne 1578) copie la commande avec le chemin `/Users/stephanie/Documents/Claude/app favoris/vinted_proxy.py` — mauvais dossier (`app favoris` au lieu de `app Vinted recherche`) et chemin obsolète (le projet est maintenant sous `Projects/`).
  - `commande python.rtf` contient aussi un chemin obsolète (`/Users/stephanie/Documents/Claude/app Vinted recherche/...` sans `Projects/`).
  - À corriger : chemin réel actuel = `/Users/stephanie/Documents/Claude/Projects/app Vinted recherche/vinted_proxy.py`.
- Pas de backlog fonctionnel identifié au-delà de ce correctif.
