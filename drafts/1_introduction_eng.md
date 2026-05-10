# Introduction

> Author: 유도연   
> Date: 2026.04.30.   

---

## 1. Problem Statement

Buildings account for roughly one-third of global final energy consumption and approximately one-quarter of CO₂ emissions worldwide [29]. Accurate building energy modeling (BEM) is therefore a critical prerequisite for energy performance prediction, efficiency improvement, and consumption reduction [1]. However, building information models (BIM) and design drawings typically document only fundamental geometric and HVAC system configurations; non-geometric input parameters—including thermal properties, operational schedules, internal load densities, and thermostat setpoints—are either omitted or assigned default values [31]. Furthermore, these key inputs are subject to temporal change and deviation between design intent and actual operation, generating persistent discrepancies between simulated and measured energy use [1].

## 2. Research Gap

Closing this gap requires calibrating the building energy model against measured energy consumption data [1]. The calibration process, however, is notoriously labor-intensive, time-consuming, and case-dependent, making standardization and reproduction across diverse buildings difficult [1]. To automate and scale calibration, prior research has explored four principal directions: optimization-based methods such as genetic algorithms [4], rule- and pattern-based automation [11], multi-step or staged calibration procedures [4], and multi-agent and LLM-based frameworks [13]. Taken together, these approaches have substantially reduced the effort required compared to fully manual workflows.

Despite this progress, each direction carries a structural limitation. Optimization- and staged-calibration methods enable systematic, bounded search over a predefined parameter space but cannot perform semantic reasoning about residual patterns or adaptively interpret diagnostic context [4]. Rule- and pattern-based approaches encode domain knowledge as static if–then logic, providing a fixed form of inference while remaining unable to restructure the search space dynamically [11]. LLM-based and multi-agent frameworks exhibit flexible diagnostic reasoning, yet they generally lack structured search guarantees: calibration parameter sets and ranges are assembled on a case-by-case basis through unconstrained generation, yielding limited reproducibility and structural consistency [13].

In short, prior work has advanced either the search axis—through optimization and staged methods—or the reasoning axis—through diagnostic rules and LLM agents—but no automated calibration procedure has integrated both axes within a single, structured workflow.

To address this gap, this study proposes a two-stage calibration framework that integrates structured search (Stage 1) and structured reasoning (Stage 2) within a single automated procedure.

## 3. Contribution

The principal contribution of this work is a two-stage automated calibration framework that simultaneously unifies structured parameter-space search and reasoning-guided adjustment in a reproducible procedure. Stage 1 employs an Optuna-based hyperparameter optimization pipeline to conduct systematic, bounded exploration of calibration variables, narrowing the parameter search space and isolating structured residual patterns that inform the subsequent stage. Stage 2 deploys a constraint-bound LLM-based multi-agent system whose agent roles and operational boundaries are predefined, enabling reasoning-driven calibration without unconstrained free generation.

This design resolves two complementary limitations at once: it endows the optimization and staged-calibration paradigm with reasoning capability, and it imposes structural constraints on the free-generation tendency inherent in LLM-based approaches. The framework is evaluated on two real buildings with contrasting environmental conditions and operational characteristics, demonstrating improvements in simulation accuracy, stepwise ablation of each stage's contribution, interpretable agent-routing decisions, and elimination of manual case-specific redesign.
