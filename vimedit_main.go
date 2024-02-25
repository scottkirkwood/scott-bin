package main

import (
	"flag"
	"fmt"
	"strings"

	"github.com/scottkirkwood/scott-bin/vimedit"
)

var (
	txtFlag       = flag.String("txt", "# Comments are stripped\nOriginal line\n\n", "Text to edit")
	aaIDFlag      = flag.String("aa_id", "", "Auto Attendant ID")
	leaveTemp     = flag.Bool("leave", false, "Leave temp file behind")
	leaveComments = flag.Bool("comments", false, "Leave comment lines behind")
	cmds          = flag.String("cmds", "$", "Vim commands (comma sep) to pass (ex. $ goes to end of file)")
)

func main() {
	flag.Parse()

	t, err := vimedit.EditText(*txtFlag, strings.Split(*cmds, ",")...)
	defer t.Close()

	t.LeaveTempFile = *leaveTemp
	if *leaveComments {
		t.LeaveComments = true
	}

	if err != nil {
		fmt.Printf("Err: %v\n", err)
	}
	if t.Abort() {
		fmt.Printf("ExitCode: %d, Stderr: %s\n", t.ExitCode(), t.Error())
	} else {
		fmt.Printf("Updated:\n%s\n", t.GetText())
	}
	if t.LeaveTempFile {
		fmt.Printf("Left temp file %s\n", t.TempFilename())
	}
}
