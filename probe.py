# Copyright 2026 Munim, Inc. (MV2, mv2@munimtech.com)
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in MV2's name; not yet checked by a human expert.
"""Job lrc16-allik-probe-v1: what would 16 runners cost with the best public engine?

Jaan Allikvere's 14/15-runner proof (arXiv:2609.02604) published its full
pipeline on Zenodo under CC BY 4.0:
  10.5281/zenodo.22667683 (fifteen runners: code, logs, 71 gate certificates)
  10.5281/zenodo.22066772 (fourteen runners: generator v6.6, code guide)
This job (see COST.md, Sections 3-4, for what each number is used for):

  1. downloads those files into /data (sha256-checked against SHA256SUMS.txt);
  2. copies every source file, script, README and small log into /out so the
     next run can read the real pipeline, and extracts the per-gate SUMMARY.json
     files and every timing line (cost of the 15-runner gates, stage by stage);
  3. builds the 13-runner-era generator (basegen_v66_lf.cpp) and checks its own
     published regression: p = 43 'both' -> direct = decomp = 163507, missing 0;
  4. builds the campaign generator, cascade and level-15 tool with K = 14 and,
     for 16 runners, K = 15; captures usage and self-tests;
  5. times the generator on a ladder of small primes for K = 14 and K = 15, and
     our own engine (lrc.c, fetched from the public repo) on the same ladder;
  6. if the generator has root/subroot sharding (as v6 does), estimates the
     total level-one cost at real gate primes by timing a random sample of
     subroots (seeded): estimate = (number of subroots) x (mean time).

Nothing here is a proof step: it measures cost, and checks that their code builds
and reproduces their own published numbers.  Everything is best effort: a step
that fails is recorded in summary_probe.json and the job goes on.

  python -I probe.py --data-dir /data --out-dir /out [--budget-min 200]
"""
import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import tarfile
import threading
import time
import urllib.request
import zipfile

Z15 = "https://zenodo.org/records/22667683/files/"
Z14 = "https://zenodo.org/records/22066772/files/"
FILES15 = ["README.md", "SHA256SUMS.txt", "LRC15_AUDIT_SUMMARY.json",
           "audit_lrc14_gates.py", "fifteen_runners_code_and_logs.zip"]
FILES14 = ["CODE_GUIDE.md", "basegen_v66_lf.cpp", "st_benchmark.zip"]
# small 'Div' gates and 'Empty' gates of the 15-runner proof (sizes 0.1-30 MB)
EVIDENCE = [89, 179, 223, 233, 239, 251, 263, 281, 293, 313, 353, 401, 449, 503, 569]
LRC_C = "https://raw.githubusercontent.com/munimtechnologies/lonely-runner-16/main/lrc.c"
UA = {"User-Agent": "lonely-runner-16-probe/1.0 (open research job)"}

# Small primes are skipped on purpose: there the number of improper multisets is
# huge (memory), and the gate primes for 16 runners are >= 251 anyway.  179, 223,
# 233, 239, 251 are 15-runner gates with published orbit counts.
LADDER = [101, 113, 127, 139, 151, 163, 173, 179, 191, 199, 211, 223, 233, 239, 251,
          263, 281, 307]
CHILD_MEM_BYTES = 700_000_000  # address-space cap per engine process (4 run at once)
SAMPLE_TARGETS = [(14, 401), (15, 401), (15, 307), (15, 503), (14, 251), (15, 251)]
SRC_EXT = (".cpp", ".cc", ".c", ".h", ".hpp", ".py", ".sh", ".md", ".tex", ".toml",
           ".cfg", ".yaml", ".yml", ".txt", ".json", ".log", ".csv", ".stats", ".out")
SEED = 20261121

SUMMARY = {"job": "lrc16-allik-probe-v1", "steps": {}}
LOCK = threading.Lock()


# ----------------------------------------------------------------- helpers
def safe_name(name):
    """Relative, normalised member path, or None if it could escape the target."""
    if not name:
        return None
    name = name.replace("\\", "/")
    if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        return None
    parts = [x for x in name.split("/") if x not in ("", ".")]
    if not parts or any(x == ".." for x in parts):
        return None
    return "/".join(parts)


def parse_modes(text):
    """Mode names from a usage line such as 'usage: prog p mode(a|b|c) [args]'."""
    m = re.search(r"mode\s*\(([^)]*)\)", text or "")
    if not m:
        return []
    return [x.strip() for x in m.group(1).split("|") if x.strip()]


