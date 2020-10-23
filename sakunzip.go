// Make unzip, tar, etc smarter by not creating folder
package main

import (
	"flag"
	"fmt"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
)

func main() {
	flag.Parse()

	if len(flag.Args()) == 0 {
		fmt.Printf("Need to pass in a filename")
		return
	}
	err := smartUnzip(flag.Args()[0])
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	}
}

func smartUnzip(fname string) error {
	needsSubfolder, err := needsSubfolder(fname)
	if err != nil {
		return err
	}

	folder := getExportFolder(fname, needsSubfolder)

	fmt.Printf("Smart exporting to folder %q\n", folder)
	return handleUnzip(fname, folder)
}

func getExportFolder(fname string, needsSubfolder bool) string {
	dir, name := filepath.Split(fname)
	if needsSubfolder {
		ext := filepath.Ext(name)
		return filepath.Join(dir, name[:len(name)-len(ext)]) + "/"
	}
	return dir
}

func handleUnzip(fname, toFolder string) error {
	out, err := exec.Command("unzip", "-d", toFolder, fname).CombinedOutput()
	if err != nil {
		return err
	}
	fmt.Println(string(out))
	return nil
}

func needsSubfolder(fname string) (bool, error) {
	if !strings.HasSuffix(fname, ".zip") {
		return false, fmt.Errorf("Only support zip files currently")
	}
	rows, err := listUnzip(fname)
	if err != nil {
		fmt.Printf("Problem calling unzip -l: %v", err)
		return false, err
	}
	for _, row := range rows {
		if !strings.Contains(row, "/") {
			return true, nil
		}
	}
	return false, nil
}

var fileRowRx = regexp.MustCompile(`\s*\d+\s+[\d-]+\s[\d:]+\s+(.*)`)

// listUnzip lists the zip file, skipping any folder only entries
func listUnzip(fname string) ([]string, error) {
	out, err := exec.Command("unzip", "-l", fname).CombinedOutput()
	if err != nil {
		return nil, err
	}
	lines := strings.Split(string(out), "\n")

	results := make([]string, 0, len(lines))
	for _, line := range lines {
		parts := fileRowRx.FindStringSubmatch(line)
		if len(parts) > 0 {
			name := parts[1]
			if strings.HasSuffix(name, "/") {
				continue
			}
			results = append(results, name)
		}
	}
	return results, nil
}
