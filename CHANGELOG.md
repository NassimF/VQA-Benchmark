# Changelog

## 2026-06-08

- feat: add LVLM comparison tables to results.tex (ffe68aa)

## 2026-06-08

- feat: add reproduce_table_lvlm and fix C1/C2 n-gram scores (7e376f2)

## 2026-06-08

- docs: update results.md with full LVLM comparison table (79c4aa7)

## 2026-06-08

- fix: paper consistency pass — correct benchmark counts after quality fix (5f30c23)

## 2026-05-29

- docs: add entailment scores and key findings to plan (18d93f7)

## 2026-05-29

- feat: complete LVLM inference for all 4 models with fixes (9bdfbee)

## 2026-05-28

- docs: update plan.md and changelog for phase 11 (50409fc)

## 2026-05-28

- fix: recover Video-LLaVA empty answers via max_frames_total (7c1a5b1)

## 2026-05-28

- fix: correct 10 invalid GT timestamps, remove 2 broken QA pairs (557553f)

## 2026-05-26

- feat: add LVLM inference script and config (Phase 11) (c960a89)
- docs: exclude LLM-judge from LVLM comparison, note cost rationale (bb00755)
- docs: update Phase 11 spec with EduVidQA prompts and tIoU exclusion (e9d5696)
- docs: resolve all open questions in Phase 11 spec (f66b16b)
- docs: lock FactQA model to GPT-4o-mini with rationale in Phase 11 spec (970b0db)
- feat: add standalone FactQA scorer (FQA-P, FQA-R, FQA-F1) (450c4b9)
- docs: lock transcript+frames input setup, exclude frame captions for LVLMs (dd8f442)
- docs: document decision to skip fine-tuning in Phase 11 spec (bb71d94)
- docs: lock windowing strategy and per-model frame counts in Phase 11 spec (cc7bb92)
- docs: add hop count distribution table to README and benchmark section (c97efd5)
- docs: document Entailment-P exclusion decision in Phase 11 spec (0f88794)
- feat: add Phase 11 spec for LVLM/Video LLM baseline experiments (3d812f0)
- chore: add CHANGELOG.md (171 commits across 18 dates) (35c1690)

## 2026-05-26

- feat: add standalone text metrics script (BLEU, ROUGE-L, METEOR, Entailment) (e98d7b5)

## 2026-05-19

- docs: add PowerPoint advisor presentation (21 slides) (4b207cb)
- docs: add advisor presentation slide deck (Beamer, 20 slides) (8c27f32)
- docs: add QA generation steps and citation accuracy to README (9eb5f7d)

## 2026-05-18

- expand: §4.2 cite Min et al. 2019 to justify quality over quantity (7503bc1)
- sync: Overleaf submodule — caption positions, review copy number (d61e737)
- revert: undo table caption moves in §5 (881f705)
- Revert "style: move table captions above tabular in §5 (BMVC convention)" (774359a)
- style: move table captions above tabular in §5 (BMVC convention) (7aa4e75)
- review: complete paper review pass — §1–§6, abstract, references (59493b8)
- review: §5 results — tables, layout, failure case (026b418)
- docs: remove assignment header and affiliation from README (2b7946b)
- chore: remove assignment and planning artefacts (1cb8865)
- review: §4 polish — figures, spacing, LaTeX warnings (0e2a272)
- review: complete §4 benchmark construction pass (3dd0879)
- style: Figure 1 aesthetic polish for BMVC (0ac1847)
- fix: add citation accuracy to Figure 1 metrics box (c8c2629)
- review: trim §3 impl details; fix §3.5 cost argument (e4d795b)
- review: strengthen §3 design-choice justifications (6b489e1)
- review: fix §3 frame count (15020→17180) (e0da67d)
- chore: sync §2 related work fixes to Overleaf (8baeb9b)
- review: add 4 new §2 citations (LLM-judge, video RAG, aligned captions, negative queries) (769a73a)
- review: fix §2 related work factual errors (610b2f9)
- chore: ignore REVIEW_CHECKLIST.md (30b59c2)
- checkpoint: BMVC compliance + figure layout polish complete (86e6943)

