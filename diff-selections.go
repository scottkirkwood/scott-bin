// Compare dpkg --selections between two machines
// Packages with common prefixes are grouped and summarized. If you want to see them, call with -expand <prefix>
package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"sort"
	"strings"
)

var (
	oldFile = flag.String("old", "", "Path to the old selections file (from dpkg --get-selections)")
	newFile = flag.String("new", "", "Path to the current selections file (optional, defaults to running dpkg --get-selections)")
	expand  = flag.String("expand", "", "Comma-separated list of prefixes to expand (e.g. 'lib,gcc')")
)

func main() {
	flag.Parse()
	if *oldFile == "" {
		fmt.Println("Usage: diff-selections -old <old-selections.txt> [-new <current-selections.txt>] [-expand <prefix1,prefix2>]")
		os.Exit(1)
	}

	oldSelections, err := readSelectionsFile(*oldFile)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading old selections: %v\n", err)
		os.Exit(1)
	}

	var currentSelections map[string]string
	if *newFile != "" {
		currentSelections, err = readSelectionsFile(*newFile)
	} else {
		currentSelections, err = getCurrentSelections()
	}
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error getting current selections: %v\n", err)
		os.Exit(1)
	}

	missing := findMissing(oldSelections, currentSelections)

	if len(missing) == 0 {
		fmt.Println("No missing packages found.")
		return
	}

	expandPrefixes := make(map[string]bool)
	if *expand != "" {
		for _, p := range strings.Split(*expand, ",") {
			expandPrefixes[strings.TrimSpace(p)] = true
		}
	}

	groups := make(map[string][]string)
	for _, pkg := range missing {
		p := getPrefix(pkg)
		groups[p] = append(groups[p], pkg)
	}

	var prefixes []string
	for p := range groups {
		prefixes = append(prefixes, p)
	}
	sort.Strings(prefixes)

	if len(expandPrefixes) == 0 {
		fmt.Println("Missing packages found:")
	}

	for _, p := range prefixes {
		pkgs := groups[p]
		sort.Strings(pkgs)

		if len(expandPrefixes) > 0 {
			if expandPrefixes[p] {
				for _, pkg := range pkgs {
					fmt.Printf("%s\n", pkg)
				}
			}
		} else {
			if len(pkgs) > 1 {
				fmt.Printf("%s* (%d packages)\n", p, len(pkgs))
			} else {
				fmt.Printf("%s\n", pkgs[0])
			}
		}
	}
}

// getPrefix returns the prefix for a package name.
func getPrefix(pkg string) string {
	if strings.HasPrefix(pkg, "lib") {
		return "lib"
	}
	if i := strings.Index(pkg, "-"); i != -1 {
		return pkg[:i]
	}
	return pkg
}

// readSelectionsFile reads the output of dpkg --get-selections from a file.
func readSelectionsFile(path string) (map[string]string, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	return parseSelections(f)
}

// getCurrentSelections runs dpkg --get-selections and returns the result.
func getCurrentSelections() (map[string]string, error) {
	cmd := exec.Command("dpkg", "--get-selections")
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, err
	}
	if err := cmd.Start(); err != nil {
		return nil, err
	}
	selections, err := parseSelections(stdout)
	if err != nil {
		return nil, err
	}
	if err := cmd.Wait(); err != nil {
		return nil, err
	}
	return selections, nil
}

// parseSelections parses the tab-separated output of dpkg --get-selections.
func parseSelections(r io.Reader) (map[string]string, error) {
	selections := make(map[string]string)
	scanner := bufio.NewScanner(r)
	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.Fields(line)
		if len(parts) >= 2 {
			pkg := parts[0]
			status := parts[1]
			selections[pkg] = status
		}
	}
	return selections, scanner.Err()
}

// findMissing returns packages that are 'install' in old but not 'install' in current.
func findMissing(old, current map[string]string) []string {
	var missing []string
	for pkg, status := range old {
		if status != "install" {
			continue
		}
		if currentStatus, ok := current[pkg]; !ok || currentStatus != "install" {
			if shouldIgnore(pkg) {
				continue
			}
			missing = append(missing, pkg)
		}
	}
	return missing
}

// shouldIgnore filters out packages that are likely specific to a kernel version,
// library versions, or other machine-specific noise.
func shouldIgnore(pkg string) bool {
	// Exact matches to ignore
	ignoreExact := map[string]bool{
		"dpkg": true,
	}
	if ignoreExact[pkg] {
		return true
	}

	// Prefix matches to ignore
	prefixes := []string{
		"linux-image-",
		"linux-headers-",
		"linux-modules-",
		"linux-tools-",
		"libcrypt1", // often varies
	}
	for _, p := range prefixes {
		if strings.HasPrefix(pkg, p) {
			return true
		}
	}

	// You might also want to ignore packages that have version numbers in their name
	// if they are likely to be dependencies of other things.
	return false
}
