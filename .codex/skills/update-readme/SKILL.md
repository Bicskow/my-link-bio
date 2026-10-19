---
name: update-readme
description: Use this skill when a new feature, route, or dependency is added to the project.
---

# Update README

Keep the project README.md current whenever a new feature, route, or dependency is added.

1. Read the project's applicable AGENTS.md instructions and existing README.md. Review the relevant code changes, routes, dependency manifests, and configuration to establish what changed.
2. Update README.md at the project root. If it does not exist, create it. Follow the existing README format, heading style, and tone when one exists. Preserve accurate existing content.
3. Keep the README organized with sections for **Project Overview**, **Features**, **Setup**, and **Dependencies**. Reuse existing equivalent sections, renaming or adding headings where needed without duplicating content.
   - **Project Overview:** Describe the project's purpose and update the summary when the change affects it.
   - **Features:** Describe what changed and how to use the new feature. For new routes, include the path, supported HTTP method, inputs, and an example when relevant, based on the implementation.
   - **Setup:** Document any new installation, configuration, environment variables, or run steps needed to use the feature. Use placeholders for secrets.
   - **Dependencies:** List new dependencies and their purpose. Include versions or constraints only when specified in the project's dependency files, and keep installation guidance consistent with those files.
4. Verify documented commands, paths, route names, and dependencies against the project. Do not invent behavior or claim to have run checks that were not performed. Avoid unrelated README changes.
5. Summarize the README updates and any validation performed, noting any unresolved information.

This is an instruction-based skill: execute it by following the steps above when invoked as `$update-readme` or when its trigger applies. No executable script or additional dependency is required.
