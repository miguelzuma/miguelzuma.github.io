# miguelzuma.github.io

Personal academic site. Jekyll, built automatically by GitHub Pages — there is
no build step to run before pushing.

## Where things live

| What | File |
|---|---|
| Site-wide settings, affiliation, profile links | `_config.yml` |
| Navigation items | `_data/nav.yml` |
| Group members, visitors, alumni | `_data/people.yml` |
| Projects and funding | `_data/projects.yml` |
| Software cards | `_data/software.yml` |
| Shared page shell | `_layouts/`, `_includes/` |
| Styles | `assets/css/main.css` |
| Page content | `index.html`, `research.html`, `group.html`, `projects.html`, `software.html`, `outreach.html`, `contact.html` |

## Common edits

**Add a group member** — append an entry to `current:` in `_data/people.yml`.
Only `name` is required. Add a square photo to `imgs/collaborators/` and set
`photo: File_Name.jpg`; without one, the card shows initials.

**Someone leaves** — move their entry from `current:` to `alumni:` and add a
`next:` line.

**Add a project or code** — append to `_data/projects.yml` or
`_data/software.yml`. No HTML editing needed.

**Complete the AEI → IFT move** — edit the `affiliation:` block in
`_config.yml`. Every page that shows an affiliation reads from it. The Contact
page also has a hard-coded postal address that needs updating separately.

## Local preview

Requires Ruby with development headers (`sudo apt install ruby-dev
build-essential` on Debian/Ubuntu):

```
bundle install
bundle exec jekyll serve
```

## Conventions

- Body text is left-aligned, never justified.
- Every scientific figure needs descriptive `alt` text; decorative logos take `alt=""`.
- External links opened in a new tab need `rel="noopener"`.
- Prefer HTTPS. Do not add links that are already dead.