## 2026-05-17

- fix: fig1 arrow video→caps, neutral phase label colors (bd7af82)
- fix: move fig4 back to top of §5 with [t] and intro sentence (35ee05e)
- fix: remove line numbers, restore URL, fix float spacing (d3a0d20)
- fix: BMVC compliance — blind review, URL, hatch, intextsep (bfda9af)
- fix: add enumitem, replace unicode geq with \$\geq\$ (1b0e501)
- fix: add amssymb for checkmark, replace invalid texttimes (2e549f5)
- fix: update fig3 caption to reflect visual-dependent/control grouping (f422c50)
- fix: move fig4 legend to upper left to clear bars (64d2c1a)
- fix: update fig4 caption to new question type names (5f60a3a)
- fix: rename question types in benchmark.tex to match new taxonomy (7e237ee)
- fix: restore y-axis, add group spacer in fig_qa_dist (323686f)
- feat: two-level grouped QA dist chart, rename question types (48ea11d)
- feat: TikZ pipeline fig, author name/email fix (e6ce319)
- feat: replace fig1 PNG with TikZ pipeline diagram (7542b9a)
- fix: correct +183% -> +283% in fig4, add multi-hop regression note (2ee98b8)

## 2026-05-15

- fix: §4.5 Schema overflow — split long texttt, footnotesize+sloppy (535eb8f)
- fix: reduce intextsep to close gap above [H] tables (791fedd)
- fix: shrink fig4, raggedbottom to remove stretched whitespace (0e87042)
- fix: fig3 smaller+pinned, §4.5 gap removed, Schema overflow fixed (6abcb4b)
- fix: table overflow, §2 overflow, tab:qa_dist position, §4.5 gap (bc57a53)
- fix: pin fig_qa_dist and fig_iou_by_type with [H] to correct sections (a9928b9)
- fix: pin figures 4 and 5 with [H] to correct sections (40330ce)
- fix: force tables 4+5 to exact position with [H] and float package (db094f7)
- chore: sync Overleaf submodule after results table fix (1c0b6f6)
- fix: results tables [t] -> [ht] to keep them in their subsections (c91d3bd)
- fix: reposition all figures and tables to correct paper locations (ed00aba)
- fix: change all tables [h] -> [t] for correct column placement (1a95703)
- fix: scale figures to 0.82col, use [t] placement to fix refs bleed (aca2d76)
- docs: Phase 10 complete — paper polish, figures, README (048867f)
- docs: update Phase 10 spec — add TG5-8 (line numbers, overflow, BMVC format, style audit) (c674a0b)
- docs: Phase 10 spec — paper figures, factual fixes, README (f6c97c8)
- docs: Phase 9 complete — roadmap ✅, changelog updated (1fc68ad)
- feat: add --output flag to run_part1 and reproduce_tables (8308032)
- feat: Phase 9 complete — run_part1, reproduce_tables, results.md (36694d1)
- docs: revise Phase 9 spec — reflect existing files and stale API (78fa01a)
- docs: Phase 9 spec — deliverables plan, requirements, validation (79430dd)
- docs: update roadmap Phase 9.2 complete, add Phase 8 changelog (3d786fe)
- feat: Phase 8.2 complete — full eval results + paper updates (883de61)
- feat: rewrite run_part2.py to use evaluate_all API (d8a3bad)
- feat: Phase 8.1 complete — evaluator, tests, specs (fa222ec)

## 2026-05-14

