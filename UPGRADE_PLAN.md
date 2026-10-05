# ♟️ Chess Game — Systematic Review & Upgrade Plan

> **Repository:** `ThomasOP25/hacked-2026` · **Branch:** `rework`  
> **Codebase:** ~950 LOC across 4 Python files (Pygame)  
> **Reviewed:** 2026-10-04  

---

## Part 1: Systematic Code Review

### 1.1 Code Correctness — Rating: 🟡 7/10

#### ✅ What Works Correctly
- Standard piece movement (Rook, Bishop, Queen, Knight, King, Pawn) is properly implemented via direction vectors and max-step limits.
- Pawn double-step, diagonal captures, and en passant are correctly handled.
- Castling (both kingside and queenside) with proper checks: king/rook unmoved, squares empty, king doesn't pass through check.
- Legal move filtering via `get_strictly_legal_moves()` correctly simulates each move and verifies the king isn't left in check.
- Check, checkmate, and stalemate detection works.
- 50-move rule and 3-fold repetition draw detection are present.

#### 🐛 Bugs & Issues Found

| # | Severity | File | Line(s) | Issue |
|---|----------|------|---------|-------|
| 1 | **High** | `functions.py` | 176-181 | **Castling check moves king on board without updating board state.** The king's column is mutated (`piece.col = 5`) to test if the pass-through square is attacked, but `board[]` is never updated to reflect this. Since `king_checked()` iterates enemy pieces' `get_valid_moves()` which reads from `board[]`, the board still shows the king at its original position. This means the "can't castle through check" validation is **partially broken** — it works only because `king_checked` compares against `king.row, king.col` (the piece object), not the board array. If any enemy sliding piece's move generation relies on the board (which it does for blocking), the check could be missed. |
| 2 | **Medium** | `chess.py` | 117-119 | **King lookup doesn't guard against missing king.** If both kings were somehow removed (corrupted state), this loop would leave `king` as an uninitialized variable and crash on L121. Should use a safer lookup. |
| 3 | **Medium** | `chess.py` | 130-131 | **3-fold repetition hash doesn't include turn or castling rights.** The board hash is just piece positions. Two identical positions with different castling rights or different side-to-move are treated as the same — violating FIDE rules. |
| 4 | **Medium** | `ai.py` | 73-78 | **En passant capture in `simulate_move` doesn't verify the captured piece is an enemy pawn.** It captures *any* piece on `(start_row, end_col)`, which could theoretically include a friendly piece in a corrupted state. |
| 5 | **Low** | `ai.py` | 170 | **Rook castling undo always sets `has_moved = False`**, but the rook may have already moved and been restored to its original square in a complex game. The undo should restore the rook's *original* `has_moved` state, not blindly set `False`. |
| 6 | **Low** | `chess.py` | 86-87 | **`dead_pieces_white` / `dead_pieces_black` are tracked but never displayed.** Dead code with no visual output. |
| 7 | **Low** | `chess.py` | 150 | **`import ai` inside the game loop** — re-imports every AI turn. Should be a top-level import. |
| 8 | **Low** | `chess.py` | 100-101 | **`halfmove_clock` and `history` don't reset on game restart** because there's no restart mechanism. |

#### 🔧 Code Smell / Maintainability Issues
- Heavy use of `piece.__class__.__name__.lower()` throughout — should use `isinstance()` checks or a `piece_type` attribute.
- `get_piece()` returns `False` instead of `None` on failure — inconsistent with Python conventions.
- Board representation uses Unicode emoji strings instead of piece references, creating a dual-state system (objects + board array) that must stay synchronized.
- No type hints anywhere — makes refactoring risky.
- No unit tests — rule correctness can only be verified by manual play.

---

### 1.2 Logic & Game Mechanics — Rating: 🟡 7/10

#### ✅ Complete Mechanics
| Rule | Status | Notes |
|------|--------|-------|
| Standard movement | ✅ | All 6 piece types correct |
| Captures | ✅ | Including en passant |
| Castling | ✅ | Kingside & queenside with validation |
| Check detection | ✅ | Iterates all enemy pseudo-legal moves |
| Checkmate | ✅ | No legal moves + in check |
| Stalemate | ✅ | No legal moves + not in check |
| Pawn promotion | ⚠️ | Auto-queen only — no piece choice |
| 50-move rule | ✅ | Tracks halfmove clock |
| 3-fold repetition | ⚠️ | Hash doesn't include turn/castling/en-passant rights |
| Insufficient material | ❌ | Not implemented (K vs K, K+B vs K, etc.) |
| Move history / undo | ❌ | No undo/redo support |
| PGN / FEN support | ❌ | No import/export |
| Time controls | ❌ | No clock system |

