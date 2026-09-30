"""
Export exactly the datasets you need from openLCA, into the CSV the
LCA Learning Studio imports.

It reads studio_dataset_template.csv, finds the best matching process for each
search term, calculates the chosen LCIA method for 1 unit, and writes the six
indicator values into studio_datasets.csv.

SETUP
    1. openLCA: open your database.
    2. openLCA: Tools -> Developer tools -> IPC Server -> Start (default port 8080).
    3. pip install olca-ipc olca-schema
    4. Put this file next to studio_dataset_template.csv.

USE IT IN THIS ORDER
    python export_studio_datasets.py --list-methods
        Prints the LCIA methods in your database. Copy the one you want.

    python export_studio_datasets.py --method "ReCiPe 2016 Midpoint (H)" --dry-run
        Shows which process each search term matched. No calculation, seconds to run.
        Fix any bad matches by editing the search_in_openlca column, then repeat.

    python export_studio_datasets.py --method "ReCiPe 2016 Midpoint (H)"
        Calculates and writes studio_datasets.csv.

LICENCE
    The output holds values derived from your licensed database. Keep it on this
    machine. Do not send it to students or publish it: they need their own licence.
"""

import argparse
import csv
import sys

try:
    import olca_ipc as ipc
    import olca_schema as o
except ImportError:
    sys.exit("Install the client first:  pip install olca-ipc olca-schema")

IN_CSV = "studio_dataset_template.csv"
OUT_CSV = "studio_datasets.csv"

# Accepted indicator names per Studio column. Add your own spellings if needed.
INDICATORS = {
    "gwp": ["global warming", "climate change", "global warming potential (gwp100)",
            "climate change - total", "ipcc gwp 100a"],
    "ap":  ["terrestrial acidification", "acidification", "acidification potential"],
    "ep":  ["freshwater eutrophication", "eutrophication, freshwater",
            "eutrophication freshwater"],
    "wu":  ["water consumption", "water use", "water scarcity"],
    "fe":  ["fossil resource scarcity", "resource use, fossils",
            "abiotic depletion (fossil fuels)", "fossil depletion"],
    "mr":  ["mineral resource scarcity", "resource use, minerals and metals",
            "metal depletion", "abiotic depletion"],
}
OUT_COLS = ["name", "category", "geography", "unit",
            "gwp", "ap", "ep", "wu", "fe", "mr", "openlca_process", "note"]


def connect(port):
    client = ipc.Client(port)
    try:
        client.get_descriptors(o.ImpactMethod)
    except Exception as exc:
        sys.exit(f"Could not reach openLCA on port {port}. Is the IPC server running?\n  {exc}")
    return client


def score(proc_name, term, geo_wanted, model):
    """Rank a candidate process against the search term. Higher is better."""
    n = (proc_name or "").lower()
    t = term.lower().strip()
    s = 0
    if t in n:
        s += 10
    for word in t.split():
        if word in n:
            s += 1
    if n.startswith("market for") or n.startswith("market group for"):
        s += 4                                    # markets carry the supply mix
    if geo_wanted and geo_wanted.lower() in n:
        s += 3
    if model and model.lower() in n:
        s += 2                                    # e.g. "Cutoff"
    s -= len(n) / 400.0                           # prefer the shorter, plainer name
    return s


def find(client, term, geo, model, cache):
    """Return the best matching process descriptor, or None."""
    if "procs" not in cache:
        cache["procs"] = client.get_descriptors(o.Process)
    best, best_s = None, -99
    for term_part in [t.strip() for t in term.split(" OR ")]:
        for p in cache["procs"]:
            s = score(p.name, term_part, geo, model)
            if s > best_s:
                best, best_s = p, s
    return best if best_s > 0 else None


def pick(impacts, keys):
    for r in impacts:
        nm = (r.impact_category.name or "").strip().lower()
        if nm in keys:
            return r.amount
        for k in keys:                            # tolerate trailing qualifiers
            if nm.startswith(k):
                return r.amount
    return 0.0


