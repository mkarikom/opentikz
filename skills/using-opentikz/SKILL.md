---
name: using-opentikz
description: Create, revise, compile, and visually verify editable standalone TikZ conceptual figures for papers, posters, and scientific communication, using OpenTikZ icons, architecture templates, and examples. Use for neural network architectures, pipelines, system diagrams, and flowcharts; not numerical data plotting or slide-deck authoring.
---

# Using OpenTikZ

These shared instructions apply to Codex, Claude, and other coding agents.
Use this skill for standalone paper, poster, and report figures. It may supply
a figure embedded in a presentation; the selected slide-authoring skill owns
the deck and its layout/runtime. In the shared mkarikom workspace that is
`dom-aware-slide-authoring`. Numerical data plots belong to an appropriate
plotting package (e.g. pgfplots). Do not infer measured results from diagrams or
add RDF/BenchmarkTools workers or admissions merely because a figure depicts a
benchmark. Honor the user's stated scope and staged stopping points.

For model architectures, read the exact campaign configuration and the owning
model implementation. Show the instantiated model, not historical architecture
or template defaults. Distinguish forward flow, conditioning, training losses,
and iterative sampling/design. Frozen predictors can still pass gradients to
DNA. Fixed-label models do not gain continuous-state conditioning through an
evaluation mapping. Record source identities, tensor shapes, reductions, and
scientific assumptions beside the figure. Do not load large checkpoints solely
to inspect architecture. Compose a new figure with library conventions when
existing templates cannot represent the model faithfully.

On the mkarikom HPC workspace, use `env-runner` and the dedicated environment:

```bash
set -e
module unload python3.11-anaconda || true
module load python3.11-anaconda
source activate /nfs/turbo/umms-welchjd-code/code/mkarikom/latex_workflows_311
module unload python3.11-anaconda || true
which python
test "$(which python)" = /nfs/turbo/umms-welchjd-code/code/mkarikom/latex_workflows_311/bin/python
```

Outside that workspace use the user's toolchain or an isolated environment
from `environment.yml`. Do not modify a scientific training/service environment.
The bundled workflow uses Tectonic and Poppler:

```bash
python "$OTROOT/tools/render_figure.py" --preflight
python "$OTROOT/tools/render_figure.py" figures/model.tex --output-dir figures/rendered
```

It exports PDF, outlined SVG, PNG, a build log, and a render receipt. Initial
builds download TeX support files into a cache outside HOME on HPC.
`OPENTIKZ_CACHE_DIR` selects a cache. Prewarm needed packages then use `--offline`
to require cached inputs; a cache miss fails without changing compilers.
Read `docs/AGENT_INSTALL.md` for discovery and portability requirements.

OpenTikZ is a library of copyable TikZ **icons**, editable **templates** (neural
nets, encoder-decoder, training pipelines, system block diagrams, flowcharts),
and full **examples**. This skill is how you go from a user's request to a
finished, compiling `.tex` figure — reliably, and without guessing.

There is **one** skill (this file). Per-template knowledge lives in each
template's `edit_contract` (inside its `meta.json`), which you read at edit time.
Do not look for per-template `skill.md` files; they no longer exist.

## 0. First: which mode are you in, and where is the library?

**Pick the mode:**
- **Mode A — produce a figure for the user's own project** (the default). The
  OpenTikZ library is read-only and lives elsewhere; the user is working in their
  own paper/LaTeX project. You will *copy* a figure out of the library and edit the
  copy in their project. Never modify the library.
- **Mode B — contribute back to the OpenTikZ repo itself.** The user is editing the
  library: their working directory *is* the repo. Edit in place and run the repo
  tooling (see §6).

**Locate the library root (`OTROOT`) for Mode A:**
1. Use `OPENTIKZ_ROOT` when explicitly set; otherwise use `CLAUDE_PLUGIN_ROOT`
   for plugin installs. Resolve and validate the full library. An incomplete
   explicit root is an error, not grounds for silently choosing another library.
