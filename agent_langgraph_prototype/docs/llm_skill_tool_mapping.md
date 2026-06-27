# LLM -> Skill -> Tool Mapping

LLMs may propose a route, but the framework decides what is allowed.

```text
LLM proposal -> router -> skill -> catalog tool -> review gate
```

## Routing Bands

| Band | Use |
| --- | --- |
| general planner | intent and workflow planning |
| paper reasoning | public evidence planning |
| execution control | preflight and blocked execution placeholder |
| workspace memory | public/synthetic session context |
| platform ops | scheduler and harness placeholder checks |

## Safety Rule

Specialist outputs are evidence packets or plans. They are not verified facts
and they cannot bypass review gates.