def parse_kv(line):
    """'S k=15 p=43 seconds=1.5' -> {'k': '15', 'p': '43', 'seconds': '1.5'}."""
    return dict(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)=(\S+)", line or ""))


def parse_index_lines(text):
    """Leading integers of lines that are exactly 'int int' (index class)."""
    out = []
    for line in (text or "").splitlines():
        m = re.match(r"^\s*(\d+)\s+(\d+)\s*$", line)
        if m:
            out.append(int(m.group(1)))
    return out


def tail(s, n=4000):
    s = s or ""
    return s if len(s) <= n else s[-n:]


def save():
    with LOCK:
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, "summary_probe.json"), "w") as f:
            json.dump(SUMMARY, f, indent=1, default=str)


def step(name, value):
    with LOCK:
        SUMMARY["steps"][name] = value
    save()


def left():
    return DEADLINE - time.time()


def _cap_memory():
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (CHILD_MEM_BYTES, CHILD_MEM_BYTES))
    except Exception:
        pass


def run(cmd, timeout, cwd=None, stdout_path=None, cap=True):
    t0 = time.time()
    rec = {"cmd": [str(c) for c in cmd]}
    pre = _cap_memory if cap else None
    try:
        if stdout_path:
            with open(stdout_path, "w") as fo:
                r = subprocess.run([str(c) for c in cmd], stdout=fo, stderr=subprocess.PIPE,
                                   text=True, timeout=timeout, cwd=cwd, preexec_fn=pre)
            rec["stdout"] = ""
        else:
            r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True,
                               timeout=timeout, cwd=cwd, preexec_fn=pre)
            rec["stdout"] = tail(r.stdout)
        rec["rc"] = r.returncode
        rec["stderr"] = tail(r.stderr)
        rec["timed_out"] = False
    except subprocess.TimeoutExpired:
        rec["timed_out"] = True
    except Exception as e:  # keep going
        rec["error"] = repr(e)
    rec["seconds"] = round(time.time() - t0, 3)
    return rec


def download(url, path, tries=3):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return {"url": url, "cached": True, "bytes": os.path.getsize(path)}
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=600) as r, open(path + ".part", "wb") as f:
                shutil.copyfileobj(r, f, 1 << 20)
            os.replace(path + ".part", path)
            return {"url": url, "cached": False, "bytes": os.path.getsize(path)}
        except Exception as e:
            last = repr(e)
            time.sleep(10 * (i + 1))
    return {"url": url, "error": last}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def find(root, base):
    hits = []
    for d, _, fs in os.walk(root):
        for f in fs:
            if f == base:
                hits.append(os.path.join(d, f))
    return sorted(hits, key=len)


# ----------------------------------------------------------------- stages
def stage_download():
    d15 = os.path.join(DATA, "z15")
    d14 = os.path.join(DATA, "z14")
    os.makedirs(d15, exist_ok=True)
    os.makedirs(d14, exist_ok=True)
    rec = {}
    for f in FILES15:
        rec[f] = download(Z15 + f + "?download=1", os.path.join(d15, f))
    for p in EVIDENCE:
        f = f"evidence_{p}_s0.tgz"
        rec[f] = download(Z15 + f + "?download=1", os.path.join(d15, f))
    for f in FILES14:
        rec["z14/" + f] = download(Z14 + f + "?download=1", os.path.join(d14, f))
    rec["lrc.c"] = download(LRC_C, os.path.join(WORK, "lrc.c"))
    # integrity against the record's own SHA256SUMS.txt
    sums = {}
    try:
        with open(os.path.join(d15, "SHA256SUMS.txt")) as f:
            for line in f:
                m = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$", line)
                if m:
                    sums[os.path.basename(m.group(2))] = m.group(1).lower()
    except Exception as e:
        rec["sha256sums_error"] = repr(e)
    check = {}
    for f in os.listdir(d15):
        if f in sums:
            check[f] = (sha256(os.path.join(d15, f)) == sums[f])
    rec["sha256_checked"] = check
    rec["sha256_all_ok"] = bool(check) and all(check.values())
    step("download", rec)
    return d15, d14


