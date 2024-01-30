package main

import (
	"flag"
	"fmt"
	"html"
	"io/ioutil"
	"path/filepath"
	"regexp"
	"strings"
)

var (
	fname = flag.String("f", "beer.html", "Filename")
)

var (
	rxLiProduct   = regexp.MustCompile(`(?ms)<li class=[^>]*js-product-item[^>]+>(.*?)</li>`)
	rxSku         = regexp.MustCompile(`class="product__sku">([^<]+)</span>`)
	rxPrice       = regexp.MustCompile(`data-price-amount="([0-9.]+)"`)
	rxProductName = regexp.MustCompile(`(?ms)product-item-name">[^>]*>\s*(.*?)\s*</a>`)
	rxWhiteSpace  = regexp.MustCompile(`\s+`)
	rxProductLink = regexp.MustCompile(`(?ms)"product-item-link".*?https://www.riteway.vg/([^"]+).html"`)
	rxPackSize    = regexp.MustCompile(`(?ms)pack-size__container">(.*?)</div>`)
	rxProductId   = regexp.MustCompile(`"product-id-(\d+)"`)
)

// Product contains all the parts of a product
type Product struct {
	PageName string
	Sku      string
	Id       string
	Name     string
	PackSize string
	Price    string
	Link     string
}

type Line string

func parseProduct(line Line) Product {
	return Product{
		Sku:      line.findOrEmpty(rxSku),
		Id:       line.findOrEmpty(rxProductId),
		Name:     cleanWhitespace(line.findOrEmpty(rxProductName)),
		PackSize: cleanWhitespace(line.findOrEmpty(rxPackSize)),
		Price:    line.findOrEmpty(rxPrice),
		Link:     line.findOrEmpty(rxProductLink),
	}
}

func (p Product) String() string {
	return fmt.Sprintf("%s,%q,%q,%q,%q,%q,%q",
		p.PageName, p.PackSize, p.Sku, p.Id, p.Price, p.HtmlLink(), html.UnescapeString(p.Name))
}

func (p Product) HtmlLink() string {
	return "https://www.riteway.vg/" + p.Link + ".html"
}

func cleanWhitespace(txt string) string {
	return rxWhiteSpace.ReplaceAllString(strings.TrimSpace(txt), " ")
}

func (l Line) findOrEmpty(rx *regexp.Regexp) string {
	grab := rx.FindAllStringSubmatch(string(l), 1)
	if len(grab) > 0 {
		return grab[0][1]
	}
	return ""
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
	return parsePage(strings.ReplaceAll(fname, ".html", ""), txt)
}

func main() {
	flag.Parse()
	files, err := filepath.Glob(`*.html`)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	for _, fname := range files {
		err := doFile(fname)
		if err != nil {
			fmt.Printf("Err: %v\n", err)
			return
		}
	}
}