def calculate(client, proc, method, amount):
    """Calculate one process for `amount` of its reference flow."""
    setup = o.CalculationSetup(
        target=o.Ref(id=proc.id, ref_type=o.RefType.Process),
        impact_method=o.Ref(id=method.id),
        amount=amount,
    )
    result = client.calculate(setup)
    result.wait_until_ready()
    impacts = result.get_total_impacts()
    result.dispose()
    return impacts


def details(client, proc):
    """Reference unit and location of a process."""
    unit, geo = "", ""
    full = client.get(o.Process, proc.id)
    if full is not None:
        if getattr(full, "location", None) is not None:
            geo = full.location.code or full.location.name or ""
        qref = getattr(full, "quantitative_reference", None)
        if qref is not None and getattr(qref, "unit", None) is not None:
            unit = qref.unit.name or ""
    return unit, geo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--method", default="")
    ap.add_argument("--model", default="Cutoff", help="system model keyword to prefer")
    ap.add_argument("--amount", type=float, default=1.0)
    ap.add_argument("--input", default=IN_CSV)
    ap.add_argument("--output", default=OUT_CSV)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--list-methods", action="store_true")
    args = ap.parse_args()

    client = connect(args.port)

    methods = client.get_descriptors(o.ImpactMethod)
    if args.list_methods or not args.method:
        print("LCIA methods in this database:\n")
        for m in sorted(methods, key=lambda x: x.name or ""):
            print("   " + repr(m.name))
        print("\nRe-run with:  --method \"<one of the names above>\"")
        return

    match = [m for m in methods if (m.name or "").strip() == args.method.strip()]
    if not match:
        sys.exit(f"Method {args.method!r} not found. Run --list-methods to see the exact names.")
    method = match[0]

    with open(args.input, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    print(f"{len(rows)} datasets requested, method: {method.name}\n")

    cache, out, missing = {}, [], []
    for i, r in enumerate(rows, 1):
        term = (r.get("search_in_openlca") or r.get("name") or "").strip()
        if not term:
            continue
        proc = find(client, term, r.get("geography", ""), args.model, cache)
        if proc is None:
            missing.append(term)
            print(f"{i:3}. NO MATCH for {term!r}")
            continue

        if args.dry_run:
            print(f"{i:3}. {term!r}\n       -> {proc.name}")
            continue

        try:
            impacts = calculate(client, proc, method, args.amount)
            unit, geo = details(client, proc)
            rec = {
                "name": r.get("name") or proc.name,
                "category": r.get("category", "Imported"),
                "geography": geo or r.get("geography", ""),
                "unit": unit or r.get("unit", "kg"),
                "openlca_process": proc.name,
                "note": r.get("why_it_is_needed", ""),
            }
            for key, names in INDICATORS.items():
                rec[key] = pick(impacts, [n.lower() for n in names])
            out.append(rec)
            print(f"{i:3}. {rec['name']:<28} {proc.name[:52]:<52} "
                  f"GWP {rec['gwp']:.4g}")
        except Exception as exc:
            missing.append(term)
            print(f"{i:3}. FAILED {term!r}: {exc}")

    if args.dry_run:
        print("\nDry run only. Check the matches above, edit search_in_openlca "
              "where they are wrong, then run again without --dry-run.")
        return

    if not out:
        sys.exit("Nothing exported. Run --dry-run to see what matched.")

    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_COLS)
        w.writeheader()
        w.writerows(out)

    zero = [r["name"] for r in out if r["gwp"] == 0]
    print(f"\nWrote {len(out)} datasets to {args.output}")
    if zero:
        print("Zero climate result, check these: " + ", ".join(zero))
    if missing:
        print("No match or failed: " + ", ".join(missing))
    print("\nImport the file in step 4 of the Studio. Keep it on this machine.")


if __name__ == "__main__":
    main()
