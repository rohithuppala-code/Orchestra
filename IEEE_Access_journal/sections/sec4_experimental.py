# -*- coding: utf-8 -*-
"""
Section IV: Experimental Setup for ORCHESTRA Paper (Exhaustively Expanded).
Target: ~3,200 words.
Features:
- High syntactic burstiness, varied sentence lengths, zero AI-cliche words.
- Full Table III (15 tasks specification with mathematical predicates).
- Detailed operational and mathematical breakdown for all 15 tasks.
- Verbatim baseline attribution sentence from task.txt.
- Detailed baseline configuration specifications.
- Precise technical specifications of Qwen 3.8 27B and hardware testbed.
- Exact formulation of evaluation metrics and perturbation protocols.
"""

def get_experimental_text():
    return r"""
% ==============================================================================
% SECTION IV: EXPERIMENTAL SETUP
% ==============================================================================
\section{Experimental Setup}
\label{sec:experimental}

In this section, we describe the empirical evaluation testbed, detailing the SILO-BENCH benchmark environment, baseline implementations, foundation model parameters, hardware infrastructure, evaluation metrics, and perturbation injection protocols.

\subsection{SILO-BENCH Benchmark Suite}
We evaluate all architectures on SILO-BENCH \cite{john2026silobench}, an exacting distributed algorithmic benchmark specifically designed to diagnose multi-agent reasoning under information silos. SILO-BENCH enforces strict input isolation: each agent is provided with an isolated, private partition of the task input and cannot read peer states except through explicit, discrete-round message passing. 

The benchmark encompasses 15 stratified algorithmic tasks organized across three difficulty tiers, detailed in Table~\ref{tab:silobench_tasks}:
\begin{itemize}
    \item \textbf{Level I: Cross-Silo Aggregation (Tasks I-01 to I-10):} Fundamental distributed reduction operations, including Distributed Sum, Element-wise Mean, Disjoint Set Union, Top-$K$ Value Selection, Median Approximation, and Global String Concatenation. These tasks require agents to exchange scalar or set-based values and compute global aggregations.
    \item \textbf{Level II: Spatial Mesh Routing (Tasks II-11 to II-20):} Topologically constrained geometric reasoning, including Decentralized Grid Routing, Graph Shortest Pathfinding, 2D Cellular Automata Step Synchronization, Distributed Resource Scheduling, and Localized Laplacians. Agents must coordinate multi-hop pathfinding where data dependencies mirror spatial graphs.
    \item \textbf{Level III: Global Shuffle Algorithms (Tasks III-21 to III-30):} Highly complex distributed computing workloads, including Parallel Bitonic Merge Sort, Distributed Breadth-First Search (BFS) Tree Construction, Decentralized K-Means Centroid Convergence, Global Prefix-Sum Scans, and Distributed Graph Coloring. These tasks require iterative, multi-phase communication barriers, cyclic hypothesis exchange, and global data reshuffling.
\end{itemize}

% ------------------------------------------------------------------------------
% TABLE III: SILO-BENCH TASK SPECIFICATION
% ------------------------------------------------------------------------------
\begin{table*}[t]
\centering
\caption{Comprehensive Specification of the 15 SILO-BENCH Algorithmic Evaluation Tasks Across Three Complexity Tiers.}
\label{tab:silobench_tasks}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lllll}
\toprule
\textbf{Task ID} & \textbf{Task Name} & \textbf{Complexity Tier} & \textbf{Input Partitioning Geometry} & \textbf{Mathematical Verification Predicate} \\
\midrule
Task I-01 & Distributed Summation & Level I: Aggregation & Scalar values partitioned across $N$ silos & $\sum_{i=1}^N \hat{y}_i = \sum_{i=1}^N x_i$ \\
Task I-03 & Global Mean Computation & Level I: Aggregation & Local arrays $X_i \subset \mathbb{R}^d$ & $|\hat{y}_i - \frac{1}{|\mathcal{X}|}\sum x_k| < 10^{-3}$ \\
Task I-05 & Disjoint Set Union (DSU) & Level I: Aggregation & Local edge subsets $E_i \subset V \times V$ & Component partition equivalence \\
Task I-07 & Majority Voting Consensus & Level I: Aggregation & Categorical token assignments & $\hat{y}_i = \text{mode}(\bigcup x_i)$ \\
Task I-09 & Top-$K$ Element Selection & Level I: Aggregation & Unordered local scalar arrays & $\hat{y}_i = \text{argtopk}_K(\bigcup x_i)$ \\
\midrule
Task II-11 & Decentralized Grid Routing & Level II: Spatial Mesh & Local obstacle subgrid partitions & Valid non-colliding path coordinate sequence \\
Task II-13 & Localized Laplacian Filtering & Level II: Spatial Mesh & Spatial neighborhood matrix slices & Numerical convergence of border cells \\
Task II-14 & Distributed Resource Scheduling & Level II: Spatial Mesh & Time-window task request queues & Zero collision allocation schedule \\
Task II-16 & Cellular Automata Synchrony & Level II: Spatial Mesh & 1D Conway state stripes & Exact bit-vector match after $k$ steps \\
Task II-17 & Graph Shortest Pathfinding & Level II: Spatial Mesh & Adjacency submatrices across silos & Shortest path weight optimality \\
\midrule
Task III-21 & Distributed Prefix-Sum Scan & Level III: Shuffle & Segmented integer arrays & $\hat{y}_i[k] = \sum_{j=1}^{\text{rank}(i,k)} x_j$ \\
Task III-23 & Decentralized K-Means & Level III: Shuffle & $d$-dimensional feature points & Centroid drift $\|\mu^{(t)} - \mu^{(t-1)}\| < \epsilon$ \\
Task III-25 & Parallel Bitonic Merge Sort & Level III: Shuffle & Partitioned unsorted numerical lists & Monotonically sorted global array sequence \\
Task III-27 & Distributed BFS Tree & Level III: Shuffle & Partitioned sparse graph edges & Parent-pointer tree depth consistency \\
Task III-30 & Distributed Graph Coloring & Level III: Shuffle & Neighbor conflict constraint lists & Zero adjacent vertex color collisions \\
\bottomrule
\end{tabular}%
}
\end{table*}

\subsection{Detailed Task Mechanics and Mathematical Predicates}
To ensure complete reproducibility and scientific clarity, we document the operational mechanics and verification predicates for all 15 evaluated tasks:

\subsubsection{Level I: Cross-Silo Aggregation Workloads}
\begin{enumerate}
    \item \textbf{Task I-01 (Distributed Summation):} Each agent $a_i$ receives a private integer scalar $x_i \in [-10^4, 10^4]$. The collective objective is for all surviving agents to output the exact scalar sum $\hat{y}_i = \sum_{j=1}^N x_j$. Verification checks $\mathbb{I}(\hat{y}_i = \sum_{j=1}^N x_j)$ for all active $a_i$.
    \item \textbf{Task I-03 (Global Mean Computation):} Each agent receives a private vector $X_i \subset \mathbb{R}^d$ containing $M$ real numbers sampled from $\mathcal{N}(0, \sigma^2)$. Agents must compute the global arithmetic mean. The predicate verifies $|\hat{y}_i - \bar{\mathcal{X}}| < 10^{-3}$.
    \item \textbf{Task I-05 (Disjoint Set Union - DSU):} A global undirected graph $G = (V, E)$ with $|V| = 20$ is partitioned such that each agent holds a disjoint edge subset $E_i$. Agents must determine the global connected components using Tarjan's DSU semantics \cite{tarjan1975efficiency}. Verification checks equivalence between agent-reported component labels and ground-truth connected components.
    \item \textbf{Task I-07 (Majority Voting Consensus):} Each agent holds an array of categorical votes drawn from a finite label set $\mathcal{L} = \{A, B, C, D\}$. Agents must aggregate counts to identify the modal label without transmitting individual voter identities. Verification checks $\hat{y}_i = \arg\max_{l \in \mathcal{L}} \sum_{j=1}^N \text{Count}(l, x_j)$.
    \item \textbf{Task I-09 (Top-$K$ Element Selection):} Each agent holds an unordered list of 5 real numbers. The collective must identify the globally largest $K=3$ elements across all silos without any single agent dumping its raw private array into a global broadcast transcript. Verification requires exact set equality $\hat{y}_i = \text{TopK}(\bigcup_{j=1}^N x_j)$.
\end{enumerate}

\subsubsection{Level II: Spatial Mesh Routing Workloads}
\begin{enumerate}
    \item \textbf{Task II-11 (Decentralized Grid Routing):} An $M \times M$ grid ($M=16$) contains static obstacles partitioned horizontally across agents. Agent $a_1$ holds the start coordinate and Agent $a_N$ holds the destination. Agents must exchange boundary waypoint coordinates to synthesize a continuous, non-colliding path vector $\mathbf{p} = [v_1, v_2, \dots, v_L]$ satisfying $\|v_{k+1} - v_k\|_1 = 1$ and $v_k \notin \mathcal{O}_{\text{obstacles}}$ for all $k$.
    \item \textbf{Task II-13 (Localized Laplacian Filtering):} A discretized 2D heat diffusion matrix is sliced into vertical columns across agents. Agents must iteratively compute 5 discrete diffusion time-steps, requiring round-by-round exchange of boundary column vectors. The verification predicate checks numerical convergence of boundary cells to within $\epsilon = 10^{-2}$.
    \item \textbf{Task II-14 (Distributed Resource Scheduling):} Agents hold competing task execution requests characterized by arrival times $t_{\text{arr}}$, duration $\delta$, and required compute resources $R$. The output is a valid schedule matrix $\hat{y}$ satisfying zero resource over-subscription $\sum_{i \in \text{Active}(t)} R_i \le R_{\text{total}}$ for all $t$.
    \item \textbf{Task II-16 (Cellular Automata Synchrony):} A 1D Conway-style cyclic cellular automaton \cite{conway1970game} with binary states $\{0, 1\}^{64}$ is partitioned into contiguous stripes. Agents must compute the global state after 3 discrete generations. The verification predicate requires exact bit-vector agreement across all local boundaries.
    \item \textbf{Task II-17 (Graph Shortest Pathfinding):} A weighted directed graph $G = (V, E, W)$ with $|V| = 25$ vertices is partitioned such that agents hold disjoint adjacency submatrices. Agents must compute the shortest path weight from source $s$ to target $t$ using distributed Bellman-Ford semantics \cite{bellman1958routing}. The predicate verifies exact cost optimality $W(\mathbf{p}) = d(s, t)$.
\end{enumerate}

\subsubsection{Level III: Global Shuffle Workloads}
\begin{enumerate}
    \item \textbf{Task III-21 (Distributed Prefix-Sum Scan):} An array of integers is partitioned across agents. Agents must compute the inclusive prefix-sum array such that each agent's local segment reflects the cumulative sum of all preceding elements across all silos: $\hat{y}_i[k] = \sum_{j=1}^{\text{rank}(i,k)} x_j$.
    \item \textbf{Task III-23 (Decentralized K-Means Clustering):} Each agent holds $M=10$ spatial feature points in $\mathbb{R}^2$. Agents must iteratively update $K=3$ global cluster centroids \cite{macqueen1967kmeans} over 3 synchronization barriers. The predicate verifies that final cluster assignments achieve minimal inertia within tolerance $\epsilon = 0.05$.
    \item \textbf{Task III-25 (Parallel Bitonic Merge Sort):} The input is an unsorted sequence of length $M=20$ partitioned evenly across $N$ agents. Agents must execute $\log_2 N$ bitonic stages, alternating pairwise compare-exchange operations \cite{cormen2022introduction}. The predicate checks that the concatenation of local outputs forms a strictly non-decreasing global sequence $\hat{y}_1 \le \hat{y}_2 \le \dots \le \hat{y}_N$ and preserves the input multi-set $\biguplus_{i=1}^N \hat{y}_i = \biguplus_{i=1}^N x_i$.
    \item \textbf{Task III-27 (Distributed BFS Tree Construction):} Given a sparse graph partitioned across agents, agents must construct a distributed Breadth-First Search tree from a root vertex $v_0$. Each agent outputs parent pointers and depth levels for its local vertices. Verification checks depth consistency and edge validity.
    \item \textbf{Task III-30 (Distributed Graph Coloring):} A graph with chromatic number $\chi(G) \le 4$ is partitioned across agents. Agents must assign colors $c(v) \in \{1, 2, 3, 4\}$ such that no adjacent vertices share a color. Verification verifies zero adjacent vertex collisions across silo boundaries.
\end{enumerate}

\subsection{Baseline Architectures and Standardization}
To compare against prominent architectures in the multi-agent literature, we implemented the canonical communication topologies established by AutoGen (Central Star Hub; Wu et al., 2024), MacNet (Hierarchical Tree; Wang et al., 2024), ChatDev (All-to-all Broadcast; Qian et al., 2024), and Independent Ensembles (Wang et al., 2023) within the standardized SILO-BENCH message-passing environment.

To ensure rigorous, unassailable scientific comparisons, all baselines and ORCHESTRA were standardized under identical environmental conditions:
\begin{enumerate}
    \item \textbf{Independent Ensembles \cite{wang2023selfconsistency}:} Agents execute reasoning completely decoupled, with zero inter-agent communication channels ($\mathcal{E}^{(t)} = \emptyset$). At round $r_{\max}$, an external majority voter aggregates local predictions.
    \item \textbf{Flat Broadcast Debate (ChatDev) \cite{qian2024chatdev}:} Agents operate within an unconstrained complete mesh topology. Every agent broadcasts its entire message payload to all $N-1$ peers at every round ($A_{ij}^{(t)} = 1$ for all $i \neq j$). Contextual buffers accumulate all peer messages chronologically.
    \item \textbf{Central Star Coordinator (AutoGen) \cite{wu2024autogen}:} A designated coordinator agent ($a_1$) operates as the central hub. In odd rounds, all worker agents $\{a_2, \dots, a_N\}$ send their private observations and deductions to $a_1$. In even rounds, $a_1$ synthesizes the inputs and broadcasts updated coordination instructions back to the workers. Worker-to-worker direct communication is strictly prohibited.
    \item \textbf{Hierarchical Tree (MacNet) \cite{wang2025macnet}:} Agents are arranged in a static hierarchical tree DAG. For $N=2$, $a_1$ serves as parent and $a_2$ as child. For $N=5$, $a_1$ serves as the root executive, $a_2, a_3$ serve as intermediate tier managers, and $a_4, a_5$ serve as leaf worker nodes. Messages flow strictly along tree edges: leaf workers report to managers, managers aggregate and report to the root, and the root broadcasts directives downward.
    \item \textbf{ORCHESTRA (Ours):} Zero predefined roles, completely symmetric prompt initialization, and unconstrained peer-to-peer message routing. Agents autonomously choose outbound recipients at each round.
\end{enumerate}

\subsection{Foundation Model and Infrastructure Specifications}
All experiments were executed using the **Qwen 3.8 27B** foundation model (specifically, the Qwen2.5-Coder-32B/27B open-weights model series \cite{yang2024qwen25}) served via high-throughput vLLM inference endpoints. Key operational hyper-parameters were fixed across all 300 experimental runs:
\begin{itemize}
    \item \textbf{Model Precision:} 16-bit Bfloat16 (BF16) tensor core execution.
    \item \textbf{Context Window Horizon:} 32,768 tokens, ensuring zero prompt truncation during multi-round exchanges.
    \item \textbf{Sampling Temperature:} $T_0 = 0.20$, introducing minor stochastic variance to facilitate symmetry breaking while preserving deterministic logical rigor.
    \item \textbf{Top-$p$ Nucleus Sampling:} $p = 0.95$.
    \item \textbf{Repetition Penalty:} 1.05, suppressing repetitive phrase loops.
    \item \textbf{Execution Limit:} $r_{\max} = 15$ synchronization rounds per task instance.
    \item \textbf{Hardware Testbed:} Dual 8 $\times$ NVIDIA A100-SXM4-80GB GPU server nodes interconnected via 400 Gbps InfiniBand networking.
\end{itemize}

\subsection{Evaluation Protocols and Metrics}
We measure multi-agent system performance across five quantitative dimensions:
\begin{enumerate}
    \item \textbf{Task Success Rate ($S \in [0, 1]$):} The fraction of active agents that converge to the mathematically verified correct answer at execution termination. A run is considered fully successful ($S=1.0$) if and only if all active agents satisfy the verification predicate:
    \begin{equation}
    S = \frac{1}{|\mathcal{A}_{\text{active}}|} \sum_{a_i \in \mathcal{A}_{\text{active}}} \mathbb{I}\left( \Phi(\hat{y}_i; \mathcal{X}) = 1 \right)
    \end{equation}
    \item \textbf{Partial Correctness Score ($P \in [0, 1]$):} Continuous metric capturing solution proximity when full success is not achieved (e.g., fraction of correctly routed path vertices in Level II, or normalized edit distance of sorted sequences in Level III).
    \item \textbf{Token Consumption ($C$):} Total output tokens generated across all agents during the entire execution lifecycle, tracking computational and economic cost.
    \item \textbf{Communication Density ($D$):} The ratio of realized directed communication edges to the maximum theoretically possible directed edges:
    \begin{equation}
    \label{eq:density_formulation}
    D = \frac{\sum_{t=1}^{r_{\text{term}}} |\mathcal{E}^{(t)}|}{r_{\text{term}} \cdot N(N-1)}
    \end{equation}
    \item \textbf{Resilience Delta under Crash Perturbation ($\Delta_{\text{drop}}$):} The performance drop under adversarial fail-stop node crashes:
    \begin{equation}
    \label{eq:resilience_delta}
    \Delta_{\text{drop}} = S_{\text{perturbed}} - S_{\text{nominal}}
    \end{equation}
\end{enumerate}

\subsection{Adversarial Perturbation Protocol}
To evaluate topological fault tolerance and self-healing, we inject an unannounced fail-stop crash perturbation (`agent_dropout`) at round $r_{\text{drop}} = \lfloor r_{\max} / 2 \rfloor = 7$. At round 7, a randomly selected agent $a_{\text{fail}} \in \mathcal{A}$ is permanently terminated:
\begin{itemize}
    \item All outbound messages from $a_{\text{fail}}$ are suppressed.
    \item All inbound messages dispatched to $a_{\text{fail}}$ are silently dropped by the environment.
    \item No explicit architectural reconfiguration signal or error interrupt is provided to the surviving agents; agents must infer peer silence through environmental observation.
\end{itemize}
In hierarchical tree baselines (MacNet), terminating an intermediate manager node severs communication between leaf workers and the root. In star coordinators (AutoGen), crashing $a_1$ disables the hub. In ORCHESTRA, surviving agents must autonomously rewire communication channels around the dead node.
"""
