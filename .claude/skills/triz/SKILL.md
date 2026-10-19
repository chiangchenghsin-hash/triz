---
name: triz
description: "Applies the TRIZ Five-Bridges methodology to technical and product problems: problem clarification, experience-pain/IFR analysis, contradiction resolution (39 parameters, 40 principles), substance-field analysis and trimming, function modeling, and technology evolution forecasting, producing evaluated solution candidates and analysis reports. Use when the user mentions TRIZ, systematic innovation, technical contradiction, inventive problem solving, Five Bridges, IFR, substance-field, function trimming, or technology evolution/forecasting, or asks for structured innovation analysis of an engineering or product problem."
---

# TRIZ - Systematic Innovation Methodology

A comprehensive TRIZ (Theory of Inventive Problem Solving) tool that helps engineers and product managers systematically analyze technical problems and generate innovative solutions through the Five Bridges methodology.

## Description

TRIZ is a systematic approach to innovation that transforms complex technical challenges into structured problem-solving processes. This skill enables engineers and product managers to:

- Clarify technical problems through conversational guidance (≤5 interactions)
- Analyze user experience pain points and define Ideal Final Results (IFR)
- Apply the Five Bridges methodology to uncover innovation opportunities
- Generate validated innovative solutions in 4-5 minutes instead of 1-2 days
- Create comprehensive TRIZ analysis reports automatically

## When to Activate

- User mentions "TRIZ", "systematic innovation", "technical contradiction", "inventive problem solving"
- Engineering or product development discussions involving technical challenges
- Requests for innovation methodology or problem-solving frameworks
- Mentions of "Five Bridges", "IFR", "technical contradictions", "separation principles"
- Product design or engineering optimization contexts

## Key Features

- **Problem Clarification**: Interactive dialogue to transform vague requirements into structured technical problems
- **Experience Insight & IFR Definition**: Deep user experience analysis with Ideal Final Result definition
- **Problem Attribute Classification**: Automatic classification into general/parameter/structure/function categories
- **Five Bridges Analysis**: 
  - **Thinking Bridge**: Creative inspiration and system understanding
  - **Parameter Bridge**: Technical contradiction resolution using 40 inventive principles
  - **Structure Bridge**: System architecture and component relationship analysis
  - **Function Bridge**: Function modeling and trimming for system optimization
  - **Evolution Bridge**: Technology evolution trends and forecasting
- **Innovation Generation**: Generate 10 validated innovative solutions
- **Solution Evaluation**: Assess each solution across 8 critical factors including technical validation
- **Comprehensive Reporting**: Auto-generate complete TRIZ analysis reports with all analysis steps

## Usage Examples

- "Help me apply TRIZ to solve this technical contradiction in our product design"
- "Analyze this engineering problem using systematic innovation methodology"
- "Generate innovative solutions for this user experience pain point using TRIZ"
- "Create a complete TRIZ analysis report for this technical challenge"
- "Apply the Five Bridges methodology to this product development problem"

## Technical Details

- Implements classical TRIZ methodology with modern AI enhancements
- Supports all 40 inventive principles and separation methods
- Includes technology evolution patterns and forecasting
- Integrates user experience insights with technical problem solving
- Optimized for rapid analysis (4-5 minutes vs traditional 1-2 days)
- Accessible to engineers without TRIZ expertise

## Collaboration with the `security-variant-verification` skill

The pair is one product: TRIZ generates candidate designs; the companion
machine-verifies them. Cross-invocation is by skill name via the Skill tool —
never by file path.

### Handoff rules (TRIZ → SVV)

- Trigger (decidable): the solution must be **machine-verified against an
  implementation** — security property, model-vs-code agreement, or release
  gating. Do not improvise verification inside this skill.
- Hand off to `security-variant-verification` via the Skill tool, passing:
  the user's original intent (verbatim), the chosen solution as the spec, and
  the target repo/component absolute paths. The companion returns gate
  verdicts (exit-code enforced), not opinions.

### Reverse direction (SVV → TRIZ)

SVV hands back a filled contradiction card when a design gap or design
contradiction blocks its workflow (card format lives in its
`references/triz-mapping.md`). Treat the card as the problem statement and
run this skill's normal bridge flow on it.

### Boundaries — what this skill must NOT do

- No machine verdicts and no release-gate conclusions — that is the
  companion's job (differential testing + exit-code gate).
- No opportunistic work "along the way" inside a handoff scope.
- No recursive self-invocation while this skill is running; handoffs are
  one-shot, not loops.
