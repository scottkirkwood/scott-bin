package resolve

import (
	"os"
	"path"
	"regexp"
	"strings"
)

var g3rx = regexp.MustCompile(`\b(?:google3|blaze-bin|lblaze-gen)/([^# :]+)`)

// R is the resolve info
type R struct {
	ToBaseName bool
	NoExt      bool
	Only       bool // only valid paths shown
	ToDir      bool
	G3         bool
	Unique     bool
	VerifyPath bool
	StartPath  string // unused, currently
	UpDirCount int

	results []string
}

// Resolve handles one line from stdin or an argument on the command line.
func (r *R) Resolve(line string) {
	r.results = append(r.results, r.filenames(r.split(line))...)
}

func allPaths(paths []string) bool {
	for _, path := range paths {
		if !isPath(path) {
			return false
		}
	}
	return true
}

func isPath(path string) bool {
	if strings.ContainsAny(path, " =(){};:") {
		// Don't funny characters in paths, limitation in how we are splitting here.
		return false
	}
	return true
}

// Report outputs the resolved values.
func (r *R) String() string {
	if r.Unique {
		uniq := make(map[string]bool, len(r.results))
		newResults := make([]string, 0, len(r.results))
		for _, result := range r.results {
			if !uniq[result] {
				uniq[result] = true
				newResults = append(newResults, result)
			}
		}
		r.results = newResults
	}
	return strings.Join(r.results, "\n")
}

func (r *R) split(line string) []string {
	paths := strings.Split(line, "\n")
	if len(paths) > 1 && allPaths(paths) {
		return paths
	}
	paths = strings.Split(line, ":")
	if len(paths) > 1 && allPaths(paths) {
		return paths
	}
	paths = strings.Split(line, " ")
	if len(paths) > 1 && allPaths(paths) {
		return paths
	}
	return []string{line}
}

func (r *R) filenames(fnames []string) []string {
	ret := make([]string, 0, len(fnames))
	for _, fname := range fnames {
		fname = r.filename(strings.TrimSpace(fname))
		if fname != "" {
			ret = append(ret, fname)
		}
	}
	return ret
}

func (r *R) upDir(dir string, isDir bool) string {
	if r.UpDirCount == 0 {
		return dir
	}
	fname := ""
	if !isDir {
		dir, fname = path.Split(dir)
	}
	parts := strings.Split(dir, string(os.PathSeparator))
	updir := -r.UpDirCount + 1
	if len(parts) >= updir {
		return path.Join(strings.Join(parts[0:len(parts)-updir], string(os.PathSeparator)), fname)
	}
	return path.Join(dir, fname)
}

func (r *R) filename(fname string) string {
	if r.G3 {
		grps := g3rx.FindStringSubmatch(fname)
		if len(grps) > 1 {
			fname = grps[1]
		}
	}
	if r.VerifyPath && !pathExists(fname) {
		fname = "?" + fname
	}
	if r.ToDir {
		return r.upDir(path.Dir(fname), true)
	}
	if r.ToBaseName {
		fname = path.Base(fname)
	}
	if r.NoExt {
		ext := path.Ext(fname)
		fname = fname[:len(fname)-len(ext)]
	}
	fname = r.upDir(fname, false)
	if r.Only && !pathExists(fname) {
		return "ONLY"
	}
	return fname
}

func pathExists(fname string) bool {
	// TODO(scottkirkwood): Try harder to find path
	if _, err := os.Stat(fname); os.IsNotExist(err) {
		return false
	}
	return true
}