#### Missing UX Mechanics
- No "new game" / restart button
- No game mode selection screen (PvP vs PvAI)
- No move notation display
- No last-move highlight on the board
- No sound effects
- Winner announcement doesn't specify *who* won

---

### 1.3 AI Complexity — Rating: 🟠 5/10

#### Current Implementation
- **Algorithm:** Minimax with alpha-beta pruning — solid classical approach.
- **Depth:** Configurable 1-3 via keyboard (1/2/3 keys).
- **Evaluation function:** Material only + small center-control bonus.
- **Move ordering:** None — significantly hurts alpha-beta pruning efficiency.
- **Opening book:** None — AI plays from scratch every game.
- **Endgame tables:** None.

#### Detailed AI Weaknesses

| Issue | Impact | Details |
|-------|--------|---------|
| **No move ordering** | High | Alpha-beta's efficiency depends critically on examining good moves first. Without ordering (captures, checks, promotions first), the pruning is nearly ineffective, making depth 3 very slow. |
| **Primitive evaluation** | High | Only counts material + tiny center bonus. Missing: king safety, pawn structure (doubled/isolated/passed pawns), piece mobility, rook on open files, bishop pair bonus, piece-square tables. |
| **No transposition table** | Medium | Same positions reached via different move orders are re-evaluated. A hash table (Zobrist hashing) would dramatically reduce search time. |
| **No quiescence search** | High | Search stops at fixed depth even mid-capture sequence, causing the "horizon effect" — AI may blunder by pushing a losing capture sequence just past the search horizon. |
| **No iterative deepening** | Medium | Can't gracefully handle time limits. With iterative deepening, the AI could search deeper when it has time and return the best move found so far if interrupted. |
| **No opening book** | Low | AI makes suboptimal opening moves. |
| **Always promotes to Queen** | Low | Rare edge case, but underpromotion (to Knight) can be the only way to avoid stalemate or deliver checkmate. |
| **AI blocks UI during thinking** | Medium | `get_best_move()` runs synchronously, freezing the window at depth 3+. Should run in a separate thread. |

---

### 1.4 Visual Appeal — Rating: 🔴 3/10

#### Current State
- **Board:** Simple colored rectangles (green/cream) — functional but flat.
- **Pieces:** Single-letter text ("K", "Q", "R", etc.) with a gray shadow — **not actual chess piece images** despite `download_assets.py` existing. The downloaded PNG images are never used.
- **Window:** Fixed 512×512, no resizing.
- **UI Elements:** Only a small "AI Depth: X" text in the corner. No menus, no panels, no captured-piece display.
- **Game Over:** Plain text overlay with a gray semi-transparent background.
- **Highlights:** Green circles for valid moves, subtle highlight on selected square — decent but could be much better.
- **No animations** — pieces teleport instantly.
- **No sound** — completely silent.
- **No theming** — single hardcoded color scheme.

