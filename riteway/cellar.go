package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"regexp"
)

var (
	fname = flag.String("f", "cellar.txt", "Filename")
)

var (
	rxCodeBrand = regexp.MustCompile(`^\t(\d+) (.+) $`)
	rxDesc      = regexp.MustCompile(`^\t(.+) $`)
	rxUnit      = regexp.MustCompile(`^\t(\d+) $`)
	rxSize      = regexp.MustCompile(`^\t(\d+)([A-Z]+) $`)
	rxPrice     = regexp.MustCompile(`^\t[$]([0-9.]+)\s*$`)
)

// Product contains all the parts of a product
type Product struct {
	Code        string
	Brand       string
	Description string
	Unit        string
	Size        string
	SizeUnits   string
	BottlePrice string
	CasePrice   string
}

type Line struct {
	scanner *bufio.Scanner
	line    string
}

func (p Product) String() string {
	return fmt.Sprintf("%s,%q,%q,%s,%s,%s,%s,%s",
		p.Code, p.Brand, p.Description, p.Unit, p.Size, p.SizeUnits, p.BottlePrice, p.CasePrice)
}

func doFile(fname string) ([]Product, error) {
	file, err := os.Open(fname)
	if err != nil {
		return nil, err
	}
	scanner := &Line{
		scanner: bufio.NewScanner(file),
	}

	ps := []Product{}
	for {
		code, brand := scanner.scanTill2(rxCodeBrand)
		if code == "" {
			break
		}
		description := scanner.scanTill(rxDesc)
		unit := scanner.scanTill(rxUnit)
		size, units := scanner.scanTill2(rxSize)
		if size == "120" && units == "Z" {
			// hah, they typed "0Z"
			size = "12"
			units = "OZ"
		}
		bottlePrice := scanner.scanTill(rxPrice)
		casePrice := scanner.scanTill(rxPrice)
		ps = append(ps, Product{
			Code:        code,
			Brand:       brand,
			Description: description,
			Unit:        unit,
			Size:        size,
			SizeUnits:   units,
			BottlePrice: bottlePrice,
			CasePrice:   casePrice,
		})
	}

	if err := scanner.Err(); err != nil {
		return ps, err
	}
	return ps, nil
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

func (l *Line) scanTill(rx *regexp.Regexp) string {
	for l.Next() {
		if l.match(rx) {
			return l.findOrEmpty(rx)
		}
	}
	return ""
}

func (l *Line) scanTill2(rx *regexp.Regexp) (string, string) {
	for l.Next() {
		if l.match(rx) {
			return l.findOrEmpty2(rx)
		}
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

func (l *Line) findOrEmpty2(rx *regexp.Regexp) (string, string) {
	grab := rx.FindAllStringSubmatch(l.line, 1)
	if len(grab) > 0 {
		return grab[0][1], grab[0][2]
	}
	return "", ""
}

func main() {
	flag.Parse()
	products, err := doFile(*fname)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}
	for _, product := range products {
		fmt.Println(product)
	}
}
