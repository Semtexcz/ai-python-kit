## AI Python Kit routing

Append this block to the existing project instructions after reviewing it. Keep the existing text.

## Python engineering workflow

Project policy is `.ai-python/policy.toml`; native configuration is under `.ai-python/config/`. Run the unified check before reporting completion:

    just --justfile .ai-python/kit/justfile --working-directory . check

Read the matching workflow skill under `.ai-python/kit/skills/` and the shared references under `.ai-python/kit/references/`. Do not weaken tests or gates, add broad suppressions, bypass typing, hide exceptions, add unauthorized dependencies, or expand scope. Policy exceptions require recorded human approval.
