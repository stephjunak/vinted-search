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
5. Correction des badges 📌 « marques déjà utilisées »

Pas de déploiement en ligne : usage 100% local (fichier HTML ouvert directement + proxy Python lancé à la main).

## Historique des sessions

- **2026-07-26** : marque « fantôme » indélogeable, symptôme et correctif de fond. Symptôme rapporté : dans les recherches PREF, la marque « Creeks » (id 262) ressortait dans l'URL Vinted alors qu'elle n'apparaissait pas dans la liste des marques. Cause : une fiche marque erronée (`{"name": "K&us", "vinted_name": "Creeks", "id": 262}`, nom local différent de la marque Vinted réelle) avait été supprimée du catalogue alors qu'elle était encore utilisée dans 3 recherches (PREF robes, PREF jupes, PREF hauts). L'id 262 restait stocké dans `state.brands` de ces recherches, invisible car `buildBrands()` ne dessine une case que pour les marques présentes dans le catalogue, donc impossible à décocher, et il ressortait quand même dans l'URL via `buildParamsFromState()` qui lit `state.brands` en direct. Réparation des données : id 262 retiré des 3 recherches PREF directement dans Supabase (105 → 104 marques chacune), backup conservé, vérifié en base. Correctif de fond : `deleteBrand()` supprime désormais en cascade. Avant suppression, il liste dans la confirmation les recherches qui utilisent la marque, puis retire l'id du catalogue ET de toutes les recherches enregistrées (localStorage + Supabase, comme `deleteSearch()`), et décoche la marque dans l'édition en cours si besoin. La comparaison des ids se fait via `Number()` pour couvrir les ids stockés en texte. Plus aucune marque fantôme possible. Logique de cascade testée à blanc sur données synthétiques, aucune erreur console.
- **2026-07-22** : correction des badges 📌 « marques déjà utilisées ». Rappel du fonctionnement voulu, une case cochée signifie « marque présente dans la recherche en cours », et les marques utilisées dans les *autres* recherches sont signalées par un badge 📌 qui les nomme (jamais par une case cochée). Deux bugs, tous deux dus au même schéma : `buildBrands()` était appelé avant que `activeSearchName` soit à jour, donc la liste était dessinée en croyant éditer la recherche précédente. Dans `newSearch()`, `setEditMode(null)` est remonté avant `buildBrands()` (sinon les marques de la recherche qu'on venait de quitter perdaient leur 📌). Dans `loadSearch()`, `setEditMode(name)` est remonté avant `setState()` (sinon la recherche ouverte s'auto-signalait avec son propre nom, et la précédente perdait son 📌). `saveSearch()`, `duplicateSearch()` et `deleteSearch()` faisaient déjà l'ordre correct. Vérifié en conditions réelles sur les 4 recherches chargées depuis Supabase, en lecture seule (aucune des fonctions touchées n'écrit).
- **2026-07-03** : ajout de la sélection des catégories parentes. Quand une catégorie a des sous-catégories ET son propre ID catalogue, le sous-menu affiche en premier une option « … (toutes) » cochable, qui envoie l'ID du parent (ex : « Chaussures (toutes) » → `catalog[]=16`). Avant, seul le choix d'une sous-catégorie était possible. Touche `getCatIds()` (renvoie l'ID du parent même s'il a des enfants), `buildCategories()` (rend l'option « (toutes) » quand le parent a un ID) et `toggleCat()` (pastille parente marquée active si le parent OU un enfant est coché). Aucun impact sur les données. Vérifié en conditions réelles (catégories chargées depuis Supabase).
- **2026-07-01** : incident de perte de données (les recherches sauvegardées `vintedSearches` se sont retrouvées vides en local et sur Supabase ; marques, catégories et étiquettes intactes). Cause : synchro aveugle, le vide pouvait écraser le plein dans les deux sens. Correctif appliqué et testé en conditions réelles contre la base Supabase : `sbLoad()` ne remplace plus une valeur locale non vide par une valeur Supabase vide ; `sbSave()` demande confirmation avant d'écraser une valeur Supabase non vide par du vide. Les recherches perdues n'ont pas pu être récupérées (pas de Time Machine, pas d'export JSON existant).

## Bugs connus / backlog

- **Chemin du proxy incorrect à deux endroits** :
  - Dans `vinted-search.html`, la fonction `copyProxyCommand()` (~ligne 1578) copie la commande avec le chemin `/Users/stephanie/Documents/Claude/app favoris/vinted_proxy.py` — mauvais dossier (`app favoris` au lieu de `app Vinted recherche`) et chemin obsolète (le projet est maintenant sous `Projects/`).
  - `commande python.rtf` contient aussi un chemin obsolète (`/Users/stephanie/Documents/Claude/app Vinted recherche/...` sans `Projects/`).
  - À corriger : chemin réel actuel = `/Users/stephanie/Documents/Claude/Projects/app Vinted recherche/vinted_proxy.py`.
- **Badge 📌 peu visible** : le badge « déjà utilisée » est un texte discret en bout de ligne, noyé dans une liste de ~190 marques. C'est probablement pour ça que le bug d'ordre d'appel corrigé le 2026-07-22 est passé inaperçu si longtemps. Piste : le rendre plus lisible (contraste, position, ou compteur en tête de liste).
