# Chaîne YouTube en pilote automatique (Edunos Studio)

Claude Code fabrique et publie un Short 3 fois par semaine (mardi, jeudi et samedi, vers 17 h 40 UTC, soit 18 h 40 à Paris en hiver). Ce qu'il fait à chaque lancement est décrit dans [`PLAYBOOK.md`](PLAYBOOK.md). Le premier épisode est dans [`episodes/001-paper-boat/video.mp4`](episodes/001-paper-boat/video.mp4).

- `render.mjs`: dessine les images d'un épisode (Chromium headless).
- `make.sh`: images + son + ffmpeg → `video.mp4` (normalisé à −14 LUFS).
- `upload.py`: liste les vidéos déjà postées / envoie une vidéo (API YouTube, sans dépendance). Test : `python3 test_upload.py`.

## Mise en route (une seule fois, environ 20 minutes, gratuit)

Ces étapes demandent ton identité ou ton compte Google : Claude ne peut pas les faire à ta place.

1. **Créer la chaîne** sur youtube.com → photo de profil → *Créer une chaîne*. Nom : **Edunos Studio**, identifiant : `@edunosstudio`. Description à coller :
   > One prompt. One video. Every Short here was made 100% by Claude Code: it writes the code that draws every frame and makes the sound. No app, no editing, no AI video model. Learn how: Prompt to Reel → https://edunosstudio.gumroad.com/l/prompt-to-reel
2. **Google Cloud** (console.cloud.google.com, avec le même compte Google, sans carte bancaire) :
   1. Créer un projet, par exemple « edunos-youtube ».
   2. *API et services → Bibliothèque* → activer **YouTube Data API v3**.
   3. *Écran de consentement OAuth* : type **Externe**, nom de l'appli, ton e-mail. Puis **Publier l'application** (passer en production). En mode *Test*, l'autorisation expire au bout de 7 jours.
   4. *Identifiants → Créer → ID client OAuth*, type **Application Web**. Dans *URI de redirection autorisés*, ajouter `https://developers.google.com/oauthplayground`. Noter l'**ID client** et le **code secret**.
3. **Obtenir le jeton** sur https://developers.google.com/oauthplayground :
   - Roue dentée → cocher *Use your own OAuth credentials* → coller l'ID client et le secret.
   - À gauche, taper le scope `https://www.googleapis.com/auth/youtube` → *Authorize APIs* → choisir le compte de la chaîne. Si Google affiche « appli non validée », cliquer *Paramètres avancés → Continuer* : c'est ton appli.
   - *Exchange authorization code for tokens* → copier le **Refresh token**.
4. **Ranger les 3 secrets dans l'environnement Claude** (menu de l'environnement cloud dans la barre de titre de la session → *Modifier* → variables d'environnement) :
   ```
   YT_CLIENT_ID=...
   YT_CLIENT_SECRET=...
   YT_REFRESH_TOKEN=...
   ```
   Ne les colle jamais dans le chat.
5. **Audit YouTube** (pour que les vidéos sortent en public) : les projets Google Cloud récents envoient les vidéos en **privé** tant que l'API n'a pas été auditée. Remplir le formulaire gratuit *YouTube API Services – Audit and Quota Extension Form* (lien dans la doc de l'API YouTube, rubrique *Quota and Compliance Audits*). En attendant la réponse (quelques jours à quelques semaines), un appui dans l'appli YouTube Studio suffit pour passer chaque vidéo en public.

Tant que les secrets ne sont pas en place, chaque lancement fabrique quand même la vidéo et te l'envoie pour que tu la postes à la main.
