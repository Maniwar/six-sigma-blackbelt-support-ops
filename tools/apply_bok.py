#!/usr/bin/env python3
"""Write every module's BOK mapping line from tools/bok.py.

The mapping used to be prose typed by hand next to a code typed by hand, which
is how the page came to cite six sections that do not exist and three that mean
something other than the label beside them. Now the code is the only thing
anyone edits, in MODULE_MAP, and the line on the page is rendered from it.

    python3 tools/apply_bok.py
    python3 tools/sync_html.py

Idempotent. verify.py fails if the page and MODULE_MAP ever disagree.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from bok import ASQ, IASSC, MODULE_MAP, coverage, render          # noqa: E402

HTML = ROOT / "six-sigma-blackbelt-support-ops.html"
RE_MOD = re.compile(r'<span class="mid">(M\d+)</span>')
RE_SECTION = re.compile(r'<section id="bokmap">.*?</section>\n', re.S)


def _rows(cov: dict, titles: dict) -> str:
    out = []
    for code, mids in cov.items():
        if mids:
            # Links, not labels. A traceability matrix whose cells you cannot
            # follow is a picture of the mapping rather than a way through it.
            # No separator: the chips carry their own margin, and a comma between
            # two inline-block pills renders with a space in front of it.
            where = "".join(f'<a class="pill" href="#{m}">{m}</a>' for m in sorted(mids))
        else:
            where = '<em>not taught in this programme</em>'
        cls = "" if mids else ' class="gap"'
        out.append(f'      <tr{cls}><td><code>{code}</code></td>'
                   f'<td>{titles[code]}</td><td>{where}</td></tr>')
    return "\n".join(out)


def coverage_section() -> str:
    """The whole map on one page, gaps included.

    Every module states its own mapping, but a reader could only ever see them
    one expanded module at a time — so "full ASQ/IASSC body of knowledge" was a
    claim with no way to audit it. Rendered from MODULE_MAP, so the gaps cannot
    be quietly dropped: a section nothing covers appears here saying so.
    """
    asq_cov, iassc_cov = coverage()
    a_gaps = [k for k, v in asq_cov.items() if not v]
    i_gaps = [k for k, v in iassc_cov.items() if not v]
    note = (f"{len(asq_cov) - len(a_gaps)} of {len(asq_cov)} ASQ sections and "
            f"{len(iassc_cov) - len(i_gaps)} of {len(iassc_cov)} IASSC sections "
            "are taught here.")
    if a_gaps:
        note += (" The " + ("section" if len(a_gaps) == 1 else "sections") + " below marked "
                 "&ldquo;not taught&rdquo; " + ("is" if len(a_gaps) == 1 else "are") +
                 " outside the scope of this programme &mdash; it is built for support "
                 "operations, and these have no worked support application. If you are "
                 "sitting the ASQ exam, study them elsewhere.")
    return (
        '<section id="bokmap">\n'
        '  <h2 class="big">Body of knowledge coverage</h2>\n'
        f'  <p class="lede">Every section of both bodies of knowledge, against the module '
        f'that teaches it. {note}</p>\n'
        '  <h3>ASQ Certified Six Sigma Black Belt (2022)</h3>\n'
        '  <div class="tw"><table>\n'
        '    <thead><tr><th>Section</th><th>Title</th><th>Taught in</th></tr></thead>\n'
        '    <tbody>\n' + _rows(asq_cov, ASQ) + '\n    </tbody>\n  </table></div>\n'
        '  <h3>IASSC Lean Six Sigma Black Belt</h3>\n'
        '  <div class="tw"><table>\n'
        '    <thead><tr><th>Section</th><th>Title</th><th>Taught in</th></tr></thead>\n'
        '    <tbody>\n' + _rows(iassc_cov, IASSC) + '\n    </tbody>\n  </table></div>\n'
        '</section>\n')


def main() -> int:
    src = HTML.read_text(encoding="utf-8")
    blocks = re.split(r'(?=<details class="mod">)', src)
    out, written, added = [], 0, 0
    for b in blocks:
        m = RE_MOD.search(b)
        if m:
            # An anchor to link at. The modules had none, so the coverage table
            # could only name them; the page's own deep-link handler already
            # opens a collapsed <details> once it can find one by id.
            #
            # Matched as a tag rather than a literal string because one module
            # ships expanded, as <details class="mod" open> — a literal replace
            # silently skipped exactly that one and left a dead link behind it.
            b = re.sub(r'<details class="mod"((?: (?!id=)[^>]*)?)>',
                       lambda mm: f'<details class="mod" id="{m.group(1)}"{mm.group(1)}>',
                       b, count=1)
        line = render(m.group(1)) if m else None
        if line is None:
            out.append(b)
            continue
        want = f"<h5>BOK mapping</h5><p>{line}</p>"
        if re.search(r"<h5>BOK mapping</h5>\s*<p>.*?</p>", b, re.S):
            new = re.sub(r"<h5>BOK mapping</h5>\s*<p>.*?</p>", lambda _: want, b,
                         count=1, flags=re.S)
            written += new != b
        else:
            # A module that never had one — the three tollgate clinics. It goes
            # where every other module carries it, immediately inside the body.
            new = b.replace('<div class="body">',
                            f'<div class="body">\n    {want}', 1)
            added += new != b
        out.append(new)
    text = "".join(out)

    section = coverage_section()
    if RE_SECTION.search(text):
        text = RE_SECTION.sub(lambda _: section, text, count=1)
    else:
        text = text.replace('<section id="sources">', section + '\n<section id="sources">', 1)
    link = '<a href="#bokmap">Body of knowledge coverage</a>\n'
    if 'href="#bokmap"' not in text:
        text = text.replace('  <a href="#sources">Sources</a>',
                            '  ' + link + '  <a href="#sources">Sources</a>', 1)

    if text != src:
        HTML.write_text(text, encoding="utf-8")
    print(f"  {written} mapping(s) rewritten, {added} added, "
          f"{len(MODULE_MAP)} module(s) declared")
    missing = [k for k in MODULE_MAP if f'<span class="mid">{k}</span>' not in text]
    if missing:
        print(f"  ! MODULE_MAP names modules that are not on the page: {missing}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