def stage_extract(d15, d14):
    code = os.path.join(WORK, "code")
    os.makedirs(code, exist_ok=True)
    rec = {"zip_members": 0, "skipped_unsafe": 0}
    inv = []
    for zpath, sub in ((os.path.join(d15, "fifteen_runners_code_and_logs.zip"), "z15"),
                       (os.path.join(d14, "st_benchmark.zip"), "z14_st_benchmark")):
        try:
            with zipfile.ZipFile(zpath) as z:
                for info in z.infolist():
                    name = safe_name(info.filename)
                    if info.is_dir():
                        continue
                    if not name:
                        rec["skipped_unsafe"] += 1
                        continue
                    dst = os.path.join(code, sub, name)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    with z.open(info) as src, open(dst, "wb") as f:
                        shutil.copyfileobj(src, f, 1 << 20)
                    rec["zip_members"] += 1
                    inv.append(f"{sub}/{name}\t{info.file_size}")
        except Exception as e:
            rec[f"{sub}_error"] = repr(e)
    for f in ("basegen_v66_lf.cpp", "CODE_GUIDE.md"):
        try:
            os.makedirs(os.path.join(code, "z14"), exist_ok=True)
            shutil.copy(os.path.join(d14, f), os.path.join(code, "z14", f))
        except Exception as e:
            rec[f"z14_{f}_error"] = repr(e)
    for f in ("README.md", "LRC15_AUDIT_SUMMARY.json", "audit_lrc14_gates.py", "SHA256SUMS.txt"):
        try:
            shutil.copy(os.path.join(d15, f), os.path.join(code, "z15", "_record_" + f))
        except Exception as e:
            rec[f"z15_{f}_error"] = repr(e)
    # evidence: small text members only
    ev = os.path.join(WORK, "evidence")
    rec["evidence"] = {}
    for p in EVIDENCE:
        path = os.path.join(d15, f"evidence_{p}_s0.tgz")
        n = 0
        try:
            with tarfile.open(path, "r:*") as t:
                for m in t:
                    name = safe_name(m.name)
                    if not m.isfile() or not name:
                        continue
                    inv.append(f"evidence_{p}/{name}\t{m.size}")
                    if not name.lower().endswith(SRC_EXT) or m.size > 5_000_000:
                        continue
                    dst = os.path.join(ev, str(p), name)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    src = t.extractfile(m)
                    if src is None:
                        continue
                    with open(dst, "wb") as f:
                        shutil.copyfileobj(src, f, 1 << 20)
                    n += 1
            rec["evidence"][p] = n
        except Exception as e:
            rec["evidence"][p] = repr(e)
    with open(os.path.join(OUT, "inventory.txt"), "w") as f:
        f.write("\n".join(inv) + "\n")
    step("extract", rec)
    return code, ev


def copy_capped(src_root, dst_root, budget, max_file, exts, order):
    """Copy text files, the extensions in `order` first, until `budget` bytes."""
    used = 0
    copied = 0
    files = []
    for d, _, fs in os.walk(src_root):
        for f in fs:
            if f.lower().endswith(exts):
                path = os.path.join(d, f)
                files.append(path)

    def rank(path):
        low = path.lower()
        for i, e in enumerate(order):
            if low.endswith(e):
                return (i, os.path.getsize(path))
        return (len(order), os.path.getsize(path))
    for path in sorted(files, key=rank):
        size = os.path.getsize(path)
        if size > max_file or used + size > budget:
            continue
        dst = os.path.join(dst_root, os.path.relpath(path, src_root))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(path, dst)
        used += size
        copied += 1
    return {"copied": copied, "bytes": used, "candidates": len(files)}


def flatten(x, prefix="", out=None):
    out = {} if out is None else out
    if isinstance(x, dict):
        for k, v in x.items():
            flatten(v, f"{prefix}.{k}" if prefix else str(k), out)
    elif isinstance(x, list):
        if len(x) <= 50:
            for i, v in enumerate(x):
                flatten(v, f"{prefix}[{i}]", out)
        else:
            out[prefix + ".len"] = len(x)
    elif isinstance(x, (int, float, bool)) or x is None:
        out[prefix] = x
    elif isinstance(x, str) and len(x) <= 200:
        out[prefix] = x
    return out


TIME_RE = re.compile(r"(?i)(cpu|second|elapsed|wall|runtime|real\s|user\s|time[_ =:]|hours?\b)")


