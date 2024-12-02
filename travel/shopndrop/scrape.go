package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"regexp"
)

var fname = flag.String("f", "homepage.html", "Filename")

var (
	rxCategories = regexp.MustCompile(`(?ms)<ul id="categories" (.*)</ul>`)
	rxAHref      = regexp.MustCompile(`(?ms)<a href="([^"]+)" class="subcat">([^<]+)<`)
)

// Page contains information about one page to download
type Page struct {
	PageName string
	Name     string
	Link     string
}

func doFile(fname string) ([]Page, error) {
	file, err := os.Open(fname)
	if err != nil {
		return nil, err
	}
	scanner := &Line{
		scanner: bufio.NewScanner(file),
	}

	ps := []Page{}
	for {
		grabbed, n := scanner.scanTill(rxCategories)
		if n == -1 {
			break
		}
		name, link := splitRx2(rxAHref, grabbed)
		ps = append(ps, Page{
			Name: name,
			Link: link,
		})
	}

	if err := scanner.Err(); err != nil {
		return ps, err
	}
	return ps, nil
}

// Line holds the current line and a scanner
type Line struct {
	scanner *bufio.Scanner
	line    string
}

func (l *Line) Next() bool {
	ret := l.scanner.Scan()
	l.line = ""
	if ret {
		l.line = l.scanner.Text()
	}
	return ret
}

func (l *Line) Err() error {
	return l.scanner.Err()
}

func (l *Line) match(rx *regexp.Regexp) bool {
	return rx.MatchString(l.line)
}

// scanTill scans until any of the regular expressions match
// returns the one's base index for which expression patched
func (l *Line) scanTill(rxs ...*regexp.Regexp) (string, int) {
	for l.Next() {
		for i, rx := range rxs {
			if l.match(rx) {
				return l.findOrEmpty(rx), i + 1
			}
		}
	}
	return "", -1
}

func splitRx2(rx *regexp.Regexp, txt string) (string, string) {
	grab := rx.FindAllStringSubmatch(txt, 1)
	if len(grab) > 0 {
		return grab[0][1], grab[0][2]
	}
	return "", ""
}

func (l *Line) findOrEmpty(rx *regexp.Regexp) string {
	grab := rx.FindAllStringSubmatch(l.line, 1)
	if len(grab) > 0 {
		return grab[0][1]
	}
	return ""
}

func main() {
	flag.Parse()
	fmt.Printf("Parsing %s\n", *fname)
	entries, err := doFile(*fname)
	if err != nil {
		fmt.Printf("Error parsing file %q: %v\n", *fname, err)
		return
	}
	fmt.Printf("Entries %d:\n", len(entries))
	for _, entry := range entries {
		fmt.Printf("%s: %s\n", entry.Link, entry.Name)
	}
}
