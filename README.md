# LCA Studio

A browser tool for teaching life cycle sustainability assessment. Students build one product system and
examine it from three sides: environmental LCA, social LCA and life cycle costing.

**Live page:** https://YOUR-USERNAME.github.io/lca-studio/

Built for **H2VE Module 3** (German Centre of Vocational Excellence, Erasmus+ 101194163), Sustainable
Technologies Laboratory, Hochschule Bochum.

## What it does

* **Environmental LCA**, the seven ISO 14040/14044 steps: goal and scope, functional unit, system boundary,
  inventory, impact assessment, results, interpretation. Six ReCiPe 2016 midpoint categories.
* **Social LCA**, structured as UNEP (2020) prescribes: stakeholder, subcategory, indicator. Risk levels use
  the PSILCA v4.0 reference scales. You enter the country values yourself.
* **Life cycle costing**, six steps with explicit cost timing, discounting, residual value and sensitivity.
* **Compare**, the three sets of results side by side, in their own units, never added into one score.
* **Class**, a short result code per group and a facilitator scoreboard.
* **Learn**, a glossary and 29 explainers. Any underlined term opens an explanation with an example.

Results are never combined into a single sustainability score, and a stage outside the system boundary is
reported as excluded, not as zero.

## Use it

Open the live page in any browser, or download `index.html` and double-click it. One file, no build step, no
dependencies, no account, no network. Your work is kept in the browser; **Save study file** writes a JSON you
can reopen anywhere.

Load example gives a worked 12-process study: a 10 kW PEM stack made in Germany, run on a solar mini-grid in
Ghana. New study starts empty.

## In class

The last step of the environmental workflow ends with **Send your result to the class**: a name field, a
28-character result code, and one button that copies both as one line.

```
Group A  1103-90B4-HBAJ-01X0-004S-S1E0-FK8A
```

The facilitator pastes those lines into the **Class** tab and gets a scoreboard with charts. Groups appear in
the same chart only when their functional unit, boundary and method match; the rest stay in the table and the
view says what differs. A mistyped code is caught by a check character.

The code holds headline results and scope only. It has no personal data and cannot be turned back into a model.
For marking, collect the JSON study file or the exported report.

## Reports

The interpretation step exports the whole study as **HTML** or **Word (.docx)**, with the product system
diagram, the impact charts, the social risk chart and the cost timeline embedded as figures.

## Your own data

The built-in factors are indicative teaching values, not dataset values. Each carries a note saying where its
order of magnitude comes from. To work with real numbers, import a CSV in step 4 of the environmental
workflow: see [`data-import/GETTING_DATA.md`](data-import/GETTING_DATA.md).

Imported files are read in the browser and never uploaded. Values derived from ecoinvent or any licensed
database stay on your machine and must not be committed here or handed to students.

## Data and sources

| Content | Source |
|---|---|
| Method and terminology | ISO 14040:2006, ISO 14044:2006 |
| Impact categories | ReCiPe 2016 midpoint (H), EF 3.1, IPCC AR6 GWP100 |
| Social framework | UNEP (2020) Guidelines for Social LCA, ISO 14075:2024 |
| Social reference scales | PSILCA v4.0 manual, evaluation schemas only, no country data |
| Costing | Conventional and environmental LCC, discounted cash flow |
| Built-in factors | Indicative teaching values, each with a provenance note in the tool |

## Limits

* Built-in factors are teaching values, not dataset values.
* The inventory is single level: each flow links to an aggregated dataset rather than a traced background
  system. It teaches the method; it does not replace openLCA or Brightway.
* Uncertainty, normalisation and weighting are not implemented.
* Imported data live in one browser profile. Save to JSON to move a study between machines.

## Files

| Path | What it is |
|---|---|
| `index.html` | The whole application |
| `data-import/GETTING_DATA.md` | How to get factors out of openLCA |
| `data-import/studio_dataset_template.csv` | Template to fill by hand |
| `data-import/export_studio_datasets.py` | Optional script, openLCA IPC server |
| `teaching/` | Guided task, student and answer versions |

## Publishing it

Put these files in a repository, then Settings, Pages, Deploy from a branch, `main`, `/ (root)`. The empty
`.nojekyll` file is already here so GitHub serves the page as written.

## Licence

Code: MIT, see `LICENSE`. Teaching text and task sheets: CC BY 4.0. Cite as:

> Effah, E., & Devarajan, S. K. (2026). *LCA Studio: a teaching platform for environmental life cycle
> assessment, social life cycle assessment and life cycle costing*
> Sustainable Technologies Laboratory, Hochschule Bochum University of Applied Sciences. Developed within
> H2VE, Erasmus+ project 101194163. https://e-effah.github.io/lca-studio/

