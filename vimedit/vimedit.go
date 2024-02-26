// Package vimedit edits a file with vim
// Has support for removing comments
// Knows to check exit code for 0, otherwise leave as is
package vimedit

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"regexp"
	"strings"
)

// Txt is sn object that manages the tmp file
type Txt struct {
	LeaveTempFile bool // Don't delete on Close
	LeaveComments bool // Don't remove comments

	rxComment    *regexp.Regexp // Compiled CommentRx
	tempFilename string         // name of tmp file
	prevText     []string       // old text split into lines

	exitCode int
	errText  string
}

// EditText edits the txt passed and returns an object with updated text
// If `txt` had comments, it defaults to removing comments, otherwise comments ignored
func EditText(txt string, vimCommands ...string) (*Txt, error) {
	f, err := os.CreateTemp("", "vimedit")
	if err != nil {
		return nil, err
	}
	t := &Txt{
		tempFilename: f.Name(),
		prevText:     strings.Split(txt, "\n"),
	}
	if err := t.CompileRx("^#"); err != nil {
		return t, err
	}
	if !t.HadComments() {
		t.LeaveComments = true
	}
	if _, err := f.Write([]byte(txt)); err != nil {
		return t, err
	}
	if err := f.Close(); err != nil {
		return t, err
	}

	editor := "vim"
	if os.Getenv("EDITOR") != "" {
		editor = os.Getenv("EDITOR")
	}
	vimPath, err := exec.LookPath(editor)
	if err != nil {
		return t, err
	}
	cmds := []string{}
	for _, cmd := range vimCommands {
		cmds = append(cmds, "-c", cmd)
	}
	cmds = append(cmds, f.Name())
	cmd := exec.Command(vimPath, cmds...)

	cmd.Stdout = os.Stdout
	cmd.Stdin = os.Stdin
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		if exitError, ok := err.(*exec.ExitError); ok {
			t.exitCode = exitError.ExitCode()
			t.errText = exitError.Error()
		} else {
			return t, err
		}
	}
	return t, nil
}

// CompileRx will compile and set your comment regular expression
func (t *Txt) CompileRx(rx string) (err error) {
	t.rxComment, err = regexp.Compile(rx)
	return err
}

// Close will delete the temporary file, unless LeaveTempFile is set
func (t *Txt) Close() {
	if t.LeaveTempFile {
		return
	}
	os.Remove(t.TempFilename())
	t.tempFilename = ""
}

// Abort returns true exit code was not 0
func (t *Txt) Abort() bool {
	return t.ExitCode() != 0
}

// ExitCode returns the exit code
func (t *Txt) ExitCode() int {
	return t.exitCode
}

// Error returns stderr text if any
func (t *Txt) Error() string {
	return t.errText
}

// TempFilename returns the temporary filename
func (t *Txt) TempFilename() string {
	return t.tempFilename
}

// GetText returns the text or empty
func (t *Txt) GetText() string {
	lines, err := t.GetLines()
	if err != nil {
		fmt.Fprintf(os.Stderr, "ERR: %v\n", err)
	}
	return strings.Join(lines, "\n")
}

// GetLines returns the lines of text with any comments removed
func (t *Txt) GetLines() (lines []string, err error) {
	if t.Abort() {
		lines = t.prevText
	} else {
		f, err := os.Open(t.TempFilename())
		if err != nil {
			return lines, err
		}
		defer f.Close()

		scanner := bufio.NewScanner(f)
		for scanner.Scan() {
			lines = append(lines, scanner.Text())
		}
		err = scanner.Err()
	}
	return t.removeComments(lines), err
}

// HadComments looks at the original txt and sees if it had any comments
func (t *Txt) HadComments() bool {
	for _, line := range t.prevText {
		if t.rxComment.MatchString(line) {
			return true
		}
	}
	return false
}

// removeComments will remove the comments unless LeaveComments is set
func (t *Txt) removeComments(lines []string) []string {
	if t.LeaveComments {
		return lines
	}
	newLines := make([]string, 0, len(lines))
	for _, line := range lines {
		if !t.rxComment.MatchString(line) {
			newLines = append(newLines, line)
		}
	}
	return newLines
}