- chore: ignore literature-review/, untrack Excel and MD files (da7777c)
- docs: update roadmap Phase 7.4/7.5 complete, add regen raw + review logs (0350d12)
- feat: Phase 7.5 span precision audit, update paper limitation (fcd93d5)
- feat: Phase 7.4 build/validate benchmark, 810 final QA pairs (41e9c7a)
- docs: update visual QA percentage from 60% target to 55.6% actual (9da02c4)
- docs: add post-evaluation reminder notes to Phase 9 and 10 (4083589)
- docs: mark Phase 7.3 complete, update roadmap with final QA counts (2f06abe)
- docs: add paper figures/tables and failure case example (451708d)
- docs: update roadmap for no-discard policy and check_coverage step (2d5cde8)
- feat: add coverage check script, remove lecture discard threshold (1c7c8ae)
- docs: add paper reminder for low QA count fallback defense (a9a2b35)
- docs: add cross-benchmark density defense to benchmark section (f954e10)
- docs: add end-to-end reproduction steps to README (034db40)
- docs: rewrite README for LectureBench submission (2f5e959)
- feat: Phase 10 paper sections complete with placeholders (a63d353)
- feat: Phase 9 placeholder scripts and results tracker (11c157b)
- docs: update changelog through Phase 7.3 pre-regen fixes (097babb)
- fix: pre-regeneration fixes for Phase 7.3 QA review (20ff7b3)
- docs: add question descriptions to all Q sections in phase 7.3 lit review (7b52d68)
- docs: downgrade D8b human spot-check to optional note in all specs (6e62c34)
- docs: sync specs with Phase 7.3 run results and lit review updates (91537dd)
- docs: remove duplicate CALCE entry from main Paper Dictionary (896d25c)
- docs: add missing URLs and fix venues in main Paper Dictionary (ee6b9ff)
- docs: add Venue/Peer-Reviewed column to main Paper Dictionary (f7bc72f)
- docs: correct RAGAS venue to EACL 2024 System Demonstrations track (318e1a3)
- docs: add Venue/Peer-Reviewed column to phase 7.3 Paper Dictionary (e9b1589)
- docs: fix 8 discrepancies in phase 7.3 lit review report (8e1ebce)
- docs: rewrite abstract following top-venue benchmark paper conventions (03a2893)
- docs: update benchmark.tex LLM Review section for Phase 7.3 (da18882)
- docs: merge chunk-as-ground-truth argument into curation support section (60ab5d7)
- docs: add 'What Supports LLM-Only Curation' subsection (aaa4829)
- docs: clarify RAGAS and Ho et al. as partial support in curation table (09ff92a)
- docs: add LLM-only curation gap section to lit review (f5f00b6)
- docs: update lit review Q1-Q6 with peer-reviewed citations (c257293)

## 2026-05-13

- feat: add Phase 7.3 reviewer tests, 8/8 passing (Group 4) (f19f047)
- feat: implement Phase 7.3 core reviewer and review script (Group 3) (838e7d5)
- feat: add reviewer prompt templates for Phase 7.3 (Group 2) (b24d775)
- docs: sync all specs with D1 two-call reviewer design (830329e)
- docs: adopt simplified Option C (cross-family C1 check) for Phase 7.3 (67e055d)
- fix: convert Figure 1 PNG to RGB, set 300 DPI (3720b7d)
- feat: add Figure 1 pipeline diagram to paper (31dcd04)
- docs: clarify tIoU@0.3 source in Q6 answer (04c4406)

## 2026-05-12

- docs: add Option C criterion-targeted reliability to lit review (c561800)
- docs: add Lee et al. 2026 to multi-judge lit review (145773a)
- docs: add multi-judge lit review to Phase 7.3 report (331177e)
- feat: add Phase 7.3 LLM review spec (fcbcd2b)

## 2026-05-11

- docs: define Phase 8 LLM judge criteria, add lit review TODO (0524d15)
- docs: add Phase 7.5 span precision audit to roadmap (0cfbaf3)
- docs: Phase 7.3 lit review, paper formatting rules, sync fixes (08edc0d)
- docs: add Phase 7.3 context for post-context-clear pickup (46fb5c4)
- docs: strengthen EduVidQA contrast in related work (79b15f1)

## 2026-05-10

