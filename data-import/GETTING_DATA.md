# Getting data out of openLCA and into the Studio

The Studio ships with about thirty **indicative teaching values**. They are the right order of magnitude but
they are not dataset values. This page explains two ways to replace them with figures from your own licensed
database.

**Licence first.** Values derived from ecoinvent or any licensed database stay on your machine. Do not commit
the exported CSV to this repository and do not hand it to students: each user needs their own licence. The
Studio reads the file in the browser, so nothing is uploaded when you import it.

## Which route to take

| | Route A, by hand | Route B, the script |
|---|---|---|
| Effort | ~2 minutes per dataset | 20 minutes of setup, then minutes of waiting |
| Good for | 20 to 40 datasets, which is plenty for a seminar | 50 to 300 datasets |
| Needs | openLCA only | openLCA, Python, two packages |
| Fails when | you need many datasets | the IPC server or the API version misbehaves |

For teaching, **Route A is usually the right answer.** A student learns more from choosing between five
plausible datasets than from scrolling twenty thousand.

## Route A: by hand, straight from openLCA

Do this once per dataset. Keep `studio_dataset_template.csv` open beside openLCA and fill the six factor columns.

1. **Find the process.** Search the Navigator for the term in the template's `search_in_openlca` column. Prefer
   a `market for …` process, which carries the supply mix, and the geography closest to your case.
2. **Create a product system.** Right-click the process → *Create product system*. Tick *auto-link processes*,
   set the cut-off to `1E-3`, Finish.
3. **Calculate.** On the product system's General information tab click *Calculate*. Choose your method, for
   example ReCiPe 2016 Midpoint (H). Leave normalisation and weighting off. Finish.
4. **Read the Impact analysis tab.** Copy the six totals into the template row:

| Template column | ReCiPe 2016 indicator | Unit |
|---|---|---|
| `gwp` | Global warming | kg CO₂ eq |
| `ap` | Terrestrial acidification | kg SO₂ eq |
| `ep` | Freshwater eutrophication | kg P eq |
| `wu` | Water consumption | m³ |
| `fe` | Fossil resource scarcity | kg oil eq |
| `mr` | Mineral resource scarcity | kg Cu eq |

Faster than typing: on the result page use *Export to Excel*, then copy the six totals across.

5. **Save the template as CSV** and import it in the Studio: environmental tab, step 4, *Import a dataset file*.

### Three things that will bite you

- **The amount must be 1.** The calculation uses the product system's reference amount. If it says 1000 kg,
  every factor comes out a thousand times too high. Check before calculating.
- **Keep one system model.** Cut-off, APOS and consequential give different numbers. Mixing them makes the
  library incoherent. Note which you used in the `basis` column.
- **Iridium does not exist** as its own dataset. That is a real gap in ecoinvent, not a failed search. Use a
  platinum-group-metal proxy and write the substitution down: the Studio shows the note next to the dataset.

## Route B: the script, over openLCA's IPC server

`export_studio_datasets.py` reads the search terms in `studio_dataset_template.csv`, finds the best matching
process for each, calculates the method, and writes `studio_datasets.csv`.

The script runs **on your computer and talks to openLCA**, which must stay open the whole time.

### Setup

1. Open openLCA and open the database.
2. **Tools → Developer tools → IPC Server**, port `8080`, Start. Leave it running.
3. If ecoinvent is slow, raise the memory first: Preferences → Configuration, at least 8 GB, then restart openLCA.
4. Install the client. With Anaconda, use the **Anaconda Prompt**, where the line starts with `(base)`:

```
pip install olca-ipc olca-schema
python -c "import olca_ipc; print('ready')"
```

5. Put `export_studio_datasets.py` and `studio_dataset_template.csv` in one folder and move the terminal there:

```
cd /d C:\Users\YourName\Documents\lca-export
dir
```

`dir` must list both files.

### Run it in three commands

```
python export_studio_datasets.py --list-methods
python export_studio_datasets.py --method "ReCiPe 2016 Midpoint (H)" --dry-run
python export_studio_datasets.py --method "ReCiPe 2016 Midpoint (H)"
```

The first prints the exact method names in your database; copy one, brackets and all. The second takes seconds,
calculates nothing, and shows which process each term matched, so you can correct a bad match in the template
before spending twenty minutes. The third writes the file.

### When it fails

| Message | Cause | Fix |
|---|---|---|
| `Could not reach openLCA on port 8080` | IPC server not started, or a different port | Start it under Tools → Developer tools; or pass `--port` |
| `can't open file …` | terminal is not in the folder | `cd` to the folder, check with `dir` |
| `pip is not recognised` | pip not on the path | `python -m pip install olca-ipc olca-schema` |
| `Method 'X' not found` | spelling differs from your database | run `--list-methods` and copy exactly |
| Runs, but every value is 0 | the method has no factors for those flows, or the process target did not link | check the method matches the database version; tell me and I will add explicit product-system creation |
| `ImportError` on `olca_schema` | openLCA 1.x, which uses the older API | tell me your version and I will adapt the script |

The script never stops on a bad dataset. It reports failures at the end, flags any row whose climate result is
zero, and still writes what worked.

### After the export

Check two things before trusting it:

- The `openlca_process` column records which activity was actually used for each row, so you can see whether
  "platinum" resolved to `market for platinum` or to something unexpected.
- Any row flagged with a zero climate result is suspect. A zero normally means the method had no factors for
  that process, not that the process is clean.

Then import `studio_datasets.csv` in the Studio, environmental tab, step 4.

## What the Studio does with the file

Recognised columns, in any order; anything else is ignored:

| Column | Meaning |
|---|---|
| `name`, `category`, `geography`, `unit` | how the dataset is shown and matched |
| `gwp`, `ap`, `ep`, `wu`, `fe`, `mr` | the six characterisation results, per unit |
| `price` | used by the costing and social pathways; optional |
| `sector` | used for the labour intensity in social LCA; optional |

Imported datasets live in that one browser profile. Save your study to a JSON file to move it between machines,
and re-import the CSV there.
