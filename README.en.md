# iPhone Duo Adaptation Skill

[简体中文](README.md) | [English](README.en.md)

A reusable skill for Codex and other coding assistants that support `SKILL.md`. Improve adaptive layouts, navigation, toolbars, fold avoidance, and task continuity across iPhone Duo configurations.

The research baseline is **November 2, 2026**. The skill draws on Apple's Human Interface Guidelines, six Tech Talks, SDK declarations, and original release materials from seven apps. It distinguishes official platform guidance, vendor descriptions, project-specific design recommendations, and observed test results.

## What it helps you do

- Adapt to the outer display, unfolded inner display in both orientations, book and tabletop configurations, tent use, and opening and closing transitions.
- Handle left and right Split View placement, reduced height from pinned picture-in-picture, keyboards, and active camera regions.
- Choose meaningful layouts: list and detail, content and supporting information, overlays, optional sidebars, and comfortable reading widths.
- Preserve drafts, selection, navigation paths, semantic reading positions, playback sessions, and other ongoing work as layouts change.
- Review SwiftUI and UIKit implementations, with adaptation considerations for Flutter, React Native, and Web content.
- Validate accessibility and continuity while reporting static review, builds, simulator behavior, device installation, and physical-device acceptance separately.

The skill instructions and detailed references are currently written in Chinese. This English introduction explains installation, usage, scope, and verification limits; it is not a complete translation of the skill.

## Install in Codex

Clone the repository into your skills directory. If the destination already exists, inspect it before making changes; do not overwrite an existing installation blindly.

```bash
git clone https://github.com/vanohezy/iphone-duo-adaptation.git ~/.codex/skills/iphone-duo-adaptation
```

If you have set `CODEX_HOME`, use its `skills/iphone-duo-adaptation` directory instead. Start a new chat and invoke the skill:

```text
Use $iphone-duo-adaptation to review and improve this app across the outer display, unfolded and partially folded configurations, Split View, and opening/closing transitions. Validate the changes and report the evidence. Respond in English.
```

## Included resources

| Resource | Contents |
| --- | --- |
| [Skill entry point](SKILL.md) | Workflow, scope, constraints, and evidence boundaries |
| [Official guidance](references/official-guidance.md) | SDK behavior tiers, six Apple talks, API names, and original sources |
| [States and layouts](references/states-and-layout.md) | Configuration matrix, layout choices, and continuity contracts |
| [App patterns](references/app-patterns.md) | Things, Fantastical, Cardhop, Bulletin, Structured, Detail, and Prime Video |
| [Implementation](references/implementation.md) | Code review and adaptation approaches across frameworks |
| [Validation](references/validation.md) | Task-based checks, accessibility, continuity, and evidence levels |

## Read-only layout audit

The helper requires only Python 3's standard library:

```bash
python3 scripts/audit_layout.py /absolute/path/to/app --format markdown
python3 scripts/audit_layout.py /absolute/path/to/app --format json --max-findings 200
```

It highlights candidates for manual review, including main-screen sizing, device-based layout branches, fixed dimensions, safe-area bypasses, media cropping, and custom bars. Findings and explanations are currently in Chinese.

The scan can produce false positives and miss issues. It does not replace compilation, runtime checks, or physical-device testing. By default, it skips hidden directories, dependencies, build outputs, symbolic links, sensitive filenames, and files larger than 2 MiB. It does not modify the inspected project.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests cover cross-platform pattern discovery, excluded paths and symbolic links, output limits, command-line exit status, read-only behavior, and unreadable inputs. The skill structure has also been validated and independently exercised against a realistic podcast-app request. These checks do not establish that any particular app has passed foldable-device acceptance testing.

## Sources and contributions

This is an independent project, unaffiliated with Apple, and is not an official Apple skill. It summarizes and links to original sources; third-party documentation and vendor materials retain their respective rights. Start with Apple's [Get ready for iPhone Duo](https://developer.apple.com/iphone-duo/) resources.

APIs and app behavior may change. Before implementing a change, check the current official documentation and the SDK selected by your project.

Issues and pull requests are welcome. Include original sources or reproducible steps with corrections, and avoid submitting credentials, personal data, or materials you are not authorized to share.

## License

Original code and documentation in this repository are available under the [MIT License](LICENSE). Referenced third-party materials remain subject to their own terms.
