package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"path/filepath"
	"regexp"
	"strings"
)

var (
	fname = flag.String("f", "cellar.txt", "Filename")
)

var (
	rxCodeBrand = regexp.MustCompile(`^\t(\d+) (.+) $`)
	rxDesc      = regexp.MustCompile(`^\t(.+) $`)
	rxUnit      = regexp.MustCompile(`^\t(\d+) $`)
	rxSize      = regexp.MustCompile(`^\t(\d+)([A-Z]+) $`)
	rxBottle    = regexp.MustCompile(`^\t$([0-9.]+) $`)
	rxCase      = regexp.MustCompile(`^\t$([0-9.]+) $`)
)

// Product contains all the parts of a product
type Product struct {
	Code   string
	Name   string
	Unit   string
	Size   string
	Bottle string
	Case   string
}

type Line string

func (p Product) String() string {
	return fmt.Sprintf("%s,%s,%s,%q,%q,%s,%q",
		p.Code, p.Name, p.Unit, p.Size, p.Bottle, p.Case)
}

func parsePage(name, txt string) error {
	for _, product := range rxLiProduct.FindAllStringSubmatch(txt, -1) {
		p := parseProduct(Line(product[1]))
		p.PageName = name
		fmt.Println(p.String())
	}
	return nil
}

func doFile(fname string) error {
	body, err := ioutil.ReadFile(fname)
	if err != nil {
		return err
	}
	txt := string(body)
	return parsePage(txt)
}

func main() {
	flag.Parse()
	err := doFile(*fname)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}
}
