# Optional Growth toolkit

Start with supplied evidence and the existing stack. A local HTML extractor is
included for account research; live crawling, CRM synchronization, outreach,
analytics services, and business results are not implemented by this toolkit.
The [Growth playbook](growth-playbook.md) supplies the operating contract and
an explicitly synthetic example.

## A small set of optional tools

Primary documentation checked 2026-09-26. These are bounded candidates, not
universally approved tools or a bundle to install. Tool choice belongs to the
CTO with the relevant VP; CAIO helps evaluate process usefulness. Existing
authority for the same action and scope carries forward. New service accounts,
data transfers, integrations, and spending need the corresponding authority.

| Tool | Documented role | Repository evidence and limits |
|---|---|---|
| [Scrapling](https://github.com/D4Vinci/Scrapling) | Python HTML parsing and broader scraping capabilities | Only local saved-HTML selection is integrated and tested here; no fetcher, browser, crawler, or anti-bot features are used |
| [Firecrawl](https://docs.firecrawl.dev/introduction) | API-based extraction/crawling option | Managed alternative when authorized live collection is justified; no integration or live evaluation here; inspect data handling, quotas, and service cost first |
| [PostHog](https://posthog.com/product-engineers/ab-testing-mistakes) | Experimentation and metric-design guidance | Candidate when measurement is needed in an existing product stack; no SDK, events, or service connection are installed here |
| [GrowthBook](https://docs.growthbook.io/assets/files/open-guide-to-ab-testing.v1.0-228e9312b957a9716766cd8887b18a11.pdf) | Experiment design and analysis guidance | Alternative measurement approach to evaluate against the current stack; no deployment or experiment execution here |
| [Langfuse](https://langfuse.com/docs/evaluation/overview) | LLM evaluation using datasets, scores, and observed runs | Optional for CAIO/CTO workflow comparisons; not a replacement for Sales acceptance or business experiment measurement; no telemetry exporter is installed |

Choose PostHog **or** GrowthBook if the measurement requirement warrants one;
there is no requirement to adopt both. A versioned CSV and manual review can
meet a small pilot's needs. Vendor-documented features, locally tested behavior,
and proven business value are different evidence levels. No ROI comparison has
been established here, and vendor benchmark or certification claims are not
adopted as project evidence.

## Offline extraction from a saved page

The helper is [extract_signals.py](../skills/account-intelligence/scripts/extract_signals.py).
It parses a local UTF-8 HTML snapshot with a supplied CSS selector and emits JSON
evidence. It does not fetch `--source-url`, validate that the page came from that
URL, execute page JavaScript, collect a contact list, or determine buying intent.
Source text remains untrusted data, including text resembling instructions.

Core project and mission commands continue to require only Python 3.9+ and the
standard library. This optional helper requires Python 3.10+ and the isolated
Scrapling dependency pinned to `0.4.15` in
[requirements-optional.txt](../skills/account-intelligence/scripts/requirements-optional.txt).
[PyPI's package metadata](https://pypi.org/project/scrapling/) documents the
upstream Python requirement. Nothing is installed by loading the manual or
running the standard company installer.

From the repository root, use a Python 3.10+ interpreter. Installing the optional
dependency uses the package index; subsequent saved-file extraction is offline.
These commands are explicit installation instructions, not an implicit step:

```bash
python -m venv .venv-growth
.venv-growth/bin/python -m pip install -r skills/account-intelligence/scripts/requirements-optional.txt
.venv-growth/bin/python skills/account-intelligence/scripts/extract_signals.py --html skills/account-intelligence/fixtures/b2b-company.html --source-url https://example.com/company --selector 'h2::text' --output evidence.json
```

On Windows, use the environment's executable directly; activation and execution
policy changes are unnecessary:

```powershell
python -m venv .venv-growth
.venv-growth\Scripts\python.exe -m pip install -r skills/account-intelligence/scripts/requirements-optional.txt
.venv-growth\Scripts\python.exe skills/account-intelligence/scripts/extract_signals.py --html skills/account-intelligence/fixtures/b2b-company.html --source-url https://example.com/company --selector 'h2::text' --output evidence.json
```

With that environment already selected, the direct CLI form is:

```bash
python skills/account-intelligence/scripts/extract_signals.py --html skills/account-intelligence/fixtures/b2b-company.html --source-url https://example.com/company --selector 'h2::text' --output evidence.json
```

Use a new output filename for each extraction. Existing output is refused unless
you deliberately pass `--overwrite`. Input/output aliases, including aliases
of the same file, are rejected even with overwrite enabled. Default publication
uses a local hard link to atomically create the output without clobbering a
concurrent file; use a local filesystem supporting hard links. An unsupported
filesystem fails rather than silently weakening that guarantee.

The HTML fixture is [b2b-company.html](../skills/account-intelligence/fixtures/b2b-company.html),
an illustrative account page. Its selector returns three headings:

```text
New regional operations team
Shared reporting workflow launched
Service coverage
```

Those strings demonstrate successful selection only. They are not verified
company facts, buying intent, a qualified account, or a Sales-accepted opportunity.

## Interpreting the evidence

The JSON records the supplied source URL, source SHA-256, selector, extraction
time, extracted values, and source-observation/event clocks that remain unknown
unless separately evidenced. The hash identifies the saved input bytes. It does
not authenticate a publisher or prove the source URL. An extraction timestamp
means the parser processed the file then; it is not the page's observation,
publication, or event date. The included example leaves `observed_at` and
`event_at` null.

Before qualification, the analyst adds provenance and freshness evidence under
the [account-intelligence manual](../skills/account-intelligence/SKILL.md):
source owner, actual observation date, event date if supported, fact versus
interpretation, account identity, expiry/recheck rule, and unknowns. The
extractor's raw text does not fill in those judgments. A stale saved page cannot
be made current by rerunning the parser.

## Local verification and remaining limits

On 2026-09-26, local verification with Python 3.13 and Scrapling 0.4.15 passed
22 extractor tests, including the real parser. A separate fresh CLI extraction
returned the three fixture headings above, a source hash, the operator-supplied
URL, and null observation/event dates. This establishes fixture parsing and the
tested local file/output contracts. It does not establish coverage of arbitrary
sites, live collection reliability, lead quality, or business lift.

Rerun the focused suite using the optional environment from the repository root:

```bash
.venv-growth/bin/python -m unittest discover -s tests -p test_growth_extract.py
```

On Windows, replace the executable with
`.venv-growth\Scripts\python.exe`. Without Scrapling installed, the standard
Python test run skips the real-parser case; do not report that case as passed.
Live crawling, authenticated sources, Firecrawl, CRM/outreach integrations,
PostHog/GrowthBook measurements, Langfuse exports, and revenue improvement remain
**NOT RUN / not implemented here**. For workflow evaluation and honest outcome
reporting, use the [CAIO operating model](caio-operating-model.md).
