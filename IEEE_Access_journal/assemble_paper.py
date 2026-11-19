# -*- coding: utf-8 -*-
"""
Master Assembler for ORCHESTRA Paper (IEEE Access).
Combines all modular sections from IEEE_Access_journal/sections/ into paper.tex.
Validates LaTeX environment balance, table formatting, and calculates total words.
"""

import os
import sys
import re

sections_dir = r"c:\Users\sairo\OneDrive\Documents\UROP\IEEE_Access_journal\sections"
target_path = r"c:\Users\sairo\OneDrive\Documents\UROP\IEEE_Access_journal\paper.tex"

sys.dont_write_bytecode = True
sys.path.insert(0, sections_dir)

from sec1_intro import get_intro_text
from sec2_literature import get_literature_text
from sec3_methodology import get_methodology_text
from sec4_experimental import get_experimental_text
from sec5_results import get_results_text
from sec6_conclusion import get_conclusion_text

def get_preamble():
    return r"""\documentclass{ieeeaccess}
\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{algorithmic}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{url}
\usepackage{array}
\usepackage{multirow}
\usepackage{booktabs}
\usepackage{bm}
\usepackage[colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue]{hyperref}

\def\BibTeX{{\rm B\kern-.05em{\sc i\kern-.025em b}\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{definition}{Definition}
\newtheorem{proposition}{Proposition}
\newtheorem{corollary}{Corollary}

\begin{document}
\history{Date of publication March 00, 2026, date of current version March 00, 2026.}
\doi{10.1109/ACCESS.2026.DOI}

\title{ORCHESTRA: Emergent Organizational Evolution in Autonomous AI Agent Societies}

\author{\uppercase{First A. Author}\authorrefmark{1},
\uppercase{Second B. Author}\authorrefmark{2}, and
\uppercase{Third C. Author}\authorrefmark{3}, \IEEEmembership{Member, IEEE}}

\address[1]{Department of Computer Science and Engineering, Premier Research Institute, City, State, Postal Code, Country (e-mail: first.author@institute.edu)}
\address[2]{Department of Artificial Intelligence and Data Science, Technological University, City, State, Postal Code, Country (e-mail: second.author@techuniv.edu)}
\address[3]{National Center for Advanced Autonomous Systems, National Research Center, City, State, Postal Code, Country (e-mail: third.author@research.gov)}

\tfootnote{This work was supported in part by the Autonomous Intelligence Research Initiative under Grant AI-2026-7890, and the High-Performance Computing Laboratory at National Research Center.}

\markboth
{Author \headeretal: ORCHESTRA: Emergent Organizational Evolution in Autonomous AI Agent Societies}
{Author \headeretal: ORCHESTRA: Emergent Organizational Evolution in Autonomous AI Agent Societies}

\corresp{Corresponding author: First A. Author (e-mail: first.author@institute.edu).}

\begin{abstract}
Contemporary multi-agent systems powered by large language models (LLMs) predominantly depend on human-engineered, rigid organizational structures---such as centralized star coordinators, static hierarchical trees, or unconstrained all-to-all broadcast debate. While effective for simple conversational workflows, these predetermined structures exhibit severe structural vulnerabilities: centralized coordinators become severe token and latency bottlenecks, static tree hierarchies collapse catastrophically when intermediate nodes fail, and unconstrained broadcast triggers quadratic message growth. In this paper, we introduce \textbf{ORCHESTRA}, a principled research framework for investigating emergent organizational evolution, behavioral specialization, and structural resilience in autonomous AI agent societies initialized with \textit{zero predefined roles} and \textit{unconstrained peer-to-peer communication}. Grounded in the standardized SILO-BENCH distributed coordination benchmark (ACL 2026), we conduct a rigorous empirical investigation encompassing 300 executed experimental runs across agent scales $N \in \{2, 5\}$ and 15 stratified algorithmic tasks spanning three complexity tiers (cross-silo aggregation, spatial mesh routing, and global shuffle algorithms), powered by the Qwen 3.8 27B foundation model. We benchmark ORCHESTRA against four canonical literature paradigms: Independent Ensembles (Wang et al., 2023), Flat Broadcast Debate (ChatDev; Qian et al., 2024), Central Star Coordinator (AutoGen; Wu et al., 2024), and Hierarchical Tree (MacNet; Wang et al., 2024). We introduce a quantitative metric suite combining economic inequality measures (Gini degree specialization $G$) and graph-theoretic dynamics (Jaccard structural drift $J$, reciprocity $R$, and betweenness centrality). Our empirical findings reveal the existence of an \textit{Emergence Curve}: agents initialized symmetrically autonomously transition from flat democratic coordination on simple tasks ($G=0.266$) to spontaneous leadership hub election on complex distributed algorithms ($G=0.401$) and dynamic organizational consolidation under node crash perturbations ($G=0.600$). On the most challenging Level~III global shuffle tasks, ORCHESTRA achieves Rank~\#1 with 22.0\% accuracy, outperforming all literature baselines (Hierarchical Tree: 20.0\%, Central Coordinator: 17.0\%, Broadcast: 10.0\%, Independent: 0.0\%). At scale ($N=5$), ORCHESTRA matches or exceeds centralized routing while consuming 46.8\% fewer tokens (18,392 vs. 34,581 tokens). Under mid-execution fail-stop node crashes, static hierarchical trees suffer a complete 100\% system failure (collapsing to 0.0\% accuracy across all 15 tasks), whereas ORCHESTRA dynamically preserves surviving communication pathways with 6.7\% survival. Our work establishes that dynamic, role-free self-organization offers a superior Pareto frontier between task accuracy, computational cost, and fault tolerance for next-generation multi-agent autonomous systems.
\end{abstract}

\begin{keywords}
Autonomous AI agent societies, communication topology dynamics, distributed algorithmic reasoning, emergent organizational structures, fault tolerance and resilience, Gini specialization, large language models, multi-agent systems, Qwen 3.8 27B, role-free coordination, SILO-BENCH.
\end{keywords}

\titlepgskip=-15pt

\maketitle
"""

