import VersoManual
import Doc
import Doc.Render

open Verso.Genre Manual

-- Renders the document. `lake exe generate-doc --output _out --with-html-single` writes
-- `_out/html-multi/` and `_out/html-single/index.html`. The configuration is in `Doc/Render.lean`.
def main := manualMain (%doc Doc) (config := config)