def stage_harvest(code, ev):
    rec = {}
    order = (".cpp", ".cc", ".c", ".h", ".hpp", ".sh", ".py", ".md", ".tex", ".toml",
             ".cfg", ".yaml", ".yml", ".json", ".txt", ".csv", ".stats", ".log", ".out")
    rec["code"] = copy_capped(code, os.path.join(OUT, "allik_code"), 40_000_000, 1_500_000,
                              SRC_EXT, order)
    rec["evidence"] = copy_capped(ev, os.path.join(OUT, "allik_evidence"), 20_000_000, 300_000,
                                  SRC_EXT, (".json", ".txt", ".md", ".log"))
    summaries = {}
    for root in (code, ev):
        for d, _, fs in os.walk(root):
            for f in fs:
                if f.upper().startswith("SUMMARY") and f.lower().endswith(".json"):
                    path = os.path.join(d, f)
                    try:
                        with open(path) as fh:
                            summaries[os.path.relpath(path, WORK)] = flatten(json.load(fh))
                    except Exception as e:
                        summaries[os.path.relpath(path, WORK)] = {"error": repr(e)}
    with open(os.path.join(OUT, "gate_summaries.json"), "w") as f:
        json.dump(summaries, f, indent=1)
    rec["summaries"] = len(summaries)
    lines = []
    for root in (code, ev):
        for d, _, fs in os.walk(root):
            for f in fs:
                if not f.lower().endswith((".log", ".txt", ".json", ".out", ".stats", ".csv", ".md", ".tex")):
                    continue
                path = os.path.join(d, f)
                if os.path.getsize(path) > 20_000_000:
                    continue
                try:
                    with open(path, errors="replace") as fh:
                        for i, line in enumerate(fh):
                            if TIME_RE.search(line):
                                lines.append(f"{os.path.relpath(path, WORK)}:{i + 1}: {line.rstrip()[:300]}")
                                if len(lines) >= 40000:
                                    break
                except Exception:
                    pass
            if len(lines) >= 40000:
                break
    with open(os.path.join(OUT, "timing_lines.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    rec["timing_lines"] = len(lines)
    build_lines = []
    for d, _, fs in os.walk(code):
        for f in fs:
            if f.endswith((".sh", ".py", ".md")):
                try:
                    with open(os.path.join(d, f), errors="replace") as fh:
                        for line in fh:
                            if "g++" in line or "-DK=" in line:
                                build_lines.append(f"{f}: {line.rstrip()[:400]}")
                except Exception:
                    pass
    with open(os.path.join(OUT, "build_lines.txt"), "w") as f:
        f.write("\n".join(build_lines) + "\n")
    rec["build_lines"] = len(build_lines)
    step("harvest", rec)


def stage_build(code):
    b = os.path.join(WORK, "bin")
    os.makedirs(b, exist_ok=True)
    rec = {"cpu_flags": "", "bins": {}}
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("flags"):
                    fl = line.split(":", 1)[1].split()
                    rec["cpu_flags"] = " ".join(x for x in fl if x.startswith(("avx", "bmi", "popcnt")))
                    break
        rec["nproc"] = os.cpu_count()
    except Exception as e:
        rec["cpu_error"] = repr(e)
    bins = {}

    def build(name, cmds):
        tries = []
        for cmd in cmds:
            r = run(cmd, 900, cap=False)
            tries.append(r)
            if r.get("rc") == 0:
                bins[name] = cmd[cmd.index("-o") + 1]
                break
        rec["bins"][name] = {"ok": name in bins, "tries": tries}

    v66 = find(code, "basegen_v66_lf.cpp")
    if v66:
        out = os.path.join(b, "v66n")
        build("v66n", [["g++", "-O3", "-march=native", "-std=c++17", "-o", out, v66[0]],
                       ["g++", "-O3", "-march=native", "-std=c++20", "-o", out, v66[0]],
                       ["g++", "-O3", "-std=c++17", "-o", out, v66[0]]])
    bg = find(code, "basegen_k_campaign.cpp")
    if bg:
        inc = os.path.dirname(bg[0])
        for K in (14, 15):
            out = os.path.join(b, f"bgk{K}")
            base = ["g++", "-std=c++20", "-O3", "-march=native", f"-DK={K}", "-DNW=8",
                    "-DMAXN=512"]
            full = base + ["-DBGK_INCREMENTAL_GAIN", "-DBGK_DEFERRED_PROBES",
                           "-DBGK_THRESHOLD_WITNESS"]
            build(f"bgk{K}", [full + ["-I", inc, "-o", out, bg[0]],
                              base + ["-I", inc, "-o", out, bg[0]]])
    else:
        rec["bgk_missing"] = True
    for src, tag in (("cascade_filter_k.cpp", "cascade"), ("tight_lift_L.cpp", "tight_lift")):
        hits = find(code, src)
        if not hits:
            rec[f"{tag}_missing"] = True
            continue
        for K in (14, 15):
            out = os.path.join(b, f"{tag}_k{K}")
            build(f"{tag}_k{K}", [["g++", "-O3", "-march=native", "-std=c++17", f"-DK={K}",
                                   "-I", os.path.dirname(hits[0]), "-o", out, hits[0]]])
    lrc = os.path.join(WORK, "lrc.c")
    if os.path.exists(lrc):
        build("lrc", [["cc", "-O3", "-march=native", "-o", os.path.join(b, "lrc"), lrc]])
    # usage, help, self-tests
    usage = {}
    for name, path in bins.items():
        usage[name] = {"noargs": run([path], 120), "help": run([path, "--help"], 120)}
        if name.startswith("cascade"):
            usage[name]["selftest"] = run([path, "--selftest"], 1200)
    rec["usage"] = usage
    step("build", rec)
    return bins


def usage_text(rec):
    return " ".join((rec.get(x, {}).get(y) or "") for x in ("noargs", "help")
                    for y in ("stdout", "stderr"))


def stage_regression(bins):
    rec = {}
    if "v66n" in bins:
        r = run([bins["v66n"], 43, "both"], 1800)
        kv = parse_kv(r.get("stdout", ""))
        r["parsed"] = kv
        r["published_expectation"] = "direct=163507 decomp=163507 missing=0 extra=0"
        r["matches_published"] = (kv.get("direct") == "163507" and kv.get("decomp") == "163507"
                                  and kv.get("missing") == "0" and kv.get("extra") == "0")
        rec["v66_p43_both"] = r
    step("regression", rec)


def ladder(name, cmd_of, stop_after_timeout=True, per_call=600, share=0.3):
    """Run cmd_of(p) for each ladder prime until a call times out or the share of
    the remaining budget is used."""
    t_end = time.time() + share * left()
    rows = []
    streak = 0
    for p in LADDER:
        if time.time() > t_end or left() < 300:
            rows.append({"p": p, "skipped": "budget"})
            break
        cmd, outfile = cmd_of(p)
        if cmd is None:
            continue
        r = run(cmd, min(per_call, max(60, t_end - time.time())), stdout_path=outfile)
        r["p"] = p
        if outfile and os.path.exists(outfile):
            r.update(scan_output(outfile))
            os.remove(outfile)
        rows.append(r)
        with LOCK:
            SUMMARY["steps"].setdefault("ladders", {})[name] = rows
        save()
        streak = streak + 1 if r.get("timed_out") else 0
        if streak >= 2 and stop_after_timeout:
            break
    return rows


def scan_output(path):
    """Count lines by first token and keep key=value lines (S, T, counters)."""
    counts = {}
    keep = []
    with open(path, errors="replace") as f:
        for line in f:
            tok = line.split(" ", 1)[0].strip()[:20]
            counts[tok] = counts.get(tok, 0) + 1
            if "=" in line and len(keep) < 40:
                keep.append(line.rstrip()[:400])
    top = dict(sorted(counts.items(), key=lambda kv: -kv[1])[:12])
    return {"line_counts": top, "kv_lines": keep}


def stage_ladders(bins, usage):
    threads = []
    for K in (14, 15):
        name = f"bgk{K}"
        if name not in bins:
            continue
        modes = parse_modes(usage_text(usage.get(name, {})))
        with LOCK:
            SUMMARY["steps"].setdefault("modes", {})[name] = modes
        mode = next((m for m in ("decomp", "direct") if m in modes), None)
        if mode is None:
            continue

        def cmd_of(p, path=bins[name], mode=mode, modes=modes, K=K):
            m = "both" if (p <= 113 and "both" in modes) else mode
            return [path, p, m], os.path.join(WORK, f"lad_{K}_{p}.txt")
        threads.append(threading.Thread(target=ladder, args=(f"{name}_{mode}", cmd_of)))
    if "lrc" in bins:
        for K in (14, 15):
            # canonical irredundant covers of size <= K (lrc's own time cap 570 s)
            def cmd_of(p, K=K):
                return ([bins["lrc"], "covers", K, p, K, 570, 1],
                        os.path.join(WORK, f"lrc_{K}_{p}.txt"))
            threads.append(threading.Thread(target=ladder, args=(f"lrc_covers_k{K}", cmd_of)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def stage_sample(bins, usage):
    rec = {}
    for K, p in SAMPLE_TARGETS:
        name = f"bgk{K}"
        if name not in bins or left() < 900:
            continue
        modes = parse_modes(usage_text(usage.get(name, {})))
        sub_mode = next((m for m in ("irsubrootrawc", "irsubroot") if m in modes), None)
        if not ("irroots" in modes and "irsubroots" in modes and sub_mode):
            rec["skipped"] = f"modes {modes} lack irroots/irsubroots/irsubroot"
            break
        key = f"k{K}_p{p}"
        r0 = run([bins[name], p, "irroots"], 600)
        roots = parse_index_lines(r0.get("stdout", ""))
        info = {"irroots": {x: r0.get(x) for x in ("rc", "seconds", "timed_out")},
                "roots": len(roots), "subroots_per_root": {}}
        pairs = []
        t_list = time.time()
        for r in roots[:600]:
            if time.time() - t_list > 1200 or left() < 600:
                info["root_listing_cut"] = True
                break
            rr = run([bins[name], p, "irsubroots", r], 120)
            subs = parse_index_lines(rr.get("stdout", ""))
            info["subroots_per_root"][r] = len(subs)
            pairs += [(r, s) for s in subs]
        listed = len(info["subroots_per_root"])
        info["roots_listed"] = listed
        info["pairs_listed"] = len(pairs)
        rng = random.Random(SEED + 1000 * K + p)
        sample = rng.sample(pairs, min(24, len(pairs)))
        runs = []
        for r, s in sample:
            if left() < 400:
                break
            tmp = os.path.join(WORK, f"sub_{K}_{p}_{r}_{s}.txt")
            x = run([bins[name], p, sub_mode, r, s, tmp], min(900, left() - 300))
            x.update({"root": r, "sub": s, "parsed": parse_kv(x.get("stdout", ""))})
            if os.path.exists(tmp):
                x["out_lines"] = sum(1 for _ in open(tmp, errors="replace"))
                os.remove(tmp)
            runs.append(x)
            info["runs"] = runs
            rec[key] = info
            step("sample", rec)
        done = [x["seconds"] for x in runs if not x.get("timed_out") and x.get("rc") == 0]
        tout = [x["seconds"] for x in runs if x.get("timed_out")]
        if runs:
            mean = sum(done + tout) / len(runs)
            frac = listed / max(1, len(roots))
            info["estimate"] = {
                "mean_seconds_per_subroot": round(mean, 3),
                "sampled": len(runs), "timed_out": len(tout),
                "est_cpu_hours_listed_roots": round(mean * len(pairs) / 3600, 2),
                "fraction_of_roots_listed": round(frac, 4),
                "est_cpu_hours_all_roots": round(mean * len(pairs) / max(frac, 1e-9) / 3600, 2),
                "is_lower_bound": bool(tout),
                "note": "irredundant branch only; the reducible (fewer-classes) branch, "
                        "cascade and final kill are extra",
            }
        rec[key] = info
        step("sample", rec)


def main():
    global OUT, DATA, WORK, DEADLINE
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--work-dir", default="/tmp/allik")
    ap.add_argument("--budget-min", type=float, default=200)
    a = ap.parse_args()
    OUT, DATA, WORK = a.out_dir, a.data_dir, a.work_dir
    DEADLINE = time.time() + 60 * a.budget_min
    for d in (OUT, WORK):
        os.makedirs(d, exist_ok=True)
    try:  # /data may be read-only; then download into the work dir
        os.makedirs(DATA, exist_ok=True)
        with open(os.path.join(DATA, ".probe_write_test"), "w") as f:
            f.write("ok")
    except Exception:
        DATA = os.path.join(WORK, "data")
        os.makedirs(DATA, exist_ok=True)
    SUMMARY["data_dir"] = DATA
    SUMMARY["started"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save()
    stages = []
    try:
        d15, d14 = stage_download()
        code, ev = stage_extract(d15, d14)
        stage_harvest(code, ev)
        bins = stage_build(code)
        usage = SUMMARY["steps"]["build"].get("usage", {})
        stage_regression(bins)
        stage_ladders(bins, usage)
        stage_sample(bins, usage)
        stages.append("all")
    except Exception as e:
        import traceback
        SUMMARY["fatal"] = traceback.format_exc()[-4000:]
    SUMMARY["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save()
    print(json.dumps({"finished": SUMMARY["finished"], "fatal": "fatal" in SUMMARY}), flush=True)


OUT = DATA = WORK = None
DEADLINE = 0.0

if __name__ == "__main__":
    main()
