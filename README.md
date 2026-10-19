# TRIZ - Systematic Innovation Methodology

A comprehensive OpenClaw skill that implements the complete TRIZ (Theory of Inventive Problem Solving) methodology to help engineers and product managers solve technical problems systematically.

## Overview

TRIZ is a powerful problem-solving methodology developed by Genrich Altshuller that provides systematic approaches to innovation. This skill implements the "Five Bridges" approach to make TRIZ accessible to engineers who may not be familiar with the full methodology.

**Key Benefits:**
- Reduces traditional 1-2 day TRIZ analysis to 4-5 minutes
- Makes TRIZ accessible to non-experts while maintaining professional quality
- Integrates user experience insights with technical problem solving
- Generates structured innovative-solution candidates with multi-criteria evaluation

## Core Methodology

### The Five Bridges of TRIZ

1. **Thinking Bridge** - Creative thinking and system understanding
2. **Parameter Bridge** - Resolving technical contradictions using 39 parameters and 40 principles
3. **Structure Bridge** - Analyzing and improving system structure using substance-field analysis
4. **Function Bridge** - Function modeling and trimming for system optimization
5. **Evolution Bridge** - Applying patterns of technical evolution to predict future improvements

### Nine-Step Analysis Process

#### AA-01: Problem Clarification
- Dialog-based guidance (≤5 interactions)
- Captures domain expertise from engineers
- Transforms fuzzy requirements into structured technical problems

#### AA-02: Experience Insight & IFR Definition
- Deep analysis of user experience pain points
- Defines Ideal Final Result (IFR)
- Classifies problem attributes (general/parameter/structure/function)
- Recommends which TRIZ bridges to execute

#### AA-03 to AA-07: Five Bridges Analysis
- **AA-03**: Thinking Bridge Analysis (for general attribute problems)
- **AA-04**: Parameter Bridge Analysis (for parameter contradictions)
- **AA-05**: Structure Bridge Analysis (for structural issues)
- **AA-06**: Function Bridge Analysis (for functional problems)
- **AA-07**: Evolution Bridge Analysis (for evolutionary opportunities)

#### AA-08: Solution Innovation & Evaluation
- Synthesizes results from all five bridges
- Generates 10 innovative solutions
- Evaluates each solution across 8 criteria including technical validation

#### AA-09: Complete Report Generation
- Generates comprehensive TRIZ analysis report
- Includes all analysis steps and results
- Provides actionable recommendations

## Usage Examples

### Basic Problem Analysis
```
Analyze this technical problem using TRIZ methodology: [describe your problem]
```

### Specific Innovation Request
```
Use TRIZ to find innovative solutions for improving battery life in smart watches
```

### User Experience Focus
```
Apply TRIZ to solve user complaints about slow app loading times
```

### Comprehensive Analysis
```
Perform complete TRIZ analysis on our manufacturing process bottleneck
```

## Technical Implementation

### Problem Attribute Classification
The skill automatically classifies problems into four categories:
- **General**: Broad system-level issues requiring creative thinking
- **Parameter**: Technical contradictions between conflicting parameters
- **Structure**: Issues with system components and their relationships
- **Function**: Problems with system functions and interactions

### TRIZ Tools Implemented

#### Parameter Bridge
- **39 Engineering Parameters**: Complete parameter matrix
- **40 Inventive Principles**: All classical TRIZ principles
- **Contradiction Matrix**: Automated contradiction resolution

#### Structure Bridge  
- **Substance-Field Analysis**: Standard and incomplete models
- **76 Standard Solutions**: Complete standard solution library
- **System Trimming**: Function-based component elimination

#### Function Bridge
- **Function Modeling**: Complete function analysis
- **Function Cost Analysis**: Resource efficiency evaluation
- **Idealization**: Moving toward ideal final result

#### Evolution Bridge
- **8 Patterns of Evolution**: Complete evolutionary trends
- **Technology Forecasting**: Future state prediction
- **Maturity Assessment**: Technology lifecycle analysis

### Solution Evaluation Criteria
Each generated solution is evaluated on 8 dimensions:
1. **Technical Feasibility** - Can it be implemented with current technology?
2. **Cost Effectiveness** - What's the cost-benefit ratio?
3. **User Impact** - How much does it improve user experience?
4. **Implementation Complexity** - How difficult is it to implement?
5. **Risk Level** - What are the potential risks?
6. **Time to Market** - How quickly can it be deployed?
7. **Scalability** - Can it scale to larger applications?
8. **Sustainability** - Is it environmentally and economically sustainable?

## Repository layout

- `.claude/skills/triz/` — the TRIZ skill: `SKILL.md`, `triz.js`, `templates/`,
  `examples/` (a self-contained skill directory — the layout every skills
  scanner registers one level deep)

This repo ships the generation half of a pair. The adjudication half is the
companion skill **[security-variant-verification](https://github.com/chiangchenghsin-hash/security-variant-verification)**
(its own project — install it separately): TRIZ's "validated solutions" are
heuristic evaluations (opinions); anything that must be machine-verified
against a production implementation — security properties, model-vs-code
agreement, release gating — goes to SVV, which returns gate verdicts
(differential testing + exit-code gate), not opinions. The two skills invoke
each other by skill name via the Skill tool (handoff rules and boundaries in
each `SKILL.md`).

## Installation

```bash
./install.sh
# -> ~/.openclaw/skills/triz/   (SKILL.md + triz.js + templates/ + examples/)
```

Companion (optional, for the full generate→verify loop): install from
[security-variant-verification](https://github.com/chiangchenghsin-hash/security-variant-verification).
On platforms that load skills from directories (Claude Code project skills,
WorkBuddy, other OpenClaw-style workspaces), copy each project's skill
directory in side by side and keep its bundled files.

## License

MIT License - Free to use and modify.
