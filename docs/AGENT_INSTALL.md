# Shared Codex and Claude installation

Install the complete OpenTikZ repository; the nested skill alone lacks its
resources. Root `SKILL.md` is a relative link to the canonical
`skills/using-opentikz/SKILL.md`. Claude plugin discovery keeps that nested
entrypoint. Both clients follow the same instructions. `AGENTS.md` owns library
contribution requirements; `CLAUDE.md` imports it. Optional client metadata is
not a scientific contract.

In the mkarikom workspace, the fork is a registered submodule at
`code/.agents/skills/using-opentikz`. Generated Codex and Claude skill links point
to this directory. Startup adds missing links on each selected host. Existing
conflicting entries and retired links require explicit reconciliation; adding
a skill does not authorize repairing product system-skill state.

Outside this workspace, clone `https://github.com/mkarikom/opentikz.git` and
expose the complete root directory as `using-opentikz` in the client's skill
surface. Alternatively install the fork as a Claude plugin using its existing
marketplace metadata. Avoid installing both personal and plugin copies in the
same client. Resolve discovery links before finding the resource root. An
explicit `OPENTIKZ_ROOT` overrides `CLAUDE_PLUGIN_ROOT`.

## Dedicated LaTeX environment

The shared Linux environment is
`/nfs/turbo/umms-welchjd-code/code/mkarikom/latex_workflows_311`, beside
`GL_zarr3_311`. Follow the strict activation block in `SKILL.md` and run
`tools/render_figure.py --preflight` before using it.

`environment.yml` is a readable recipe; `environment-linux-64.lock.txt` records
the exact installed Conda builds. Recreate with `conda create -p NEW_PREFIX
--file environment-linux-64.lock.txt`, or create from the YAML to solve fresh
builds. Conda-pack supports relocation of an installed environment on compatible
Linux x86_64 hosts. Do not infer compatibility with other operating systems,
architectures, or older glibc versions.

Tectonic's TeX support-file cache is separate from Conda package resolution.
The helper sets `XDG_CACHE_HOME` to `OPENTIKZ_CACHE_DIR`, or defaults to
`$CONDA_PREFIX/share/opentikz/cache`. Thus HPC compilation does not populate
HOME with large caches. A first build needs network access. Prewarm required
packages and carry this cache with a relocated environment. `--offline` uses
`--only-cached`; missing support files fail explicitly. Pinning compiler packages
alone does not establish a complete hermetic TeX input manifest.

The renderer supports standalone one-page figures and leaves editable `.tex`
in the project. It exports PDF, outlined SVG, PNG, logs, and hash receipts.
It preserves relative project includes through the source working directory.
Receipts describe rendering, not scientific validity or RDF admission.
Visually inspect all figures before delivering them.

Contributor tooling also accepts `render_preview.py --backend tectonic` and
`validate.py --strict --engine tectonic`. Existing latexmk/dvisvgm/pdf2svg
backends remain available for projects that deliberately use those toolchains.
