# Changelog

## 0.1.0

The first release: the fifteen rendering modules Solander and Slate carried as copies, moved here unchanged from Solander's at the commit both apps had reached, with the tests that need no vault.

A bare install needs nothing past the standard library. Parsing Markdown and reading YAML take the `render` extra, so an app that only uses the palettes or the list diffs installs no Markdown parser. The README lists every `READER_MAX_*` limit with its default.
