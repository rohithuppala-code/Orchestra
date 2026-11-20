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

\def\referencefont{\normalsize}

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
Contemporary multi-agent systems powered by large language models (LLMs) predominantly depend on human-engineered, rigid topologies such as centralized coordinators or static trees. These predetermined structures introduce critical vulnerabilities: central hubs become token bottlenecks, static hierarchies collapse catastrophically under node failure, and unconstrained broadcast triggers quadratic message growth. We present \textbf{ORCHESTRA}, an autonomous multi-agent framework investigating emergent organizational evolution, behavioral specialization, and structural resilience in agent societies initialized with \textit{zero predefined roles} and \textit{unconstrained peer-to-peer communication}. Grounded in the standardized SILO-BENCH benchmark across 300 controlled experimental runs using the Qwen 3.8 27B model, we benchmark ORCHESTRA against four canonical paradigms: Independent Ensembles, Flat Broadcast Debate (ChatDev), Central Coordinator (AutoGen), and Hierarchical Tree (MacNet). We introduce a quantitative metric suite combining economic inequality measures (Gini out-degree specialization $G$) and graph dynamics (Jaccard structural drift $J$, reciprocity $R$, and betweenness centrality). Our findings reveal an empirical \textit{Emergence Curve}: agents autonomously transition from flat democratic coordination on simple tasks ($G=0.266$) to spontaneous leadership hub election on complex distributed algorithms ($G=0.401$) and dynamic organizational consolidation under node crashes ($G=0.600$). On Level~III global shuffle tasks, ORCHESTRA achieves Rank~\#1 with 22.0\% accuracy, outperforming all baselines. At scale ($N=5$), ORCHESTRA delivers 28.0\% accuracy on spatial mesh routing while saving 46.8\% tokens over AutoGen. Under mid-execution node failure, while static hierarchical trees suffer complete 100\% collapse (0.0\% accuracy), ORCHESTRA dynamically self-heals surviving pathways (6.7\% survival). Our work demonstrates that role-free self-organization establishes an optimal Pareto frontier across accuracy, computational efficiency, and fault tolerance.
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
    bibitems = re.findall(r'\\bibitem\{([^}]+)\}', full_text)
    citations = len(bibitems)

    cites = set(re.findall(r'\\cite\{([^}]+)\}', full_text))
    all_cited = set()
    for c in cites:
        for k in c.split(','):
            all_cited.add(k.strip())
    missing_cites = all_cited - set(bibitems)
    unused_cites = set(bibitems) - all_cited

    print(f"Tables found: {tables} (Target: 10)")
    print(f"Figures found: {figures} (Target: 9: 4 draw.io diagrams + 5 empirical plots)")
    print(f"Algorithms found: {algorithms} (Target: 2)")
    print(f"Numbered equations found: {equations}")
    print(f"Citations found: {citations} (Target: 50)")
    print(f"Distinct cited keys in text: {len(all_cited)} / {len(bibitems)}")
    if missing_cites:
        print(f"WARNING: Missing bibitems for cited keys: {missing_cites}")
    if unused_cites:
        print(f"WARNING: Unused bibitems: {unused_cites}")

if __name__ == "__main__":
    assemble()