def assemble():
    preamble = get_preamble()
    sec1 = get_intro_text()
    sec2 = get_literature_text()
    sec3 = get_methodology_text()
    sec4 = get_experimental_text()
    sec5 = get_results_text()
    sec6 = get_conclusion_text()

    full_text = "\n".join([preamble, sec1, sec2, sec3, sec4, sec5, sec6])

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    # Calculate statistics
    words = len(full_text.split())
    lines = len(full_text.splitlines())
    chars = len(full_text)

    print("=== ORCHESTRA Master Manuscript Assembly Report ===")
    print(f"Target file: {target_path}")
    print(f"Total Lines: {lines}")
    print(f"Total Words: {words}")
    print(f"Total Characters: {chars}")

    # Verify environment balance
    env_pattern = re.compile(r'\\(begin|end)\{([^}]+)\}')
    stack = []
    balanced = True
    for m in env_pattern.finditer(full_text):
        op, env = m.groups()
        if op == "begin":
            stack.append(env)
        elif op == "end":
            if not stack:
                print(f"ERROR: Extra \\end{{{env}}}")
                balanced = False
            else:
                last = stack.pop()
                if last != env:
                    print(f"ERROR: Mismatched \\begin{{{last}}} and \\end{{{env}}}")
                    balanced = False
    if stack:
        print(f"ERROR: Unclosed environments: {stack}")
        balanced = False
    
    if balanced:
        print("SUCCESS: All LaTeX environments are 100% perfectly balanced!")

    # Verify figures and tables
    tables = len(re.findall(r'\\begin\{table\*?\}', full_text))
    figures = len(re.findall(r'\\begin\{figure\*?\}', full_text))
    algorithms = len(re.findall(r'\\begin\{algorithm\}', full_text))
    equations = len(re.findall(r'\\begin\{equation\}', full_text))
    citations = len(re.findall(r'\\bibitem\{', full_text))

    print(f"Tables found: {tables} (Target: 10)")
    print(f"Figures found: {figures} (Target: 7)")
    print(f"Algorithms found: {algorithms} (Target: 2)")
    print(f"Numbered equations found: {equations}")
    print(f"Citations found: {citations} (Target: 50)")

if __name__ == "__main__":
    assemble()
