package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"regexp"
	"strings"
)

var (
	fname = flag.String("f", "cellar.txt", "Filename")
)

var (
	rxCodeBrand = regexp.MustCompile(`^\t(\d+ .+)\s+$`)
	rxDesc      = regexp.MustCompile(`^\t(.+) $`)
	rxUnit      = regexp.MustCompile(`^\t(\d+) $`)
	rxSize      = regexp.MustCompile(`^\t(\d+[A-Z]+) $`)
	rxPrice     = regexp.MustCompile(`^\t[$]([0-9.]+)\s*$`)
	rxNumVal    = regexp.MustCompile(`(\d+)\s*(.*)`)
	rxSection   = regexp.MustCompile(`^\s*(` + strings.Join([]string{
		"BEERS",
		"HARD CIDER",
		"CIGARETTES",
		"MISCELLANEOUS: .*",
		"MIXERS",
		"JUICE",
		"SOFT DRINKS",
		"ENERGY DRINKS",
		"SPIRITS - .*",
		"WATER",
		"BAG IN BOX WINES",
		"SAKE",
		".* - White",
		".* - Red",
		".* - Rose",
	}, "|") + `)$`)
	rxLink = regexp.MustCompile(`corders@caribbeancellars.com`)
)

// Product contains all the parts of a product
type Product struct {
	Section     string
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
	return fmt.Sprintf("%q,%s,%q,%q,%s,%s,%s,%s,%s",
		p.Section, p.Code, p.Brand, p.Description, p.Unit, p.Size, p.SizeUnits, p.BottlePrice, p.CasePrice)
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
	section := "Beer"
	for {
		grabbed, n := scanner.scanTill(rxCodeBrand, rxSection)
		if n == -1 {
			break
		}
		if n == 2 {
			section = grabbed
			continue
		}
		code, brand := splitRx2(rxNumVal, grabbed)
		description, _ := scanner.scanTill(rxDesc)
		unit, _ := scanner.scanTill(rxUnit)
		sizeUnits, _ := scanner.scanTill(rxSize)
		size, units := splitRx2(rxNumVal, sizeUnits)
		if size == "120" && units == "Z" {
			// hah, they typed "0Z"
			size = "12"
			units = "OZ"
		}
		bottlePrice, _ := scanner.scanTill(rxPrice)
		casePrice, _ := scanner.scanTill(rxPrice)
		ps = append(ps, Product{
			Section:     section,
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
	products, err := doFile(*fname)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}
	for _, product := range products {
		fmt.Println(product)
	}
}
