// r is the universal resolver.
// Tries to force a string into what you want.
// You can force it into:
// -d directory
//    all or lowest common denominator(s)
// -f filename
//    all or without suffix
// -t target
//    test, run, or build
package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"

	"github.com/scottkirkwood/scott-bin/resolve/resolve"
)

// The following command will work even for BUILD files that haven't been submitted.
// (found in _get_build_targets from the bash shell)
// 	<rule_re> can be:
// 		(test) rule_re=".*_test"
// 		(build) rule_re=".*"
// 		(run) rule_re=".*_test|.*_binary"
// 		(mpm) rule_re="genmpm"
// blaze query "kind(\"<rule_re>\", production/incident_management/requiem:all)"

// Types of paths we should be able to resolve:
// ./ ...
// //depot/...
// /google/src/files/
// Maybe:
// /blaze-bin/
// /blaze-genfile/
// /google/src/files/head/depot/google3/googleclient/chrome/webapk/testing/chrome-webapk-test/src/site.go
// or
// blaze query 'tests("java/com/google/communication/wolverine/admin/pbx/autoattendant/service:all")'

var (
	toFilename = flag.Bool("f", false, "Resolve to filenames without path.")
	noExt      = flag.Bool("x", false, "Remove extension.")
	toDir      = flag.Bool("d", false, "Directories.")
	only       = flag.Bool("o", false, "Show only matching lines.")
	upDir      = flag.Bool("u", false, "Up one directory level.")
	upUpDir    = flag.Bool("uu", false, "Up two directory levels.")
	unique     = flag.Bool("unique", true, "Uniquify results (default true).")
	verifyPath = flag.Bool("verify-path", false, "Put ? before filenames we can't find.")
	g3         = flag.Bool("g3", false, "google3 relative folder.")
)

func main() {
	flag.Parse()
	wd, err := os.Getwd()
	if err != nil {
		fmt.Fprintln(os.Stderr, "Unable to get current working directory")
	}

	up := 0
	if *upDir {
		up--
	}
	if *upUpDir {
		up -= 2
	}
	r := resolve.R{
		ToBaseName: *toFilename,
		NoExt:      *noExt,
		Only:       *only,
		ToDir:      *toDir,
		G3:         *g3,
		Unique:     *unique,
		VerifyPath: *verifyPath,
		StartPath:  wd,
		UpDirCount: up,
	}

	if len(flag.Args()) > 0 {
		for _, arg := range flag.Args() {
			r.Resolve(arg)
		}
	} else {
		scanner := bufio.NewScanner(os.Stdin)
		for scanner.Scan() {
			r.Resolve(scanner.Text())
		}
		if err := scanner.Err(); err != nil {
			fmt.Fprintln(os.Stderr, "reading standard input:", err)
		}
	}
	fmt.Println(r.String())
}
