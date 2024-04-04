# CST-301-project part 3
# Written by Spencer Meren

## Execution

	python3 Main.py [file-path]

`[file-path]` specifies the path of the .java file to parse. Sample programs are located in `assets/` by default.

## Sample Program List

- `assets/AssignmentSample.java`
- `assets/AutosaveManager.java`
- `assets/BindingsHelper.java`
- `assets/ClipBoardManager.java`
- `assets/CrossRef.java`
- `assets/DefaultLatexParser.java`
- `assets/DefaultTexParserTest.java`
- `assets/ExternalFilesEntryLinker.java`
- `assets/FieldFactory.java`
- `assets/JabRefFrame.java`
	- Warning: Large file size results in exceptionally long parsing time. Prone to crashing the program.
- `PreviewViewer.java`
	- Does not parse properly due to triple quote, multi-lined strings. `PreviewViewer(Redacted).java` replaces triple-quoted strings with short dummy strings.
- `PreviewViewer(redacted).java`

# Additional attribution

`Classifier.py` was build off example GPT4Free code provided by Dylan Johnson.

GPT4Free Repository: https://github.com/xtekky/gpt4free