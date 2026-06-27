# Privacy Sanitization Notes

## Sanitization Strategy

This project was created as a clean personal documentation repository. It intentionally does not copy private source code, data, logs, deployment details, tool manifests, screenshots, reports, or internal project descriptions.

The public project keeps only:

- generic architecture ideas
- generic skill/tool extension design
- public-safe optimization plans
- privacy and review principles
- portfolio positioning

## Removed Or Excluded Content

The following categories must not be included:

| Category | Reason |
| --- | --- |
| API keys and `.env` files | Secret leakage risk. |
| Internal project names | Confidentiality and affiliation risk. |
| Institution or team names | Privacy and agreement risk. |
| Proprietary tool names or tool IDs | IP and workflow leakage risk. |
| Real workflow parameters | May reveal internal implementation. |
| Data files such as spreadsheets or databases | May contain proprietary or sensitive metadata. |
| Logs, caches, exports, reports | May contain user activity, paths, or generated sensitive content. |
| Model paths and weight locations | Infrastructure leakage risk. |
| Internal API routes and deployment notes | Security and confidentiality risk. |
| Patient, clinical, or slide data | Medical privacy risk. |

## Public-Safe Replacement Pattern

Use this replacement style:

| Private concept | Public-safe replacement |
| --- | --- |
| Internal tool platform | external analysis tool |
| Project-specific tool ID | public-safe mock tool ID |
| Real workflow | toy workflow |
| Real biomedical dataset | public dataset or synthetic fixture |
| Internal deployment path | local placeholder path |
| Institution-specific task | generic biomedical research task |

## Release Rule

Before any public release:

1. Search for private names and paths.
2. Confirm no `.env`, logs, Excel files, databases, or generated reports are present.
3. Confirm all examples are synthetic or public.
4. Confirm README does not imply clinical diagnosis capability.
5. Confirm every tool/skill description is generic.

