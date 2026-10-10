# Cheddar Smart Hub — public information website

A small, standalone HTML/CSS website prepared for GitHub Pages. It contains
public product information and the Google Calendar privacy policy. It does
not contain the Raspberry Pi application, access credentials, or event data.

Publishing target: the standalone public repository
https://github.com/corbelltony/cheddar-smart-hub, with GitHub Pages serving the
root of the `main` branch. Google OAuth verification is a separate process.

## Files

```text
index.html       Home page
privacy.html     Google Calendar privacy policy
styles.css       Responsive styles and local system fonts
favicon.svg      Local vector brand mark
.nojekyll        Serve static files without Jekyll processing
.gitignore       Exclude credentials and local development artifacts
check_site.py    Dependency-free HTML, link, and security checks
README.md        Local preview and publishing instructions
```

There is no JavaScript, package installation, build step, or external asset
dependency. Links to Google, GitHub, and documentation load only when followed.
All local links use relative paths so they work beneath a GitHub project URL.

## Check and preview locally

Run from this directory with Python 3:

```text
python check_site.py
python -m http.server 8080 --bind localhost
```

Open the server address shown in the terminal, then visit `index.html` and
`privacy.html`. Stop the local preview server with Ctrl+C when finished.
Check narrow and wide browser windows and keyboard navigation.

The checker validates document structure, local resources, cross-page links,
fragment targets, relative project-path links, and the absence of executable
scripts, forms, external asset dependencies, secret patterns, or private
network details. It is a basic validation tool, not a full accessibility or
Google OAuth verification audit.

## GitHub Pages publishing

1. Keep the website in the separate public repository
   `corbelltony/cheddar-smart-hub`. Repository creation and publication require
   the maintainer's authorization.
2. Initialize a new repository from this directory and commit only these
   public website files to `main`. Do not copy an application repository or
   reuse its Git metadata or history.
3. Create the approved public repository and push this website's `main` branch.
4. In GitHub, open Settings > Pages. Select **Deploy from a branch**, then
   branch **main** and folder **/(root)**. Save and wait for the Pages build.
5. Confirm both website URLs work over HTTPS, CSS and the favicon load, and
   navigation resolves beneath the project path:

   - Home: https://corbelltony.github.io/cheddar-smart-hub/
   - Privacy: https://corbelltony.github.io/cheddar-smart-hub/privacy.html

6. Only after the site is live, use the reviewed URLs in Google Cloud's OAuth
   application branding and consent configuration. Confirm the app name,
   developer contact details, access scope, and any domain requirements.

GitHub's publishing-source documentation:
https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## Google OAuth verification is a separate step

Publishing this site does not verify the Google OAuth application. Google's
review may require a developer-owned domain whose ownership can be verified.
Do not assume the default `github.io` project address satisfies that requirement.
Validate the proposed URLs and authorized-domain setup in Google Cloud before
submitting; if required, configure a domain you own for GitHub Pages and update
the canonical links and OAuth branding URLs.

No custom-domain `CNAME` or verification token is included because no owned
domain has been selected. Do not publish an ownership claim or approval badge.

Google's current verification requirements:
https://support.google.com/cloud/answer/13464321

## Basis for the privacy policy

The implementation and its documentation were inspected during preparation.
The current Calendar integration uses the read-only Calendar scope, retrieves
events from the primary calendar, stores OAuth tokens in a private local
directory, and caches event display data in server memory. Cached events can
remain available during synchronization errors. The local dashboard page also
holds event data in memory. There is no persistent event-cache database or file
in this integration.

The policy distinguishes event caching from persistent OAuth token storage,
explains retained setup/migration copies, and separates Google revocation from
local deletion. It does not promise encryption at rest, an exact event-deletion
deadline, or absence of hosting-provider request processing. The maintainer
should keep it synchronized with any future changes to the application.