2. Otherwise resolve the actual `SKILL.md` file through all discovery symlinks
   and walk its parent directories until `catalog.json`, `icons/`, `templates/`,
   and `tools/` are found. Do not count parents of a lexical client-link path.
   Root `SKILL.md` and the nested Claude plugin entry point to the same source.
3. If you can only read the repo remotely (e.g. over GitHub, no local clone), treat
   the GitHub repo as `OTROOT` and fetch raw file contents on demand.

Confirm `OTROOT` once (e.g. list `OTROOT`/catalog.json) before relying on it. The
output target honors the user's destination; otherwise choose `figures/` in
their project, never `OTROOT`. Install the complete repository; a copy of only
the nested skill directory does not contain the library or render tooling.

## 1. Communicate precisely (do this first, throughout)

Your job is to produce the figure the user actually wants, not a plausible guess.
Classify every ambiguity before acting:

**Material ambiguity → ask, or offer two concrete alternatives.**
Trigger when the answer changes the figure's *structure or identity*, is *hard to
reverse*, or you would otherwise be guessing between genuinely different intents.
Ask one crisp question with concrete options; never a vague "what do you want?".

- "draw a transformer" → encoder-only, decoder-only, or encoder-decoder? (ask)
- "add attention" → self-attention or cross-attention, and where? (ask)
- "highlight the new part" → which part is new? (ask)
- Use **offer-two-alternatives** when seeing beats describing — an aesthetic or
  layout fork (two color schemes, two layouts). Produce both and let the user
  pick. Don't use it for continuous quantities (widths, counts).

**Safe-default ambiguity → proceed, state the assumption in one line, keep it
cheap to reverse.** When there is a sensible default and changing it is a
one-line tweak, don't interrupt — just decide and tell the user what you assumed.

- palette: default light Okabe-Ito unless "dark" is mentioned.
- width: default standalone (no `\resizebox`) unless a venue/column width is named.
- spacing / size: use the template default. Model layer counts and dimensions
  come from the actual implementation/configuration, or are explicitly marked
  as illustrative when the user requests a generic teaching diagram.

**Anti-interrogation guardrail.** Ask at most ~2–3 questions up front, batched;
resolve everything else with assume-and-state. Include concise material
assumptions and physical figure-size notes with the delivered artifacts.

## 2. Workflow

1. **Understand & classify.** Restate the goal in one sentence; classify
   ambiguity per §1; ask the (few) material questions, batched.
2. **Discover.** Read `catalog.json` at `${OTROOT}` (see §0). Match the request to
   icons / templates / examples by `name`, `tags`, `domain`. If several fit,
   choose the best supported base and proceed. Offer alternatives only when
   the difference changes scientific meaning and cannot be resolved from sources.
3. **Select.** State the chosen base and material parameters. A clear request
   authorizes reversible implementation choices; do not reconfirm it.
4. **Copy, then edit (Mode A) / edit in place (Mode B).**
   - **Mode A:** copy the chosen item's `.tex` from `OTROOT` into the user's project
     (a sensible path like `figures/<name>.tex`); tell the user where you put it.
     Edit *that copy*, never the file under `OTROOT`. If the figure is already in
     the user's project, edit it there. For a **template**, read its `edit_contract`
     from `OTROOT`'s `catalog.json` (or the item's `meta.json`) and: edit only the
     contract's `parameters`; follow its `operations` as the recipe; keep every
     `invariant`; preserve the `node_naming` scheme; colours via palette names only.
     For an **icon/example** (no contract), edit under the same hard rules.
   - **Mode B:** edit the item in place inside the repo, under the same rules.
5. **Verify by compiling — in the user's project (Mode A).** Run the user's LaTeX on
   the copied/edited file (the bundled Tectonic helper, `latexmk -pdf`, or `pdflatex`). Fix failures
   before returning — never hand back a figure you didn't compile. (Regenerating
   `.svg` previews and `catalog.json` is a *Mode B / contributor* task — skip it
   when producing a figure for a user.)
6. **Inspect and deliver.** View every rendered figure, check scientific source
   fidelity, label collisions, clipping, arrows, contrast, and final physical
   font size. Rebuild and reinspect after fixes. Return the editable `.tex`,
   vector PDF/SVG, PNG preview, and concise assumptions/venue-size notes.
   A successful compile alone does not establish visual or scientific validity.

