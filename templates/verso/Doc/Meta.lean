import VersoManual

/-!
# Helpers for the document: the formalization's files, shown verbatim and checked

* `{sourceFile "../formal/comparator.json"}` inserts a file as a code block, read from disk *while
  the document is elaborated*: what the reader sees is the file itself, not a transcription.
  `(from := "text")` starts at the first line containing `text`; `(to := "text")` stops after the
  first following line containing `text`.
* A code block ```` ```libcode "../formal/{{LEAN_NAME}}/Main.lean" ```` is a `lean` code block (same
  options) whose text must be a *verbatim excerpt* of the given library file: the build fails if
  the library source no longer contains it.  The excerpt is then re-elaborated like any `lean`
  block, so the reader gets the library's own proof, with hovers and proof states.
* `{moduleTable}` renders a table of the modules of `../formal` -- lines, declarations, and
  project-internal imports -- computed from the sources while the document is elaborated.

Relative paths are resolved against the root of the Verso project (the directory containing
`lakefile.toml`).  Lake does not track these files as dependencies, so `scripts/remote-build.sh`
rebuilds the document from scratch every time.
-/

open Lean Elab
open Verso Doc Elab ArgParse
open Verso.Genre Manual

namespace DocMeta

/-- `true` iff `pat` occurs in `s` (for nonempty `pat`). -/
def hasInfix (s pat : String) : Bool := (s.splitOn pat).length > 1

/-- Candidate locations of a project-relative path: the working directory of Lake (the project
root) and the parents of the directory of the document file being elaborated. -/
def candidates (file path : System.FilePath) : List System.FilePath :=
  let dir := file.parent.getD "."
  [path, dir / path, (dir.parent.getD ".") / path]

/-- Locate a project-relative file, or fail with a clear message. -/
def findFile (path : String) : DocElabM System.FilePath := do
  let file : System.FilePath := (← getFileName)
  for c in candidates file path do
    if ← (c.pathExists : IO Bool) then return c
  throwError s!"cannot find {path} (tried {(candidates file path).map toString}); see verso/README.md"

/-! ## `{sourceFile}` -/

/-- Arguments of `{sourceFile ...}`. -/
structure SourceFileConfig where
  path : String
  start? : Option String
  stop? : Option String

instance : FromArgs SourceFileConfig DocElabM where
  fromArgs :=
    SourceFileConfig.mk <$> .positional `path .string
      <*> .named `from .string true <*> .named `to .string true

/-- The lines of `txt` from the first one containing `start?` to the first following one
containing `stop?` (both inclusive). -/
def excerpt (txt : String) (start? stop? : Option String) : Option String := Id.run do
  let mut lines := txt.splitOn "\n"
  if let some s := start? then
    lines := lines.dropWhile (fun l => !hasInfix l s)
    if lines.isEmpty then return none
  if let some e := stop? then
    let n := (lines.takeWhile (fun l => !hasInfix l e)).length
    if n == lines.length then return none
    lines := lines.take (n + 1)
  -- drop trailing blank lines
  return some ("\n".intercalate (lines.reverse.dropWhile (·.isEmpty)).reverse)

/-- `{sourceFile "PATH" (from := "…") (to := "…")}`: the file `PATH`, verbatim, as a code block. -/
@[block_command]
def sourceFile : BlockCommandOf SourceFileConfig
  | {path, start?, stop?} => do
    let f ← findFile path
    let txt ← (IO.FS.readFile f : IO String)
    let some shown := excerpt txt start? stop?
      | throwError s!"sourceFile: the markers {start?} / {stop?} were not found in {f}"
    ``(Verso.Doc.Block.code $(quote shown))

/-! ## `libcode` -/

/-- Arguments of the `libcode` code block: the library file the code is quoted from, followed by
the usual options of a `lean` code block. -/
structure LibCodeConfig where
  file : String
  leanConfig : InlineLean.LeanBlockConfig

