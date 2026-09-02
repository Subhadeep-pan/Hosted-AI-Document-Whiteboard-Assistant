"""
Evidence fusion (the "Evidence Fusion" box in the plan's architecture
diagram). Combines document RAG context, live data, and learned/semantic
memory into one clearly-labeled block for the prompt, so Gemini can see
where each piece of evidence came from.
"""


def fuse_evidence(document_context=None, live_data_text=None, learned_context=None, email_text=None):
    sections = []

    if document_context:
        sections.append(f"[From your uploaded documents]\n{document_context}")

    if live_data_text:
        sections.append(f"[From live web/API data]\n{live_data_text}")

    if email_text:
        sections.append(f"[From your email]\n{email_text}")

    if learned_context:
        sections.append(f"[From memory - preferences & past interactions]\n{learned_context}")

    return "\n\n".join(sections)
