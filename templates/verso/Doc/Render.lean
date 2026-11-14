import VersoManual

open Verso.Genre Manual

/-! Rendering configuration: colours for Lean tokens and a wider text column for statements. -/

def highlightTheme : String := "
.hl.lean .keyword { color: #9d0a6b; font-weight: 600; }
.hl.lean .const { color: #1a5fb4; }
.hl.lean .var { color: #2a6b3f; font-style: italic; }
.hl.lean .literal { color: #a1541c; }
html:root { --verso-content-max-width: 64rem; }
main pre, main code.block, main .hl.lean.block { overflow-x: auto; max-width: 100%; }
"

/-- Rendering configuration for `manualMain`. -/
def config : RenderConfig := {
  rootTocDepth := none,
  sectionTocDepth := some 2,
  extraCss := (([highlightTheme] : List String) : Std.HashSet CSS)
}