- docs: fix frame interval and fill corpus duration in paper (4bc3877)
- docs: update changelog through Phase 7.2 (fa4c9d3)
- chore: sync specs to current project state (b7b22ef)
- feat: complete QA generation for all 60 lectures (c915f7f)
- feat: QA generation pipeline (Phase 7.1-7.2) (b5f8fd4)
- chore: commit config.py qa model field and overleaf submodule pointer (4bb9b64)
- docs: update qa_generation model to claude-sonnet-4-6 (a362de8)
- Update Overleaf submodule - 2026-05-10 02:53 (ccd1c2e)
- docs: mark Phase 6 validation complete, update changelog (eabf86a)
- Update Overleaf submodule - 2026-05-10 02:33 (78c3d97)
- docs: update changelog and roadmap for Phase 6 and benchmark note (58b86ec)

## 2026-05-08

- feat: generator module (Phase 6) (d92ccef)
- docs: sync tech-stack versions and frame interval (c14814f)
- feat: RAG ingestion, both configs (Phase 5) (635af03)
- docs: update CHANGELOG.md (22d6993)
- docs: record open decision on Phase 7.3 QA review method (255a97d)
- docs: update CHANGELOG.md — fix (latest) tag, add phase 4.2 notes (4ff36dd)
- docs: mark pipeline run spec complete (phases 2.2–4.2) (8df7e4c)
- feat: run full data pipeline (phases 2.2–4.2) (8a811bb)

## 2026-04-26

- docs: add Overleaf sync rule to CLAUDE.md and roadmap (453903b)
- docs: reframe as conference paper; remove Phase 8 cross-validation (06fe49a)
- docs: add per-phase paper writing reminders to roadmap (c567527)
- docs: sync Overleaf fixes, update roadmap and changelog (206ce17)
- docs: sync Overleaf submodule — paper skeleton (83f724c)
- docs: add Specs & Roadmap section to CLAUDE.md (7b6d14c)
- docs: update CHANGELOG.md for Overleaf submodule (a770067)
- docs: reflect Overleaf submodule in specs (e469714)
- docs: update CHANGELOG.md (2b08e1a)
- Add Overleaf submodule under overleaf/ (e12f6e8)

## 2026-04-23

- docs: fix roadmap discrepancies in phases 1-4 (75ef8f4)
- docs: add frame interval and overlap rationale to Phase 4.2 (a2faf93)

## 2026-04-22

- docs: update CHANGELOG.md for Phase 1 completion (3f7ae76)
- docs: mark Phase 1 complete in roadmap (e0e3213)
- data: all 60 VTTs + metadata downloaded (Phase 1.2 ✅) (6e7492b)
- fix: add webm support and initialize downloaded field for all entries (f021580)
- docs: mark Phase 1.1 complete in roadmap (d4fd51a)
- feat: download_videos.py + Phase 1.1 feature spec (Phase 1.1) (969d75d)
- docs: remove log.md (migrated to CHANGELOG.md), fix tech-stack header (aa1825c)

## 2026-04-21

- docs: add CHANGELOG.md with git history, decisions, and observations (8d2fdba)
- docs: add deliverables, lit review, decisions log, and observations (cad5a5c)
- docs: add config.yaml reference and directory structure to tech-stack (979887c)
- docs: add multihop metric formulas and report tables to roadmap (571c065)
- docs: add specs/corpus.md with 60-video library and licensing (dc2a000)
- docs: add specs constitution (mission, tech-stack, roadmap) (3227be4)
- feat: expand to 60 lectures, replace BLIP with Qwen2-VL (52b1a4c)

## 2026-04-20

- docs: update plan for Phase 4 completion and NYU lectures (de77578)
- feat: frame caption pipeline complete (Phase 4) (1703106)
- feat: add NYU lectures + frame caption pipeline (Phase 4) (695e069)
- docs: add scale context note to PROJECT_PLAN.md (776d637)
- docs: sync PROJECT_PLAN.md with phases 2 and 3 (26806f4)
- feat: chunking pipeline (Phase 3) (6185799)
- feat: transcription pipeline (Phase 2) (7d805a2)
- docs: update literature review and project plan (9af7363)

## 2026-04-19

- feat: Phase 0+1 complete — literature review and video collection (eacb15d)

## 2026-04-18

- feat: project skeleton and documentation (31571fc)