## 3. Hard rules (never violate)

- The `.tex` must stay **standalone-compilable** (`\documentclass{standalone}`).
- **Colors only via the five palette names** (`otblue otorange otteal otpurple
  otgray`); tints/shades like `otblue!15` are fine. Never inline a hex value or a
  stock xcolor name (`blue`, `red`). See `reference/color-palettes/`.
- **Preserve node names / the `node_naming` scheme** — they are the contract that
  lets edits target the right parts. Give any new node a clear semantic name.
- **Keep figures parametric** — drive counts/spacing/labels through the `\def`
  block at the top; don't hard-code what a parameter already controls.
- **Separate icon from label — never overlay a `\pic` on a node's centred text.**
  For any box that carries *both* a glyph and a label, make the box node empty
  (`{}`), then place the icon with a standalone `\pic` in the box's **upper half**
  and the label as a *separate* text node in the **lower half** (or icon-left /
  text-right for a wide chip). Size the box tall enough for both bands. Dropping a
  `\pic` on top of a node's own `{text}`, or faking the offset with `\hspace`,
  collides every time — this is the single most common rework.
- **Budget padding — size a box to its content *plus* margin, never flush to it.**
  Set `minimum width`/`minimum height` to the widest/tallest content **plus a
  per-side padding budget of ≥0.25 cm**. For a multi-column in-box layout (e.g.
  two icon+label stacks), also give an explicit inter-column gap (≥0.3 cm) and keep
  each column's widest line clear of the frame. If any text touches the border,
  widen the box or push the columns inward — do **not** shrink the text.

## 4. Common cross-template operations

These work the same across templates; the per-template `edit_contract` lists the
specific parameter/style names to touch.

**Recolor.** Change the palette color *name* in the relevant style or node, never
a hex. "Make it teal" = `otblue` → `otteal` in that style's `fill`/`draw`.

**Switch to the dark palette.** Replace the light `\definecolor` block with the
dark block from `reference/color-palettes/color-palettes.md` — the names are
identical, so the body is unchanged. The dark palette is for **dark
backgrounds**: also set `\pagecolor{otpaper}`
(`\definecolor{otpaper}{HTML}{1E1E1E}`), or the tints render washed-out grey on a
white page.

**Adapt to a venue / column width.** Wrap the whole `tikzpicture` in `\resizebox`
(needs `\usepackage{graphicx}`):
```
\resizebox{\columnwidth}{!}{\begin{tikzpicture} ... \end{tikzpicture}}
```
In a paper use `\columnwidth` (single column) or `\textwidth` (full width); to
test a target in the standalone file give an explicit width
(`\resizebox{8.4cm}{!}{...}`). Common targets: CVPR/ICCV/ACL single column
≈ 8.4cm, full/double width ≈ 17.8cm; NeurIPS/ICML text ≈ 13.9cm. Caveat:
`\resizebox` scales text too — if the figure is far wider than the column, first
reduce content/spacing (the template's spacing parameters) and resize the rest.

## 5. Reference material

- `reference/color-palettes/` — the canonical five-color Okabe-Ito palette (light
  + dark blocks), the single source of truth for colors.
- `reference/annotations/` — how to add callouts, braces, and highlight labels.
- `reference/layout/` — positioning, alignment, and spacing patterns.
- `docs/DESIGN_GUIDE.md` — global conventions (line width, node naming, metadata).

## 6. Mode B procedure — contributing back (editing the repo itself)

If the user is adding/changing library content (not just producing a figure for
their paper), the repo tooling applies:

- regenerate the preview: `python tools/render_preview.py <file>.tex --backend tectonic -o <dir>/preview.svg`
- regenerate the catalog: `python3 tools/build_catalog.py`
- validate: `python tools/validate.py --strict --engine tectonic` (or legacy latexmk)
- a new/edited template needs an `edit_contract` in its `meta.json` (see §4 of
  `docs/DESIGN_GUIDE.md`); `validate.py` checks its parameters/styles exist in the
  `.tex`.
