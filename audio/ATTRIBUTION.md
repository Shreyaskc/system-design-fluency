# Narration provenance

Original System Design Fluency teaching content and listening adaptations. Synthetic narration is generated locally with Kokoro-82M v1.0, American English voice `af_heart`, speed 1.0, CPU inference, one thread. No paid service, voice cloning or credentials are used. The player patterns were adapted from the user-owned AI Fluency project, inspected read-only.

Primary sources checked 19 October 2026:

- Engine: https://github.com/hexgrad/kokoro (Apache-2.0 declaration).
- Model/voice: https://huggingface.co/hexgrad/Kokoro-82M (Apache-2.0 declaration and model card).
- Pinned snapshot: `f3ff3571791e39611d31c381e3a41a3af07b4987`.
- Weights SHA256: `496dba118d1a58f5f3db2efc88dbdc216e0483fc89fe6e47ee1f2c53f18ad1e4`.
- Voice SHA256: `0ab5709b8ffab19bfd849cd11d98f75b60af7733253ad0d67b12382a102cb4ff`.

The upstream Apache license is retained in `licenses/Kokoro-Apache-2.0.txt`. The model card identifies StyleTTS2/iSTFTNet architecture contributions and training-source acknowledgments, including Koniwa and SIWIS; see its primary links for details. This is attribution for the generation tools and model, not a new license grant over the original course. No Apple System Voice audio is distributed.

Each catalog record pins the original section and transcript hashes, media hash, duration and provenance path. Provenance records contain model/voice revision and hashes, per-paragraph text hashes/sample counts, non-silence statistics, and text-consumption checks. Visual code/diagram blocks have original spoken explanations in `code-narration.json`, keyed by exact source-block SHA256; changes cannot silently reuse an explanation for a different block.
