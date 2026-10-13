# MDPro4 — FAQ & Support

A public community guide for MDPro4, with 54 answers across seven categories, searchable questions, shareable answer links, bug-report guidance and creator resources.

**Live site:** https://elderlich.github.io/MDPro4-FAQ/

The site uses plain HTML, CSS and JavaScript. Python generates the static pages; visitors need no account, server or framework runtime. Answers remain readable when JavaScript is disabled. No analytics or external fonts are loaded.

## Update the guide

1. Edit `content/faqs.json`. Preserve an answer's `id` to keep its existing share links working.
2. Set `updatedAt` to the review date and confirm changed advice against the announced playable build.
3. Run `python build.py` and `python scripts/check_site.py`.
4. Preview with `python -m http.server 8764 --directory docs`, then open `http://localhost:8764`.
5. Commit the source changes together with regenerated `docs/` files and push to `main`.

GitHub Pages publishes from **main / docs**. Configure that source in **Settings → Pages** if it is not already enabled. `.nojekyll` keeps the static output intact.

## Content format

Each answer has `id`, `category`, `title`, `body` and `discordUrl`. The body supports paragraphs, numbered/bulleted lists, bold text, inline code and HTTPS Markdown links. Keep `discordUrl` empty when there is no verified discussion thread; the website link remains available for every answer.

The guide distinguishes ocgcore duels from native-engine Solo, along with their card pools and replay formats. Release-specific instructions must follow the actual published build. Publishing this site does not establish that an unreleased game feature has shipped.

`site.template.html` controls page structure; `assets/` contains the presentation and interactions. `content/bug-report-template.txt` is the downloadable reporting form. `docs/` is generated and committed for GitHub Pages.

## Content and artwork

The answers were adapted from the project's community FAQ and reviewed on 13 October 2026. The banner is a generated decorative image created for this FAQ. The favicon is an original vector mark. The website publishes only player-facing content; local authoring notes and workstation paths are excluded.

MDPro4 is an independent community project, separate from the official Master Duel service. Linked third-party tools and projects retain their respective ownership and licenses.