instance : FromArgs LibCodeConfig DocElabM where
  fromArgs := LibCodeConfig.mk <$> .positional `file .string <*> FromArgs.fromArgs

/-- The lines of `s`, without trailing whitespace. -/
def normLines (s : String) : List String :=
  (s.splitOn "\n").map fun l => l.trimAsciiEnd.copy

/-- `true` iff the (nonblank) lines of `code` occur consecutively among the lines of `src`. -/
def isExcerpt (src code : String) : Bool :=
  let sl := normLines src
  let cl := ((normLines code).reverse.dropWhile (·.isEmpty)).reverse
  !cl.isEmpty && (List.range (sl.length + 1)).any fun i => (sl.drop i).take cl.length == cl

/-- A `lean` code block whose text must be a verbatim excerpt of a library file. -/
@[code_block]
def libcode : CodeBlockExpanderOf LibCodeConfig
  | {file, leanConfig}, str => do
    let f ← findFile file
    let src ← (IO.FS.readFile f : IO String)
    unless isExcerpt src str.getString do
      throwErrorAt str s!"libcode: this code is not a verbatim excerpt of {f}: the document has drifted from the library"
    InlineLean.lean leanConfig str

/-! ## `{moduleTable}` -/

/-- The module name of a source file relative to the root of `../formal`. -/
def moduleOf (rel : System.FilePath) : String :=
  ".".intercalate ((rel.withExtension "").components.filter (· != "."))

/-- Project-internal imports of a source text (`import`, `public import`, `import all`, …). -/
def projectImports (txt : String) (internal : List String) : List String :=
  (txt.splitOn "\n").filterMap fun l =>
    let ws := (l.splitOn " ").filter (· != "")
    if ws.contains "import" then
      match ws.getLast? with
      | some m => if internal.contains m then some m else none
      | none => none
    else none

/-- Number of top-level `theorem`/`lemma`/`def`/`abbrev`/`instance`/`structure` declarations of a
source text (after attributes and modifiers), a rough size measure. -/
def declCount (txt : String) : Nat :=
  let keywords := ["theorem", "lemma", "def", "abbrev", "instance", "structure", "inductive"]
  let modifiers := ["noncomputable", "private", "protected", "public", "meta", "partial", "unsafe"]
  let isDecl (l : String) : Bool :=
    if l.startsWith " " then false
    else
      let ws := (l.splitOn " ").filter (· != "")
      let ws := ws.dropWhile fun w => w.startsWith "@[" || w.endsWith "]" || modifiers.contains w
      match ws.head? with
      | some w => keywords.contains w
      | none => false
  ((txt.splitOn "\n").filter isDecl).length

/-- `{moduleTable}`: a table of the modules of `../formal`, computed from the sources. -/
@[block_command]
def moduleTable : BlockCommandOf Unit
  | () => do
    let root ← findFile "../formal/lakefile.toml"
    let base := root.parent.getD "."
    let sub ← (System.FilePath.readDir (base / "{{LEAN_NAME}}") : IO (Array IO.FS.DirEntry))
    let subFiles := (sub.filter (·.fileName.endsWith ".lean")).map (·.fileName) |>.qsort (· < ·)
    let files : List System.FilePath :=
      ["{{LEAN_NAME}}.lean"].map (System.FilePath.mk) ++
      subFiles.toList.map (fun (f : String) => ("{{LEAN_NAME}}" : System.FilePath) / System.FilePath.mk f) ++
      ["Challenge.lean", "Solution.lean", "AxiomAudit.lean", "Audit.lean"].map System.FilePath.mk
    let mods := files.map moduleOf
    let mut rows : Array String := #[]
    let pad (s : String) (n : Nat) : String := s ++ "".pushn ' ' (n - s.length)
    let lpad (s : String) (n : Nat) : String := "".pushn ' ' (n - s.length) ++ s
    rows := rows.push s!"{pad "module" 24} {lpad "lines" 6} {lpad "decls" 6}   imports (inside the project)"
    for (f, m) in files.zip mods do
      let txt ← (IO.FS.readFile (base / f) : IO String)
      -- the number of lines, as `wc -l` counts them
      let n := (txt.splitOn "\n").length - (if txt.endsWith "\n" then 1 else 0)
      let imps := projectImports txt mods
      let subs := mods.filter (·.startsWith "{{LEAN_NAME}}.")
      let short (m : String) : String := m.replace "{{LEAN_NAME}}." ""
      let shown :=
        if imps.isEmpty then "Mathlib / Lean only"
        else if subs.all imps.contains then
          ", ".intercalate (s!"all {subs.length} {{LEAN_NAME}}.* modules" ::
            imps.filter (fun i => !subs.contains i && i != "{{LEAN_NAME}}"))
        else ", ".intercalate (imps.map fun i => if i.startsWith "{{LEAN_NAME}}." then short i else i)
      rows := rows.push s!"{pad m 24} {lpad (toString n) 6} {lpad (toString (declCount txt)) 6}   {shown}"
    ``(Verso.Doc.Block.code $(quote ("\n".intercalate rows.toList)))

end DocMeta