#### What's Missing Visually
- Piece images (PNGs are downloaded but never loaded/used)
- Rank/file labels (a-h, 1-8) on board edges
- Captured pieces display panel
- Move history sidebar
- Last-move highlight (from/to squares)
- Check highlight (red tint on checked king's square)
- Piece drag-and-drop
- Move animation (smooth sliding)
- Title screen / menu
- Board coordinates
- Player name / turn indicator
- Responsive/resizable window

---

## Part 2: Comprehensive Upgrade Plan

### Design Philosophy
Each phase is **self-contained and shippable** — the game improves meaningfully after each phase. Phases are ordered by impact-to-effort ratio. Earlier phases are marked for **Gemini 3.8 Flash High** (faster, simpler tasks) and later phases for **Gemini 3.1 Pro High** (complex reasoning, architecture).

---

### 🔵 Phase 1 — Bug Fixes & Code Quality (Foundation)
> **Assignee:** Gemini 3.8 Flash High  
> **Estimated effort:** Small  
> **Priority:** Critical — must be done first  

#### Tasks

- [ ] **1.1** Move `import ai` to top-level in `chess.py` (L150)
- [ ] **1.2** Replace all `piece.__class__.__name__.lower()` with a `piece.piece_type` string attribute set in the `Piece.__init__` constructor (e.g., `self.piece_type = "pawn"`)
- [ ] **1.3** Change `get_piece()` to return `None` instead of `False` when no piece found
- [ ] **1.4** Add guard clause for king lookup in game loop (handle missing king gracefully)
- [ ] **1.5** Fix castling validation in `get_strictly_legal_moves()` — update `board[]` when testing pass-through squares, not just `piece.col`
- [ ] **1.6** Fix 3-fold repetition hash to include: turn color, castling rights (4 booleans), en passant target square
- [ ] **1.7** Fix `unmake_move()` rook `has_moved` restoration — save and restore original value instead of hardcoding `False`
- [ ] **1.8** Add type hints to all function signatures across all files
- [ ] **1.9** Add `__repr__` methods to piece classes for debugging
- [ ] **1.10** Add a `requirements.txt` with `pygame` pinned

#### Acceptance Criteria
- All existing game functionality still works identically
- No `__class__.__name__` usage remains
- Type hints on all public functions
- Castling through check is properly blocked in all edge cases

---

### 🔵 Phase 2 — Visual Overhaul (Piece Images & Board Polish)
> **Assignee:** Gemini 3.8 Flash High  
> **Estimated effort:** Medium  
> **Priority:** High — biggest user-facing impact  

#### Tasks

- [ ] **2.1** Load piece PNG images from `assets/images/` into a dictionary at startup (use `pygame.image.load` + `pygame.transform.scale` to fit `SQ_SIZE`)
- [ ] **2.2** Replace text-based piece rendering in `draw_pieces()` with image blitting
- [ ] **2.3** Add rank (1-8) and file (a-h) labels along board edges — adjust `WIDTH`/`HEIGHT` to accommodate a margin (e.g., 30px on left and bottom)
- [ ] **2.4** Add a last-move highlight: draw the from-square and to-square with a distinct color (e.g., soft yellow `(255, 255, 120, 80)`)
- [ ] **2.5** Add a check highlight: tint the checked king's square red
- [ ] **2.6** Display captured pieces in a panel — extend window width by ~150px on the right, show captured white pieces on top and black on bottom
- [ ] **2.7** Add a turn indicator text (e.g., "White to move" / "Black to move") in the side panel
- [ ] **2.8** Improve game-over overlay — larger centered modal with winner text ("White wins by checkmate!", "Draw by stalemate", etc.), and a "New Game" button
- [ ] **2.9** Update `download_assets.py` to verify images exist before downloading, and auto-run it if images are missing when `chess.py` starts
- [ ] **2.10** Increase default `MAX_FPS` from 15 to 60 for smoother rendering

#### File Changes
- `chess.py` — major rendering refactor, window size increase
- `download_assets.py` — add verification logic
- New: `assets/` directory with 12 piece PNGs

#### Acceptance Criteria
- All 12 piece types render as proper chess piece images
- Board has coordinate labels
- Last move and check states are visually distinct
- Captured pieces visible in side panel
- Game over screen names the winner and offers restart

---

### 🔵 Phase 3 — UX & Interaction Improvements
> **Assignee:** Gemini 3.8 Flash High  
> **Estimated effort:** Medium  
> **Priority:** High  

#### Tasks

- [ ] **3.1** Implement a **start screen** with: title, "Play vs AI" button, "Play vs Human" button, difficulty selector (Easy/Medium/Hard)
- [ ] **3.2** Add a **"New Game"** button accessible during gameplay (corner button or `R` key)
- [ ] **3.3** Implement **piece drag-and-drop**: on mouse down, pick up piece; on mouse move, render piece at cursor; on mouse up, drop on target square (with snap-back if invalid)
- [ ] **3.4** Add **move animation**: when a move is made (including AI moves), smoothly slide the piece from start to end square over ~200ms
- [ ] **3.5** Add **sound effects**: piece move, capture, check, castling, game over (use small .wav files, generate or source free sounds)
- [ ] **3.6** Implement **pawn promotion UI**: when a pawn reaches the back rank, show a popup with Queen/Rook/Bishop/Knight choices
- [ ] **3.7** Add **move history panel**: display algebraic notation (e.g., "1. e4 e5 2. Nf3 ...") in the side panel with scrolling
- [ ] **3.8** Add **undo move** button (`Ctrl+Z` or button) — revert last move (and AI's response in PvAI mode)
- [ ] **3.9** Highlight legal moves more clearly: use **transparent circles on empty squares** and **corner triangles on capturable squares** (matching chess.com / lichess style)
- [ ] **3.10** Add **keyboard shortcuts**: `F` to flip the board, `R` to restart, `Esc` to return to menu

#### Acceptance Criteria
- Game can be started from a menu with mode and difficulty selection
- Pieces can be dragged and dropped
- Moves animate smoothly
- Pawn promotion offers all 4 piece choices
- Move history visible in algebraic notation
- At least move/capture/check sounds play

---

### 🟣 Phase 4 — AI Engine Upgrade (Competitive Play)
> **Assignee:** Gemini 3.1 Pro High  
> **Estimated effort:** Large  
> **Priority:** High — core gameplay depth  

#### Tasks

- [ ] **4.1** Implement **piece-square tables** (PST) for all piece types — different positional value based on square location, with separate middlegame and endgame tables
- [ ] **4.2** Enhance evaluation function with:
  - Pawn structure: doubled pawns (-), isolated pawns (-), passed pawns (+), connected pawns (+)
  - King safety: pawn shield around castled king (+), open files near king (-)
  - Piece mobility: count of legal moves for each piece (+)
  - Bishop pair bonus (+)
  - Rook on open/semi-open file bonus (+)
  - Knight outpost bonus (+)
- [ ] **4.3** Implement **move ordering** heuristics:
  - MVV-LVA (Most Valuable Victim - Least Valuable Attacker) for captures
  - Killer move heuristic (store moves that caused beta cutoffs at each depth)
  - History heuristic (track how often each move causes cutoffs)
  - Sort: PV move > captures (MVV-LVA) > killer moves > history moves > quiet moves
- [ ] **4.4** Add **quiescence search** — after reaching the search depth, continue searching only capture moves until the position is "quiet" (no more captures). Apply a stand-pat evaluation to allow the side to choose not to capture.
- [ ] **4.5** Implement **Zobrist hashing** and a **transposition table**:
  - Generate random 64-bit keys for each (piece, square) combination, turn, castling rights, en passant file
  - XOR-based incremental hash updates on make/unmake
  - Store: hash → (depth, score, flag [EXACT/ALPHA/BETA], best_move)
  - Probe table before searching; store results after
- [ ] **4.6** Implement **iterative deepening**:
  - Search depth 1, then depth 2, …, up to max depth or time limit
  - Use the best move from the previous iteration as the PV move for ordering
  - Enables time management and "anytime" behavior
- [ ] **4.7** Run AI search in a **separate thread** (using `threading.Thread`) so the UI remains responsive. Show a "Thinking..." indicator while the AI is computing.
- [ ] **4.8** Add **5 difficulty levels** instead of 3:
  - Beginner (depth 1, random noise in evaluation)
  - Easy (depth 2, basic evaluation)
  - Medium (depth 3, full evaluation)
  - Hard (depth 4, full evaluation + move ordering)
  - Expert (depth 5+, iterative deepening with 5-second time limit)
- [ ] **4.9** Add an **opening book** — embed a small dictionary of common openings (Sicilian, Italian, Queen's Gambit, etc.) as a trie. If the current move sequence matches, play the book move instantly.
- [ ] **4.10** Implement **game phase detection** (opening/middlegame/endgame based on material count) and switch PSTs accordingly.

#### New Files
- `evaluation.py` — all evaluation logic, PSTs, pawn structure analysis
- `search.py` — minimax, quiescence, transposition table, iterative deepening
- `opening_book.py` — opening book data and lookup
- Refactor `ai.py` to be a thin coordinator importing the above

#### Acceptance Criteria
- AI at depth 4+ plays significantly stronger than the current depth 3
- No UI freezing during AI thinking
- Transposition table reduces node count by ≥40% on average
- Move ordering causes alpha-beta to prune ≥60% of nodes
- Opening book covers at least 10 common openings to depth 6

---

### 🟣 Phase 5 — Architecture & Robustness
> **Assignee:** Gemini 3.1 Pro High  
> **Estimated effort:** Large  
> **Priority:** Medium — long-term maintainability  

#### Tasks

- [ ] **5.1** **Refactor board representation** — replace the dual-state system (piece objects + 2D emoji array) with a single source of truth. Options:
  - **Option A (recommended):** Board stores piece references directly (`board[row][col] = piece_obj or None`), and emoji conversion happens only at render time.
  - **Option B:** Bitboard representation for maximum performance (complex but fast).
- [ ] **5.2** Extract game state into a `GameState` class encapsulating:
  - `board`, `pieces`, `turn`, `last_move`, `halfmove_clock`, `history`, `castling_rights`, `game_phase`
  - Methods: `make_move()`, `unmake_move()`, `is_check()`, `is_checkmate()`, `is_draw()`, `get_legal_moves()`
  - This eliminates the scattered state management across `chess.py`, `functions.py`, and `ai.py`
- [ ] **5.3** Implement **FEN import/export** — parse and generate Forsyth-Edwards Notation for any position. Enables:
  - Saving/loading games
  - Setting up custom positions
  - Debugging specific scenarios
- [ ] **5.4** Implement **PGN export** — save completed games in Portable Game Notation format
- [ ] **5.5** Add a comprehensive **test suite** using `pytest`:
  - Move generation tests (perft tests at depth 1-4 for known positions)
  - Rule tests: en passant, castling, promotion, check, checkmate, stalemate
  - AI evaluation tests: verify known winning positions score correctly
  - Edge cases: insufficient material, 50-move rule, 3-fold repetition
- [ ] **5.6** Implement **insufficient material draw detection** (K vs K, K+B vs K, K+N vs K, K+B vs K+B same color)
- [ ] **5.7** Add **time controls** — optional chess clock (blitz: 3+2, rapid: 10+0, classical: 30+0). Display countdown timers in the side panel. Flag fall = loss.
- [ ] **5.8** Create a proper **MVC separation**:
  - `model/` — game state, rules, pieces
  - `view/` — all Pygame rendering
  - `controller/` — input handling, AI coordination
- [ ] **5.9** Add **logging** — use Python's `logging` module to log moves, AI thinking depth/time/nodes, and errors
- [ ] **5.10** Update `README.md` with: features list, screenshots, installation instructions, controls guide, architecture diagram

#### Acceptance Criteria
- Single source of truth for board state
- GameState class fully encapsulates game logic
- Test suite with ≥80% code coverage
- FEN strings can be imported/exported correctly
- `README.md` is comprehensive and includes screenshots

---

### 🟣 Phase 6 — Polish & Advanced Features (Stretch Goals)
> **Assignee:** Gemini 3.1 Pro High  
> **Estimated effort:** Large  
> **Priority:** Low — nice-to-haves  

#### Tasks

- [ ] **6.1** **Board themes** — selectable color schemes (classic green, blue, brown, dark mode, tournament). Store as named tuples or a config file.
- [ ] **6.2** **Piece set selection** — support multiple piece image sets (classic, modern, minimalist). Load from subdirectories under `assets/`.
- [ ] **6.3** **Move arrow drawing** — right-click drag to draw analysis arrows on the board (like chess.com)
- [ ] **6.4** **Square highlighting** — right-click to highlight squares with colors for analysis
- [ ] **6.5** **Board flip animation** — smooth 180° rotation when pressing `F`
- [ ] **6.6** **AI analysis mode** — show the AI's evaluation bar (advantage meter) and principal variation in real-time
- [ ] **6.7** **Puzzle mode** — load tactical puzzles from a database (e.g., Lichess puzzle CSV) and present them as "find the best move" challenges
- [ ] **6.8** **Game review** — after game ends, allow stepping through moves with arrows keys, showing AI evaluation at each point
- [ ] **6.9** **Multiplayer over network** — basic TCP socket-based play between two machines on the same network
- [ ] **6.10** **Pre-move support** — allow the player to queue a move during the AI's thinking time

---

## Phase Dependency Graph

```
Phase 1 (Bugs/Quality) ──────────────────────┐
    │                                         │
    ▼                                         ▼
Phase 2 (Visuals) ──► Phase 3 (UX) ──► Phase 6 (Polish)
    │                     │
    ▼                     ▼
Phase 4 (AI) ────────► Phase 5 (Architecture)
```

- **Phase 1** must be completed first (foundation)
- **Phases 2 & 4** can be done in parallel after Phase 1
- **Phase 3** depends on Phase 2 (needs the visual framework)
- **Phase 5** depends on Phases 3 & 4 (refactors everything they built)
- **Phase 6** depends on Phase 5 (builds on the clean architecture)

---

## Summary

| Phase | Assignee | Focus | Tasks | Impact |
|-------|----------|-------|-------|--------|
| 1 | Flash High | Bug fixes & code quality | 10 | 🔧 Foundation |
| 2 | Flash High | Visual overhaul | 10 | 🎨 Major UX lift |
| 3 | Flash High | Interaction & UX | 10 | 🖱️ Modern feel |
| 4 | Pro High | AI engine upgrade | 10 | 🧠 Competitive AI |
| 5 | Pro High | Architecture & testing | 10 | 🏗️ Maintainability |
| 6 | Pro High | Polish & stretch goals | 10 | ✨ Wow factor |

**Total: 60 tasks across 6 phases**

> [!TIP]
> Start with Phase 1 + Phase 2 together for the fastest visible improvement. The game will go from "hackathon prototype" to "polished chess app" in just these two phases.
