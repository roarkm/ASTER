This is an attempt to "pipeline" corenlp parses; i.e. pass a list of files to parse to corenlp
server so that it loads the annotator pipeline only once.

**Setup**

1) Split the 42,305 line raw text file into 42,305 one line files with
`mkdir split && cd split`.

`split -d -l 1 path-to/plot-summaries-raw.txt line`.

2) In the dir above that, make a list of those files with
`find "$(pwd)/split" -type f > filelist.txt`

3) Split the full file list into smaller lists in order to batch the computations
into 8 hour jobs; from testing, each parse takes ~8 seconds so (8*60*60 / 8 = 3600).
`split -d -l 3600 filelist.txt filelist-split`

4) Now our script will parse 3600 lines at a time (manually edit the script to use filename and dir)
